#!/usr/bin/env python3
"""
Unified ZMS reindexer:
- Pure REST-based reindexer (no Zope dependencies)
- Zope external method: manage_reindex_content_bg(self)
- CLI runner: python reindex.py BASE_URL [--connector ...]
"""

import argparse
import ast
import json
import logging
import os
import tempfile
import fcntl
import threading
import requests

LOGGER = logging.getLogger("ZMSReindex")
logging.basicConfig(level=logging.INFO)

# ======================================================================
# 1) PURE REST REINDEXER (Zope-free)
# ======================================================================

class ZMSIndexSchematizedReindexer:
    """
    Pure REST-based reindexer.
    Works standalone or inside Zope.
    """

    def __init__(self, base_url, connector, page_size=100, fileparsing=False):
        self.base_url = base_url.rstrip("/")
        self.connector = connector.strip("/")
        self.page_size = page_size
        self.fileparsing = 1 if fileparsing else 0

    # ------------------------------------------------------------------
    # REST helpers
    # ------------------------------------------------------------------

    def _api(self, path, **params):
        url = f"{self.base_url}/{path.lstrip('/')}"
        response = requests.get(url, params=params, timeout=60)
        response.raise_for_status()

        try:
            return response.json(), url
        except Exception:
            text = (response.text or "").strip()
            try:
                return json.loads(text), url
            except Exception:
                try:
                    return ast.literal_eval(text), url
                except Exception:
                    raise ValueError(f"Invalid REST payload: {text[:240]}")

    # ------------------------------------------------------------------
    # REST tree traversal
    # ------------------------------------------------------------------

    def _iter_index_uids(self):
        def fetch_children(path):
            rest_path = path.strip("/")
            url = f"{self.base_url}/++rest_api/{rest_path}/list_child_nodes"
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            return response.json()

        stack = [""]
        seen = set()

        while stack:
            path = stack.pop()

            try:
                nodes = fetch_children(path)
            except Exception as e:
                LOGGER.error(f"REST error fetching children for {path}: {e}")
                continue

            for node in nodes:
                uid = node.get("uid")
                meta_id = node.get("meta_id")
                node_path = node.get("getPath")

                if not uid or uid in seen:
                    continue
                seen.add(uid)

                # Nur ZMS-Knoten reindexen
                if meta_id == "ZMS":
                    yield uid, meta_id, node_path

                    # Nur bei ZMS weiter in die Tiefe gehen
                    if node_path:
                        stack.append(node_path.lstrip("/"))

    # ------------------------------------------------------------------
    # Main reindex loop
    # ------------------------------------------------------------------

    def run(self, write_line=print):
        stats = {
            "candidates": 0,
            "requests": 0,
            "objects": 0,
            "success": 0,
            "failed": 0,
            "skipped": 0,
        }

        for uid, meta_id, node_path in self._iter_index_uids():
            stats["candidates"] += 1
            write_line(f"Reindexing UID={uid} meta_id={meta_id} path={node_path}")

            params = {
                "uid": uid,
                "page_size:int": self.page_size,
                "clients:int": 0,
                "fileparsing:int": self.fileparsing,
            }

            try:
                payload, url = self._api(f"{self.connector}/reindex_page", **params)
                stats["requests"] += 1
            except Exception as e:
                stats["failed"] += 1
                write_line(f"ERROR calling REST API for uid={uid}: {e}")
                continue

            logs = payload.get("log", [])
            for entry in logs:
                objects = entry.get("objects", {})
                stats["objects"] += max(objects.values()) if objects else 0
                stats["success"] += entry.get("success", 0)
                stats["failed"] += entry.get("failed", 0)

            write_line(
                f"Success={payload.get('success', 0)} "
                f"Failed={payload.get('failed', 0)} "
                f"Objects={stats['objects']}"
            )

            if payload.get("next_node"):
                write_line(f"Next node: {payload['next_node']}")
            else:
                write_line("No next node, finished this UID")

        return stats


