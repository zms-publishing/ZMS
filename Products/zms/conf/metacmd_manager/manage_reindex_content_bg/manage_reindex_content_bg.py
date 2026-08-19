import argparse
import ast
import fcntl
import json
import logging
import os
import requests
import threading
import tempfile
from typing import Dict


LOGGER = logging.getLogger("Zope")
RUN_LOCK = threading.Lock()
RUN_IN_PROGRESS = False
RUN_LOCK_FD = None


def _get_lockfile_path(base_url):
	safe = "".join(ch if ch.isalnum() else "_" for ch in base_url)
	return os.path.join(tempfile.gettempdir(), f"zms_manage_reindex_content_bg_{safe}.lock")


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


def _get_reindex_scope(context):
	document_element = context.getDocumentElement()
	is_portal_master = context == document_element and context.getPortalMaster() is None
	if is_portal_master:
		scope_context = context.getHome()
		scope_mode = "portal-master"
	else:
		scope_context = context
		scope_mode = "recursive"
	return scope_context, scope_mode


def _open_thread_context(physical_path):
	import Zope2
	from AccessControl.SecurityManagement import noSecurityManager
	from AccessControl.users import system as system_user
	from Testing.makerequest import makerequest
	app = Zope2.app()
	app = makerequest(app)
	app.REQUEST['PARENTS'] = [app]
	app.REQUEST.set('ZMS_CONTEXT_URL', True)
	newSecurityManager(None, system_user)
	traversal_path = '/'.join([x for x in physical_path if x])
	context = app.unrestrictedTraverse(traversal_path)
	return app, context


def _close_thread_context(app):
	import transaction
	from AccessControl.SecurityManagement import noSecurityManager
	try:
		transaction.abort()
	except Exception:
		pass
	try:
		noSecurityManager()
	except Exception:
		pass
	if app is not None and getattr(app, '_p_jar', None) is not None:
		app._p_jar.close()


class ZMSIndexSchematizedReindexer:
	def __init__(self, context, base_url, scope_context=None, scope_mode="recursive"):
		self.context = context
		self.base_url = base_url.rstrip("/")
		self.scope_root = scope_context or context
		self.scope_url = self.scope_root.absolute_url().rstrip("/")
		self.scope_path = "/%s" % self.scope_root.absolute_url(relative=True)
		self.scope_mode = scope_mode
		self.connector = connector

	def _api(self, path, **params):
		url = f"{self.base_url}/{path}"
		response = requests.get(url, params=params, timeout=60)
		response.raise_for_status()
		try:
			payload = response.json()
		except Exception:
			text = (response.text or "").strip()
			try:
				payload = json.loads(text)
			except Exception:
				try:
					payload = ast.literal_eval(text)
				except Exception:
					raise ValueError(
						"Invalid REST payload (status=%s, content-type=%s): %.240s"
						% (response.status_code, response.headers.get("Content-Type", "?"), text)
					)
		if isinstance(payload, dict) and payload.get("ERROR"):
			raise LookupError(
				"REST returned ERROR=%s ids=%s path=%s"
				% (payload.get("ERROR"), payload.get("ids"), payload.get("path_to_handle"))
			)
		return payload, url

	def _iter_index_uids(self):
		"""
		Pure REST-based tree traversal.
		Retrieves all nodes with meta_id='ZMS' (portal clients)
		starting from the base_url root.
		"""

		def fetch_children(path):
			url = f"{self.base_url}/++rest_api/{path}/list_child_nodes"
			payload = requests.get(url, timeout=60).json()
			return payload  # list of nodes with id, meta_id, uid, getPath

		# Start at root path
		root_path = ""  # means: base_url/++rest_api/list_child_nodes
		stack = [root_path]
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

				# Yield only portal clients (meta_id == 'ZMS')
				if meta_id == "ZMS":
					yield uid, meta_id, node_path

				# Recurse deeper
				# Convert physical path into REST path
				if node_path:
					rest_path = node_path.lstrip("/")
					stack.append(rest_path)

