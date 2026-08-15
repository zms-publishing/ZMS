import argparse
import ast
import fcntl
import json
import logging
import os
import requests
import threading
import tempfile
import transaction
from typing import Dict
import Zope2
from AccessControl.SecurityManagement import newSecurityManager, noSecurityManager
from AccessControl.users import system as system_user
from Testing.makerequest import makerequest


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


def _brain_get(brain, key, default=None):
	try:
		return brain[key]
	except Exception:
		value = getattr(brain, key, default)
		if callable(value):
			try:
				return value()
			except Exception:
				return default
		return value


def _normalize_uid_token(uid):
	uid = (uid or "").strip()
	if not uid:
		return ""
	return uid if uid.startswith("uid:") else "uid:%s" % uid


def _url_from_path(scope_url, node_path, scope_path=None):
	if not node_path:
		return ""
	parts = [x for x in str(node_path).split("/") if x]
	scope_parts = [x for x in str(scope_path or "").split("/") if x]
	if scope_parts and parts[:len(scope_parts)] == scope_parts:
		rel = "/".join(parts[len(scope_parts):])
		return "%s/%s" % (scope_url.rstrip("/"), rel) if rel else scope_url.rstrip("/")
	return scope_url.rstrip("/")


def _resolve_node_by_path(context, path, scope_root=None):
	if not path:
		return None
	parts = [x for x in str(path).split("/") if x]
	roots = []
	for root in [scope_root, context.getRootElement(), context.getHome()]:
		if root is None or root in roots:
			continue
		roots.append(root)
	for root in roots:
		root_parts = [x for x in root.getPhysicalPath() if x]
		if parts[:len(root_parts)] != root_parts:
			continue
		ob = root
		for item_id in parts[len(root_parts):]:
			ob = getattr(ob, item_id, None)
			if ob is None:
				break
		if ob is not None:
			return ob
	return None


def _resolve_node_for_doc(context, doc, fallback_path=None, scope_root=None):
	data_uid = (doc.get("uid") or "").strip()
	if data_uid:
		token = "{$%s}" % data_uid
		node = context.getLinkObj(token)
		if node is not None:
			return node, "getLinkObj(uid)"
		node = context.findObject(token)
		if node is not None:
			return node, "findObject(uid)"

	for candidate in [doc.get("path"), doc.get("loc"), fallback_path]:
		node = _resolve_node_by_path(context, candidate, scope_root=scope_root)
		if node is not None:
			return node, "path"

	return None, ""


def _normalize_doc_for_indexing(doc):
	normalized = dict(doc)
	for key in ("created_dt", "change_dt", "start_dt", "end_dt", "indexing_dt"):
		value = normalized.get(key)
		if isinstance(value, str) and " " in value and "T" not in value:
			normalized[key] = value.replace(" ", "T", 1)
	return normalized


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
	app = Zope2.app()
	app = makerequest(app)
	app.REQUEST['PARENTS'] = [app]
	app.REQUEST.set('ZMS_CONTEXT_URL', True)
	newSecurityManager(None, system_user)
	traversal_path = '/'.join([x for x in physical_path if x])
	context = app.unrestrictedTraverse(traversal_path)
	return app, context


