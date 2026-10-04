#!/usr/bin/env python3
"""
Unified ZMS reindexer:
- Pure REST-based reindexer (no Zope dependencies)
- Zope external method: manage_reindex_content_bg(self)
- CLI runner: python3 manage_reindex_content_bg.py BASE_URL [--connector ...]
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

	def __init__(self, base_url, connector, uid='{$}', page_size=100, fileparsing=False,
				 start_path="", start_node=None, cancel_event=None,
				 cancellation_file=None):
		self.base_url = base_url.rstrip("/")
		self.connector = connector.strip("/")
		self.uid = uid
		self.page_size = page_size
		self.fileparsing = 1 if fileparsing else 0
		self.start_path = start_path.strip("/")
		self.start_node = start_node
		self.cancel_event = cancel_event
		self.cancellation_file = cancellation_file

	def _stop_requested(self):
		return (
			(self.cancel_event is not None and self.cancel_event.is_set())
			or (self.cancellation_file is not None
				and os.path.exists(self.cancellation_file))
		)

	def _extract_client_path(self, node_path: str) -> str:
		parts = [p for p in node_path.split("/") if p]

		# The first physical-path segment is the ZMS root object.
		if parts:
			parts = parts[1:]

		# Internal references use "@" where a physical path contains "content".
		if parts and parts[0] == "content":
			parts = parts[1:]
		if parts and parts[-1] == "content":
			parts = parts[:-1]
		path = "/".join(parts)
		return path.replace("/content/", "@")

	# ------------------------------------------------------------------
	# REST helpers
	# ------------------------------------------------------------------

	def _api(self, path, **params):
		url = f"{self.base_url}/{path.lstrip('/')}"
		response = requests.get(url, params=params, timeout=60)
		response.raise_for_status()

		try:
			return response.json(), response.url
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

	def _iter_index_nodes(self):

		def fetch_children(path):
			rest_path = path.strip("/")
			url = f"{self.base_url}/++rest_api/{rest_path}/list_child_nodes"
			response = requests.get(url, timeout=60)
			response.raise_for_status()
			return response.json()

		stack = [self.start_path]
		seen = set()

		if self.start_node is not None:
			uid = self.start_node.get("uid")
			node_path = self.start_node.get("getPath")
			if not uid or not node_path:
				raise ValueError("Starting context must include uid and getPath")
			seen.add(uid)
			yield uid, self.start_node.get("meta_id"), node_path

		while stack and not self._stop_requested():
			path = stack.pop()

			try:
				nodes = fetch_children(path)
			except Exception as e:
				if self._stop_requested():
					return
				LOGGER.error(f"REST error fetching children for {path}: {e}")
				continue

			for node in nodes:
				if self._stop_requested():
					return
				uid = node.get("uid")
				meta_id = node.get("meta_id")
				node_path = node.get("getPath")

				if not uid or not node_path or uid in seen:
					continue
				seen.add(uid)

				yield uid, meta_id, node_path
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

		for uid, meta_id, node_path in self._iter_index_nodes():
			if self._stop_requested():
				write_line("Stop requested; stopping reindex worker")
				break

			stats["candidates"] += 1
			client_path = "{$@%s}" % self._extract_client_path(node_path)
			write_line(f"Reindexing UID={uid} meta_id={meta_id} path={client_path}")

			params = {
				"uid": client_path,
				"page_size:int": self.page_size,
				"clients:int": 0,
				"fileparsing:int": self.fileparsing,
			}

			try:
				payload, url = self._api(f"{self.connector}/reindex_page", **params)
				for x in payload['log']:
					write_line(f"LOG {x}")
				stats['success'] += payload['success']
				stats['failed'] += payload['failed']
				stats["requests"] += 1
			except Exception as e:
				if self._stop_requested():
					write_line("Stop requested; stopping reindex worker")
					break
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

			if self._stop_requested():
				write_line("Stop requested; stopping reindex worker")
				break

		return stats



# ======================================================================
# 2) ZOPE EXTERNAL-METHOD
# ======================================================================

RUN_LOCK = threading.Lock()
RUN_IN_PROGRESS = False
RUN_LOCK_FD = None
RUN_JOB = None

# ----------------------------------------------------------------
# 2A) ZOPE EXTERNAL-METHOD: Helper functions
# ----------------------------------------------------------------
def _get_lockfile_path(base_url):
	safe = "".join(ch if ch.isalnum() else "_" for ch in base_url)
	return os.path.join(tempfile.gettempdir(), f"zms_reindex_{safe}.lock")

def _get_lock_guard_path(base_url):
	return _get_lockfile_path(base_url) + ".guard"

def _get_cancellation_file_path(base_url):
	return _get_lockfile_path(base_url) + ".stop"

def _acquire_lock_guard(base_url):
	fd = os.open(_get_lock_guard_path(base_url), os.O_CREAT | os.O_RDWR, 0o644)
	fcntl.flock(fd, fcntl.LOCK_EX)
	return fd

def _release_lock_guard(fd):
	try:
		fcntl.flock(fd, fcntl.LOCK_UN)
	finally:
		os.close(fd)

def _test_single_flight_locked(base_url):
	"""
	Check whether a single-flight lock is currently held.
	Returns the lockfile path if locked, or None if free.
	"""
	lockfile_path = _get_lockfile_path(base_url)
	guard_fd = _acquire_lock_guard(base_url)
	try:
		try:
			fd = os.open(lockfile_path, os.O_RDWR)
		except FileNotFoundError:
			return None

		try:
			try:
				fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
			except OSError:
				return lockfile_path

			fcntl.flock(fd, fcntl.LOCK_UN)
			os.unlink(lockfile_path)
			return None
		finally:
			os.close(fd)
	finally:
		_release_lock_guard(guard_fd)

def _try_acquire_singleflight_lock(base_url):
	lockfile_path = _get_lockfile_path(base_url)
	guard_fd = _acquire_lock_guard(base_url)
	try:
		fd = os.open(lockfile_path, os.O_CREAT | os.O_RDWR, 0o644)
		try:
			fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
			return fd
		except OSError:
			os.close(fd)
			return None
	finally:
		_release_lock_guard(guard_fd)

def _release_singleflight_lock(fd, base_url):
	if fd is None:
		return
	guard_fd = _acquire_lock_guard(base_url)
	try:
		fcntl.flock(fd, fcntl.LOCK_UN)
	finally:
		try:
			os.close(fd)
			try:
				os.unlink(_get_lockfile_path(base_url))
			except FileNotFoundError:
				pass
		finally:
			_release_lock_guard(guard_fd)

def _release_job_lock(job):
	if job["lock_released"]:
		return
	job["lock_released"] = True
	fd = job["lock_fd"]
	job["lock_fd"] = None
	_release_singleflight_lock(fd, job["base_url"])

def _request_cancellation(base_url):
	cancellation_file = _get_cancellation_file_path(base_url)
	fd = os.open(cancellation_file, os.O_CREAT | os.O_WRONLY | os.O_TRUNC, 0o644)
	os.close(fd)

def start(self):
	import logging
	LOGGER = logging.getLogger("Zope")

	request = self.REQUEST
	root = self.getRootElement()
	base_url = root.absolute_url()
	context_path = tuple(self.getPhysicalPath())
	start_path = "/".join(str(part) for part in context_path if part)
	if not start_path:
		raise ValueError("Unable to determine current context path")
	start_node = {
		"uid": self.get_uid(),
		"meta_id": self.meta_id,
		"getPath": "/" + start_path,
	}
	catalog_adapter = root.getCatalogAdapter()
	catalog_connector = catalog_adapter.get_connectors()[0]
	connector = request.get("connector", f"/{catalog_adapter.getId()}/{catalog_connector.getId()}/")
	uid = request.get("uid", root.getRefObjPath(self.getDocumentElement()))
	page_size = int(request.get("page_size", 1))
	fileparsing = bool(request.get("fileparsing", False))

	global RUN_IN_PROGRESS, RUN_LOCK_FD, RUN_JOB
 
	with RUN_LOCK:
		lock_fd = _try_acquire_singleflight_lock(base_url)
		if lock_fd is None:
			return "Background Job is already running"

		cancellation_file = _get_cancellation_file_path(base_url)
		try:
			os.unlink(cancellation_file)
		except FileNotFoundError:
			pass

		job = {
			"base_url": base_url,
			"lock_fd": lock_fd,
			"lock_released": False,
			"cancel_event": threading.Event(),
			"cancellation_file": cancellation_file,
		}
		RUN_JOB = job
		RUN_LOCK_FD = lock_fd
		RUN_IN_PROGRESS = True

	def worker():
		global RUN_IN_PROGRESS, RUN_LOCK_FD, RUN_JOB

		try:
			LOGGER.info("Starting background reindex job for %s", base_url)

			reindexer = ZMSIndexSchematizedReindexer(
				base_url=base_url,
				connector=connector,
				uid=uid,
				page_size=page_size,
				fileparsing=fileparsing,
				start_path=start_path,
				start_node=start_node,
				cancel_event=job["cancel_event"],
				cancellation_file=cancellation_file,
			)

			stats = reindexer.run(write_line=lambda line: LOGGER.info(line))
			LOGGER.info("Finished reindex job: %s", stats)

		except Exception:
			LOGGER.exception("manage_reindex_content_bg failed")
		finally:
			with RUN_LOCK:
				if RUN_JOB is job:
					try:
						os.unlink(cancellation_file)
					except FileNotFoundError:
						pass
				_release_job_lock(job)
				if RUN_JOB is job:
					RUN_JOB = None
					RUN_LOCK_FD = None
					RUN_IN_PROGRESS = False

	thread = threading.Thread(target=worker, name="manage_reindex_content_bg", daemon=True)
	thread.start()
	return "Background Job started"

def stop(self):
	global RUN_IN_PROGRESS, RUN_LOCK_FD, RUN_JOB

	base_url = self.getRootElement().absolute_url()
	with RUN_LOCK:
		job = RUN_JOB
		if job is not None and job["base_url"] == base_url:
			job["cancel_event"].set()
			_release_job_lock(job)
			RUN_JOB = None
			RUN_LOCK_FD = None
			RUN_IN_PROGRESS = False
			return "Background Job stopped; the current REST request may finish"

		if _test_single_flight_locked(base_url):
			_request_cancellation(base_url)
			return "Stop requested; the worker will stop after its current REST request"
		return "No background job is running"

# ----------------------------------------------------------------
# 2B) ZOPE EXTERNAL-METHOD: Entry point
# ----------------------------------------------------------------

def manage_reindex_content_bg(self):
	"""
	Zope external method entry point.
	Uses the REST-only reindexer.
	Zope imports are inside this function.
	"""
	from Products.zms import standard

	request = self.REQUEST
	message = None
	btn = request.form.get('btn')
	if btn == "BTN_START":
		message = start(self)
	elif btn == "BTN_STOP":
		message = stop(self)

	connector_url = ''
	try:
		catalog_adapter = self.getCatalogAdapter()
		connectors = catalog_adapter.get_connectors()
		if connectors:
			connector_url = connectors[0].absolute_url()
	except:
		connector_url = ''

	lockfile_path = _test_single_flight_locked(self.getRootElement().absolute_url())

	html = []
	html.append('<!DOCTYPE html>')
	html.append('<html lang="en">')
	html.append(self.zmi_html_head(self,request))
	html.append('<body class="%s">'%self.zmi_body_class(id='manage_reindex_content'))
	html.append(self.zmi_body_header(self,request))
	html.append('<div id="zmi-tab">')
	html.append(self.zmi_breadcrumbs(self,request,extra=[{'label':'Reindex Content','action':'manage_reindex_content'}]))
	if message:
		html.append('<div class="alert alert-info" role="alert">%s</div>'%standard.html_quote(message))
	html.append("""
		<form class="form-horizontal card" name="form0" method="post" enctype="multipart/form-data">
			<input type="hidden" id="lang" name="lang" value="%s"/>
			<legend>Background Reindexing</legend>
			<div class="card-body">
				<div class="form-group row">
					<label class="col-sm-2 control-label">Catalog Connector</label>
					<div class="col-sm-10">
						<input class="form-control" id="catalog_connector_url" name="catalog_connector_url" type="text" value="%s" readonly="readonly" />
					</div>
				</div><!-- .form-group -->
				<div class="form-group row">
					<label class="col-sm-2 control-label">Page Size</label>
					<div class="col-sm-10">
						<input class="form-control" id="page_size" name="page_size:int" type="number" min="1" value="1" />
						<small class="form-text text-muted">API batch size per call (1 = one node per call)</small>
					</div>
				</div><!-- .form-group -->
				<div class="form-group row">
					<label class="col-sm-2 control-label"></label>
					<div class="col-sm-10">
						<button id="start-button" class="btn btn-secondary mr-2" name="btn" value="BTN_START">
							<i class="fas fa-play text-success"></i>
						</button>
						<button id="stop-button" class="btn btn-secondary" name="btn" value="BTN_STOP">
							<i class="fas fa-stop"></i>
						</button>
					</div>
				</div>
			</div><!-- .card-body -->
		</form>
	"""%(request['lang'], standard.html_quote(connector_url)))
	html.append('</div><!-- #zmi-tab -->')
	html.append(self.zmi_body_footer(self,request))
	html.append('</body>')
	html.append('</html>')

	return '\n'.join(html)



# ======================================================================
# 3) CLI RUNNER
# ======================================================================

def main():
	parser = argparse.ArgumentParser(description="Standalone ZMS REST reindexer")
	parser.add_argument("base_url", help="Base URL, e.g. http://127.0.0.1:8080/myzms/content")
	parser.add_argument("--connector", default="/zcatalog_adapter/zcatalog_connector/")
	parser.add_argument("--uid", help="Start UID, default: start from root {$}", default="{$}")
	parser.add_argument("--page-size", type=int, default=100)
	parser.add_argument("--fileparsing", action="store_true")
	args = parser.parse_args()

	reindexer = ZMSIndexSchematizedReindexer(
		base_url=args.base_url,
		connector=args.connector,
		uid=args.uid,
		page_size=args.page_size,
		fileparsing=args.fileparsing,
	)

	print("Starting reindex…")
	stats = reindexer.run(write_line=print)
	print("Summary:", stats)


if __name__ == "__main__":
	main()