# ======================================================================
# 2) ZOPE EXTERNAL METHOD (imports only inside the function)
# ======================================================================

RUN_LOCK = threading.Lock()
RUN_IN_PROGRESS = False
RUN_LOCK_FD = None

def _get_lockfile_path(base_url):
    safe = "".join(ch if ch.isalnum() else "_" for ch in base_url)
    return os.path.join(tempfile.gettempdir(), f"zms_reindex_{safe}.lock")

def _try_acquire_singleflight_lock(base_url):
    lockfile_path = _get_lockfile_path(base_url)
    fd = os.open(lockfile_path, os.O_CREAT | os.O_RDWR, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return fd
    except OSError:
        os.close(fd)
        return None

def _release_singleflight_lock(fd):
    if fd is None:
        return
    try:
        fcntl.flock(fd, fcntl.LOCK_UN)
    finally:
        os.close(fd)


def manage_reindex_content_bg(self):
    """
    Zope external method entry point.
    Uses the REST-only reindexer.
    Zope imports are inside this function.
    """
    import logging
    LOGGER = logging.getLogger("Zope")

    request = self.REQUEST
    base_url = self.getDocumentElement().absolute_url()
    connector = request.get("connector", "/zcatalog_adapter/zcatalog_connector/")
    page_size = int(request.get("page_size", 100))
    fileparsing = bool(request.get("fileparsing", False))

    global RUN_IN_PROGRESS, RUN_LOCK_FD

    with RUN_LOCK:
        if RUN_IN_PROGRESS:
            target = self.url_append_params(
                "%s/manage_main" % self.absolute_url(),
                {"manage_tabs_message": "Background Job is already running"},
            )
            return request.response.redirect(target)

        lock_fd = _try_acquire_singleflight_lock(base_url)
        if lock_fd is None:
            target = self.url_append_params(
                "%s/manage_main" % self.absolute_url(),
                {"manage_tabs_message": "Background Job is already running"},
            )
            return request.response.redirect(target)

        RUN_LOCK_FD = lock_fd
        RUN_IN_PROGRESS = True

    def worker():
        global RUN_IN_PROGRESS, RUN_LOCK_FD
        try:
            LOGGER.info("Starting background reindex job for %s", base_url)

            reindexer = ZMSIndexSchematizedReindexer(
                base_url=base_url,
                connector=connector,
                page_size=page_size,
                fileparsing=fileparsing,
            )

            stats = reindexer.run(write_line=lambda line: LOGGER.info(line))
            LOGGER.info("Finished reindex job: %s", stats)

        except Exception:
            LOGGER.exception("manage_reindex_content_bg failed")
        finally:
            with RUN_LOCK:
                _release_singleflight_lock(RUN_LOCK_FD)
                RUN_LOCK_FD = None
                RUN_IN_PROGRESS = False

    thread = threading.Thread(target=worker, name="manage_reindex_content_bg", daemon=True)
    thread.start()

    return request.response.redirect(
        self.url_append_params(
            "%s/manage_main" % self.absolute_url(),
            {"manage_tabs_message": "Background Job has Started"},
        )
    )


# ======================================================================
# 3) CLI RUNNER
# ======================================================================

def main():
    parser = argparse.ArgumentParser(description="Standalone ZMS REST reindexer")
    parser.add_argument("base_url", help="Base URL, e.g. http://127.0.0.1:8080/myzms/content")
    parser.add_argument("--connector", default="/zcatalog_adapter/zcatalog_connector/")
    parser.add_argument("--page-size", type=int, default=100)
    parser.add_argument("--fileparsing", action="store_true")
    args = parser.parse_args()

    reindexer = ZMSIndexSchematizedReindexer(
        base_url=args.base_url,
        connector=args.connector,
        page_size=args.page_size,
        fileparsing=args.fileparsing,
    )

    print("Starting reindex…")
    stats = reindexer.run(write_line=print)
    print("Summary:", stats)


if __name__ == "__main__":
    main()