def run(self, write_line=None):
    if write_line is None:
        write_line = print

    adapter = self.context.getCatalogAdapter()
    connectors = adapter.get_connectors()
    if not connectors:
        raise RuntimeError("No catalog connector available")
    connector = connectors[0]

    stats: Dict[str, int] = {
        "candidates": 0,
        "requests": 0,
        "objects": 0,
        "success": 0,
        "failed": 0,
        "skipped": 0,
    }

    # Iterate over all indexable UIDs
    for uid, meta_id, node_path in self._iter_index_uids(adapter):
        stats["candidates"] += 1

        params = {
            "uid": uid,
            "page_size:int": connector.get_page_size() if hasattr(connector, "get_page_size") else 100,
            "clients:int": 0,
            "fileparsing:int": 1 if getattr(connector, "fileparsing", False) else 0,
        }

        write_line(f"Reindexing UID={uid} meta_id={meta_id} path={node_path}")

        try:
            # Perform REST call
            payload, url = self._api(f"{connector}/reindex_page", **params)
            stats["requests"] += 1

        except Exception as e:
            stats["failed"] += 1
            write_line(f"ERROR calling REST API for uid={uid}: {e}")
            continue

        # Handle "cleared" info
        if "cleared" in payload:
            write_line(f"Cleared {payload.get('home_id')}: {payload['cleared']}")

        # Process log entries
        logs = payload.get("log", [])
        for entry in logs:
            objects = entry.get("objects", {})
            max_per_lang = max(objects.values()) if objects else 0
            stats["objects"] += max_per_lang
            stats["success"] += entry.get("success", 0)
            stats["failed"] += entry.get("failed", 0)

        # Summary for this UID
        write_line(
            f"Success={payload.get('success', 0)} "
            f"Failed={payload.get('failed', 0)} "
            f"Objects={stats['objects']}"
        )

        # Continue with next node if provided
        next_node = payload.get("next_node")
        if next_node:
            write_line(f"Next node: {next_node}")
            # Replace UID and continue loop
            continue

        else:
            write_line("No next node, finished this UID")

    return stats


def manage_reindex_content_bg( self):
	global RUN_IN_PROGRESS, RUN_LOCK_FD
	request = self.REQUEST
	physical_path = tuple(self.getPhysicalPath())
	base_url = self.getDocumentElement().absolute_url()
	scope_context, scope_mode = _get_reindex_scope(self)
	connector = request.get("connector", "/zcatalog_adapter/zcatalog_connector/")

	with RUN_LOCK:
		if RUN_IN_PROGRESS:
			LOGGER.info("[%s] concurrent start rejected", base_url)
			target = self.url_append_params(
				"%s/manage_main" % self.absolute_url(),
				{
					"manage_tabs_message": "Background Job is already running",
				},
			)
			return request.response.redirect(target)

		lock_fd = _try_acquire_singleflight_lock(base_url)
		if lock_fd is None:
			LOGGER.info("[%s] concurrent start rejected (process lock held)", base_url)
			target = self.url_append_params(
				"%s/manage_main" % self.absolute_url(),
				{
					"manage_tabs_message": "Background Job is already running",
				},
			)
			return request.response.redirect(target)

		RUN_LOCK_FD = lock_fd
		RUN_IN_PROGRESS = True

	def _worker():
		global RUN_IN_PROGRESS, RUN_LOCK_FD
		app = None
		try:
			log_prefix = f"[{base_url}]"

			def _write_to_zope_log(line):
				LOGGER.info("%s %s", log_prefix, line)

			LOGGER.info("%s started", log_prefix)
			app, thread_context = _open_thread_context(physical_path)
			thread_scope_context = app.unrestrictedTraverse('/'.join([x for x in scope_context.getPhysicalPath() if x]))
			reindexer = ZMSIndexSchematizedReindexer(context=thread_context, base_url=base_url, scope_context=thread_scope_context, scope_mode=scope_mode, connector=connector)
			LOGGER.info("%s scope_mode=%s scope_url=%s scope_path=%s", log_prefix, reindexer.scope_mode, reindexer.scope_url, reindexer.scope_path)
			stats = reindexer.run(write_line=_write_to_zope_log)
			LOGGER.info("%s summary=%s", log_prefix, stats)
			LOGGER.info("%s finished", log_prefix)
		except Exception:
			LOGGER.exception("manage_reindex_content_bg failed")
		finally:
			_close_thread_context(app)
			with RUN_LOCK:
				_release_singleflight_lock(RUN_LOCK_FD)
				RUN_LOCK_FD = None
				RUN_IN_PROGRESS = False

	thread = threading.Thread(target=_worker, name="manage_reindex_content_bg", daemon=True)
	thread.start()

	message = "Background Job has Started"
	target = self.url_append_params(
		"%s/manage_main" % self.absolute_url(),
		{
			"manage_tabs_message": message,
		},
	)
	return request.response.redirect(target)


def main():
	parser = argparse.ArgumentParser(
		description="Reindex schematized content through ZMSIndex traversal"
	)
	parser.add_argument(
		"base_url",
		help="Base content URL, e.g. https://example.com/content"
	)
	parser.add_argument(
		"--connector",
		default="/zcatalog_adapter/zcatalog_connector/",
		help="Connector path for REST API calls (default: /zcatalog_adapter/zcatalog_connector/)"
	)

	args = parser.parse_args()
	print("Use manage_reindex_content_bg(self) in Zope runtime.")


if __name__ == "__main__":
	main()