def _close_thread_context(app):
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
	def __init__(self, context, base_url, scope_context=None, scope_mode="recursive", lang="de"):
		self.context = context
		self.base_url = base_url.rstrip("/")
		self.scope_root = scope_context or context
		self.scope_url = self.scope_root.absolute_url().rstrip("/")
		self.scope_path = "/%s" % self.scope_root.absolute_url(relative=True)
		self.scope_mode = scope_mode
		self.lang = lang
		self.params = {"preview": "preview", "lang": lang}

	def _api(self, path):
		url = f"{self.base_url}/++rest_api/{path}"
		response = requests.get(url, params=self.params, timeout=60)
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

	def _iter_index_uids(self, adapter):
		brains = self.context.zcatalog_index({"path": self.scope_path})
		meta_ids = set(self.context.getMetaobjManager().getTypedMetaIds(adapter.getIds()))
		seen = set()
		for brain in brains:
			meta_id = _brain_get(brain, "meta_id", "")
			if meta_id not in meta_ids:
				continue
			uid = _brain_get(brain, "uid", None) or _brain_get(brain, "get_uid", None)
			node_path = _brain_get(brain, "getPath", None) or _brain_get(brain, "path", None)
			if not uid or uid in seen:
				continue
			seen.add(uid)
			yield uid, meta_id, node_path

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

		for uid, meta_id, node_path in self._iter_index_uids(adapter):
			stats["candidates"] += 1
			normalized_uid = _normalize_uid_token(uid)
			node_url = _url_from_path(self.scope_url, node_path, self.scope_path)
			try:
				payload, rest_url = self._api(f"{normalized_uid}/get_indexschematized_content")
			except Exception as e:
				msg = str(e)
				if "REST returned ERROR=Not Found" in msg:
					stats["skipped"] += 1
					write_line(
						"skipped [%s] uid=%s node_path=%s node_url=%s: not found in REST traversal"
						% (meta_id, normalized_uid, node_path, node_url)
					)
				else:
					stats["failed"] += 1
					write_line(
						"failed [%s] uid=%s node_path=%s node_url=%s rest_url=%s: REST error: %s"
						% (meta_id, normalized_uid, node_path, node_url, f"{self.base_url}/++rest_api/{normalized_uid}/get_indexschematized_content", e)
					)
				continue

			stats["requests"] += 1
			docs = payload.get("docs", [])
			if not docs:
				stats["skipped"] += 1
				write_line(
					"skipped [%s] uid=%s node_path=%s node_url=%s rest_url=%s: no docs"
					% (meta_id, normalized_uid, node_path, node_url, rest_url)
				)
				continue

			objects = []
			unresolved = []
			resolver_stats: Dict[str, int] = {}
			for data in docs:
				node, resolver = _resolve_node_for_doc(self.context, data, fallback_path=node_path, scope_root=self.scope_root)
				if node is None:
					unresolved.append({
						"uid": data.get("uid"),
						"path": data.get("path") or data.get("loc") or node_path,
					})
					continue
				resolver_stats[resolver] = resolver_stats.get(resolver, 0) + 1
				objects.append((node, _normalize_doc_for_indexing(data)))

			if not objects:
				stats["skipped"] += 1
				sample = unresolved[:3]
				write_line(
					"skipped [%s] uid=%s node_path=%s node_url=%s rest_url=%s: no resolvable objects (unresolved=%s sample=%s)"
					% (meta_id, normalized_uid, node_path, node_url, rest_url, len(unresolved), sample)
				)
				continue

			try:
				success, failed = connector.manage_objects_add(objects)
			except Exception as e:
				stats["failed"] += len(objects)
				write_line(
					"failed [%s] uid=%s node_path=%s node_url=%s rest_url=%s: index add error: %s"
					% (meta_id, normalized_uid, node_path, node_url, rest_url, e)
				)
				continue

			stats["objects"] += len(objects)
			stats["success"] += int(success or 0)
			stats["failed"] += int(failed or 0)
			write_line(
				"indexed [%s] uid=%s node_path=%s node_url=%s rest_url=%s docs=%s resolved_by=%s success=%s failed=%s"
				% (meta_id, normalized_uid, node_path, node_url, rest_url, len(objects), resolver_stats, int(success or 0), int(failed or 0))
			)

		return stats


def manage_reindex_content_bg( self):
	global RUN_IN_PROGRESS, RUN_LOCK_FD
	request = self.REQUEST
	physical_path = tuple(self.getPhysicalPath())
	base_url = self.getDocumentElement().absolute_url()
	scope_context, scope_mode = _get_reindex_scope(self)
	lang = request.get("lang", "ger")

	with RUN_LOCK:
		if RUN_IN_PROGRESS:
			LOGGER.info("[%s] concurrent start rejected", base_url)
			target = self.url_append_params(
				"%s/manage_main" % self.absolute_url(),
				{
					"lang": lang,
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
					"lang": lang,
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
			reindexer = ZMSIndexSchematizedReindexer(context=thread_context, base_url=base_url, scope_context=thread_scope_context, scope_mode=scope_mode, lang=lang)
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
			"lang": lang,
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
		"--lang",
		default="de",
		help="Language parameter for REST API calls (default: de)"
	)

	args = parser.parse_args()
	print("Use manage_reindex_content_bg(self) in Zope runtime.")


if __name__ == "__main__":
	main()