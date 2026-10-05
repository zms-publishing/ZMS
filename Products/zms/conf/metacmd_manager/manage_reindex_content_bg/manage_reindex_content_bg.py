#!/usr/bin/env python3
"""
Unified ZMS reindexer:
- Zope external method: manage_reindex_content_bg(self)
- REST-based reindexer
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
import uuid
from datetime import datetime, timezone
import requests

LOGGER = logging.getLogger("ZMSReindex")
logging.basicConfig(level=logging.INFO)


# ======================================================================
# 1) REST-based REINDEXER
# ======================================================================

class ZMSIndexSchematizedReindexer:
	"""
	REST-based reindexer.
	Works standalone or inside Zope.
	"""

	def __init__(self, base_url, connector, uid='{$}', page_size=100, fileparsing=False,
			start_nodes=None, cancel_event=None,
			cancellation_file=None, progress_callback=None, meta_ids=None):
		self.base_url = base_url.rstrip("/")
		self.connector = connector.strip("/")
		self.uid = uid
		self.page_size = page_size
		self.fileparsing = 1 if fileparsing else 0
		# List of ZMS clients ({home_id, uid, meta_id, getPath}), each one is
		# traversed on its own without descending into other clients.
		# None: traverse the whole site from the root of base_url.
		self.start_nodes = start_nodes
		self.traversal_errors = 0
		self.cancel_event = cancel_event
		self.cancellation_file = cancellation_file
		self.progress_callback = progress_callback
		# None: reindex every node; otherwise only nodes with these meta_ids
		self.meta_ids = None if meta_ids is None else set(meta_ids)

	def _report_progress(self, stats, state="running", current_uid=None, current_path=None):
		if self.progress_callback is not None:
			self.progress_callback(
				stats, state=state, current_uid=current_uid,
				current_path=current_path,
			)

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

	def _meta_id_indexable(self, meta_id):
		return self.meta_ids is None or meta_id in self.meta_ids

	def _iter_client_nodes(self, client, seen):
		"""Yield the indexable nodes of one client (sub-clients are not entered)."""

		def fetch_children(path):
			rest_path = path.strip("/")
			url = f"{self.base_url}/++rest_api/{rest_path}/list_child_nodes"
			response = requests.get(url, timeout=60)
			response.raise_for_status()
			return response.json()

		if client is None:
			stack = [""]
		else:
			uid = client.get("uid")
			node_path = client.get("getPath")
			if not uid or not node_path:
				raise ValueError("Starting node must include uid and getPath")
			stack = [node_path.strip("/")]
			seen.add(uid)
			if self._meta_id_indexable(client.get("meta_id")):
				yield uid, client.get("meta_id"), node_path

		while stack and not self._stop_requested():
			path = stack.pop()

			try:
				nodes = fetch_children(path)
			except Exception as e:
				if self._stop_requested():
					return
				self.traversal_errors += 1
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
				# Other ZMS clients are reindexed only if selected themselves
				if client is not None and meta_id == "ZMS":
					continue
				seen.add(uid)

				if self._meta_id_indexable(meta_id):
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
			"nodes_completed": 0,
			"total_clients": len(self.start_nodes) if self.start_nodes else 0,
			"total_nodes": _sum_expected(self.start_nodes),
			"completed_clients": [],
			"failed_clients": [],
		}
		self._report_progress(stats)

		clients = self.start_nodes if self.start_nodes else [None]
		seen = set()
		stopped = False
		for client in clients:
			if self._stop_requested():
				break
			errors_before = self.traversal_errors
			failed_before = stats["failed"]
			stopped = self._run_client(client, seen, stats, write_line)
			if stopped:
				break
			if client is not None:
				home_id = client.get("home_id")
				if self.traversal_errors > errors_before or stats["failed"] > failed_before:
					stats["failed_clients"].append(home_id)
				else:
					stats["completed_clients"].append(home_id)
				write_line(f"Finished ZMS-node {home_id}")
				self._report_progress(stats)

		self._report_progress(
			stats, state="stopped" if self._stop_requested() else "completed",
			current_uid=None, current_path=None,
		)
		return stats

	def _run_client(self, client, seen, stats, write_line):
		"""Reindex one client; returns True if the run has been stopped."""
		for uid, meta_id, node_path in self._iter_client_nodes(client, seen):
			if self._stop_requested():
				write_line("Stop requested; stopping reindex worker")
				return True

			stats["candidates"] += 1
			client_path = "{$@%s}" % self._extract_client_path(node_path)
			stats["requests"] += 1
			self._report_progress(
				stats, current_uid=uid, current_path=node_path,
			)
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
				logs = payload.get("log", [])
				stats["success"] += payload.get(
					"success",
					sum(entry.get("success", 0) for entry in logs),
				)
				stats["failed"] += payload.get(
					"failed",
					sum(entry.get("failed", 0) for entry in logs),
				)
			except Exception as e:
				if self._stop_requested():
					write_line("Stop requested; stopping reindex worker")
					return True
				stats["failed"] += 1
				stats["nodes_completed"] += 1
				self._report_progress(
					stats, current_uid=uid, current_path=node_path,
				)
				write_line(f"ERROR calling REST API for uid={uid}: {e}")
				continue

			logs = payload.get("log", [])
			for entry in logs:
				objects = entry.get("objects", {})
				stats["objects"] += sum(objects.values())
			stats["nodes_completed"] += 1
			self._report_progress(
				stats, current_uid=uid, current_path=node_path,
			)

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
				return True

		return self._stop_requested()



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

def _get_status_file_path(base_url):
	return _get_lockfile_path(base_url) + ".status.json"

def _timestamp():
	return datetime.now(timezone.utc).isoformat(timespec="seconds")

def _read_status_fd(fd):
	size = os.fstat(fd).st_size
	if not size:
		return None
	os.lseek(fd, 0, os.SEEK_SET)
	data = os.read(fd, size)
	return json.loads(data.decode("utf-8"))

def _read_job_status(base_url):
	try:
		fd = os.open(_get_status_file_path(base_url), os.O_RDONLY)
	except FileNotFoundError:
		return None
	try:
		fcntl.flock(fd, fcntl.LOCK_SH)
		return _read_status_fd(fd)
	finally:
		os.close(fd)

def _update_job_status(base_url, updates, expected_job_id=None, replace=False):
	status_path = _get_status_file_path(base_url)
	fd = os.open(status_path, os.O_CREAT | os.O_RDWR, 0o600)
	try:
		fcntl.flock(fd, fcntl.LOCK_EX)
		status = {} if replace else (_read_status_fd(fd) or {})
		if expected_job_id and status.get("job_id") != expected_job_id:
			return status
		status.update(updates)
		status["updated_at"] = _timestamp()
		encoded = json.dumps(status, ensure_ascii=False).encode("utf-8")
		os.lseek(fd, 0, os.SEEK_SET)
		os.ftruncate(fd, 0)
		offset = 0
		while offset < len(encoded):
			offset += os.write(fd, encoded[offset:])
		return status
	finally:
		fcntl.flock(fd, fcntl.LOCK_UN)
		os.close(fd)

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

def _sum_expected(start_nodes):
	"""Total of expected nodes, or None if any client count is unknown."""
	counts = [node.get("expected") for node in start_nodes or []]
	if not counts or any(count is None for count in counts):
		return None
	return sum(counts)

def start(self):
	import logging
	LOGGER = logging.getLogger("Zope")

	request = self.REQUEST
	root = self.getRootElement()
	base_url = root.absolute_url()
	# Only meta_ids configured in the catalog adapter are reindexed
	catalog_adapter = root.getCatalogAdapter()
	meta_ids = self.getMetaobjManager().getTypedMetaIds(catalog_adapter.getIds())
	try:
		zmsindex_catalog = self.getZMSIndex().get_catalog()
	except Exception:
		zmsindex_catalog = None

	def count_nodes(node):
		# Expected number of nodes to reindex, taken from the ZMSIndex catalog
		if zmsindex_catalog is None:
			return None
		try:
			return len(zmsindex_catalog({
				"path": "/".join(str(part) for part in node.getPhysicalPath()),
				"meta_id": list(meta_ids),
			}))
		except Exception:
			LOGGER.exception("Unable to count nodes of %s", node.absolute_url())
			return None

	# ZMS clients selected in the sitemap, e.g. "{$portal/clientA@}"
	home_ids = request.get("home_ids", [])
	if isinstance(home_ids, str):
		home_ids = [home_ids]
	start_nodes = []
	for home_id in dict.fromkeys(home_ids):
		node = self.getLinkObj(home_id)
		if node is None or getattr(node, "meta_id", None) != "ZMS":
			LOGGER.warning("Skipping unresolvable ZMS-node %s", home_id)
			continue
		start_nodes.append({
			"home_id": home_id,
			"uid": node.get_uid(),
			"meta_id": node.meta_id,
			"getPath": "/" + "/".join(str(part) for part in node.getPhysicalPath() if part),
			"expected": count_nodes(node),
		})
	if not start_nodes:
		return "No ZMS-node selected"
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

		job_id = uuid.uuid4().hex
		initial_status = {
			"job_id": job_id,
			"state": "running",
			"started_at": _timestamp(),
			"current_uid": None,
			"current_path": None,
			"candidates": 0,
			"nodes_completed": 0,
			"requests": 0,
			"objects": 0,
			"success": 0,
			"failed": 0,
			"skipped": 0,
			"total_clients": len(start_nodes),
			"total_nodes": _sum_expected(start_nodes),
			"completed_clients": [],
			"failed_clients": [],
			"error": None,
		}
		try:
			_update_job_status(base_url, initial_status, replace=True)
		except Exception:
			_release_singleflight_lock(lock_fd, base_url)
			raise

		job = {
			"base_url": base_url,
			"job_id": job_id,
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
		stats = {}

		try:
			LOGGER.info("Starting background reindex job for %s", base_url)

			def update_progress(stats, state="running", current_uid=None,
								current_path=None):
				if state == "running" and (
					job["cancel_event"].is_set()
					or os.path.exists(cancellation_file)
				):
					state = "stopping"
				updates = dict(stats)
				updates.update({
					"state": state,
					"current_uid": current_uid,
					"current_path": current_path,
				})
				_update_job_status(
					base_url, updates, expected_job_id=job_id,
				)

			reindexer = ZMSIndexSchematizedReindexer(
				base_url=base_url,
				connector=connector,
				uid=uid,
				page_size=page_size,
				fileparsing=fileparsing,
				start_nodes=start_nodes,
				cancel_event=job["cancel_event"],
				cancellation_file=cancellation_file,
				progress_callback=update_progress,
				meta_ids=meta_ids,
			)

			stats = reindexer.run(write_line=lambda line: LOGGER.info(line))
			LOGGER.info("Finished reindex job: %s", stats)

		except Exception as error:
			LOGGER.exception("manage_reindex_content_bg failed")
			try:
				_update_job_status(
					base_url,
					{
						**stats,
						"state": "failed",
						"current_uid": None,
						"current_path": None,
						"error": str(error),
					},
					expected_job_id=job_id,
				)
			except Exception:
				LOGGER.exception("Unable to save failed reindex job status")
		finally:
			with RUN_LOCK:
				try:
					_update_job_status(
						base_url,
						{
							"finished_at": _timestamp(),
							"current_uid": None,
							"current_path": None,
						},
						expected_job_id=job_id,
					)
				except Exception:
					LOGGER.exception("Unable to save final reindex job status")
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
	try:
		thread.start()
	except Exception as error:
		try:
			_update_job_status(
				base_url,
				{
					"state": "failed",
					"finished_at": _timestamp(),
					"error": str(error),
				},
				expected_job_id=job_id,
			)
		except Exception:
			LOGGER.exception("Unable to save thread startup failure status")
		finally:
			with RUN_LOCK:
				_release_job_lock(job)
				if RUN_JOB is job:
					RUN_JOB = None
					RUN_LOCK_FD = None
					RUN_IN_PROGRESS = False
		raise
	return None # "Background Job started"

def stop(self):
	global RUN_IN_PROGRESS, RUN_LOCK_FD, RUN_JOB

	base_url = self.getRootElement().absolute_url()
	with RUN_LOCK:
		job = RUN_JOB
		if job is not None and job["base_url"] == base_url:
			job["cancel_event"].set()
			_update_job_status(
				base_url,
				{"state": "stopping"},
				expected_job_id=job["job_id"],
			)
			_release_job_lock(job)
			RUN_JOB = None
			RUN_LOCK_FD = None
			RUN_IN_PROGRESS = False
			return "Background Job stopped; the current REST request may finish"

		if _test_single_flight_locked(base_url):
			_request_cancellation(base_url)
			_update_job_status(base_url, {"state": "stopping"})
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
	if request.get("status") == "1":
		status = _read_job_status(self.getRootElement().absolute_url())
		if status is None:
			status = {
				"state": "idle",
				"candidates": 0,
				"nodes_completed": 0,
				"requests": 0,
				"objects": 0,
				"success": 0,
				"failed": 0,
				"skipped": 0,
				"total_clients": 0,
				"total_nodes": None,
				"completed_clients": [],
				"failed_clients": [],
			}
		request.response.setHeader(
			"Content-Type", "application/json; charset=utf-8",
		)
		request.response.setHeader("Cache-Control", "no-store")
		return json.dumps(status)

	message = None
	btn = request.form.get('btn')
	if btn == "BTN_START":
		message = start(self)
	elif btn == "BTN_STOP":
		message = stop(self)
	if btn in ("BTN_START", "BTN_STOP") and request.get("control") == "1":
		request.response.setHeader(
			"Content-Type", "application/json; charset=utf-8",
		)
		request.response.setHeader("Cache-Control", "no-store")
		return json.dumps({"message": message})

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
	status_url = self.absolute_url() + "/manage_reindex_content_bg?status=1"
	html.append("""
		<form class="form-horizontal card" name="form0" method="post" enctype="multipart/form-data">
			<input type="hidden" id="lang" name="lang" value="%s"/>
			<legend>Background Reindexing</legend>
			<div class="card-body">
			 	<div class="form-group zmi-form-container zms4-row mb-0">
					<div class="col-sm-12" data-label="ZMS-Nodes">
						<div class="zmi-sitemap-controls-container">
							<div class="btn-group zmi-sitemap-controls">
								<div title="Expand Object Tree (Hint: Mind System Load in Case!)"
									class="btn btn-secondary"
									onclick="return zmiExpandObjectTree(-1);">
									<i class="fas fa-plus-square"></i>
								</div>
								<div title="De-/Select All"
									onclick="zmiToggleSelectionButtonClick(this)"
									class="btn btn-secondary">
									<i class="fas fa-check-square"></i>
								</div>
								<div title="Expand/Compress Sitemap View"
									class="btn btn-secondary" id="zmi-sitemap-expand"
									onclick="$('.zmi-sitemap-container').toggleClass('full');$('#zmi-sitemap-expand i').toggleClass('fa-expand-arrows-alt fa-compress-arrows-alt')">
									<i class="fas fa-expand-arrows-alt"></i>
								</div>
							</div>
							<div class="progress">
								<div class="progress-bar progress-bar-striped"
									role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" style="width:0%%">
									<span></span>
								</div>
							</div>
						</div>
						<div class="zmi-sitemap-container">
							<div class="zmi-sitemap"><!-- .zmi-sitemap --></div>
						</div>
					</div><!-- .col-sm-10 -->
				</div><!-- .form-group -->
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
				<pre id="reindex-status" class="zmi-log d-none" role="status" data-status-url="%s" title="Reindex Status"></pre>
			</div><!-- .card-body -->
		</form>
	"""%(
			request.get('lang',self.getPrimaryLanguage()),
			standard.html_quote(connector_url),
			standard.html_quote(status_url)
		)
	)
	html.append("""
		<style>
			.zmi-sitemap li.zmi-reindex-done > a { color: var(--success, #28a745); }
			.zmi-sitemap li.zmi-reindex-done > a::after {
				content: " \\2713"; font-weight: bold;
			}
			.zmi-sitemap li.zmi-reindex-failed > a { color: var(--danger, #dc3545); }
		</style>
		<script>

		// Sitemap-Helper
		function zmiExpandObjectTree(max) {
			var fn = function() {
				var done = false;
				$(".zmi-sitemap .toggle[title='+']").each(function() {
					var $toggle = $(this);
					var $parents = $toggle.parentsUntil(".zmi-sitemap","ul");
					var $container = $($toggle.parents("li")[0]);
					var level = $parents.length - 1;
					if (level < max || -1 == max) {
						$ZMI.objectTree.toggleClick($toggle,fn);
						done = true;
					}
				});
			}
			fn();
			return false;
		}

		// Progress bar: determinate if the expected number of nodes is known
		function zmiSetProgress(status) {
			var $bar = $(".zmi-sitemap-controls-container .progress .progress-bar");
			var running = status.state === 'running' || status.state === 'stopping';
			var total = status.total_nodes;
			var done = status.nodes_completed || 0;
			$bar.removeClass('bg-primary bg-success bg-warning bg-danger');
			if (total) {
				var perc = Math.min(100, Math.round(done / total * 1000) / 10);
				if (status.state === 'completed') { perc = 100; }
				$bar.attr('aria-valuenow', perc).css('width', perc + '%')
					.find('span').text(perc + '% (' + done + ' / ' + total + ')');
			} else {
				$bar.attr('aria-valuenow', running ? 100 : 0)
					.css('width', running ? '100%' : '0%')
					.find('span').text(running ? done + ' nodes' : '');
			}
			$bar.toggleClass('progress-bar-striped progress-bar-animated', running);
			$bar.addClass(
				status.state === 'failed' ? 'bg-danger'
				: status.state === 'stopped' || status.state === 'stopping' ? 'bg-warning'
				: status.state === 'completed' ? 'bg-success' : 'bg-primary');
		}

		// Mark sitemap nodes: ZMS-nodes completed (or failed) so far
		var reindexDone = [];
		var reindexFailed = [];
		function zmiMarkReindexed() {
			$(".zmi-sitemap input[name='home_ids:list']").each(function() {
				var $li = $(this).closest("li");
				var val = $(this).val();
				$li.toggleClass("zmi-reindex-done", reindexDone.indexOf(val) >= 0);
				$li.toggleClass("zmi-reindex-failed", reindexFailed.indexOf(val) >= 0);
			});
		}

		// On Document Ready
		(function () {

			// -------------------------------
			// Initialize Sitemap
			// -------------------------------
			var href = $ZMI.get_document_element_url($ZMI.getPhysicalPath());
			$ZMI.objectTree.init('.zmi-sitemap', href, {
				params: {'meta_types':'ZMS'},
				filter: x => x.meta_id === 'ZMS',
				'init.callback': function() {
					zmiExpandObjectTree(1);
				},
				'addPages.callback': function() {
					console.log('addPages.callback')
					$(".zmi-sitemap a:not(.checkboxed)").each(function() {
						var $a = $(this);
						var phys_path = $a.attr('href');
						var href_manage = phys_path + '/manage';
						$a.addClass("checkboxed")
							.removeAttr('onclick')
							.attr('target','_blank')
							.attr('href',href_manage)
							.attr('title',href_manage);
						var uid = '{'+'$'+phys_path.substring(1).replace(/\\/content/gi,'@')+'}'; // $a.attr('data-uid');
						$a.before('<input name="home_ids:list" type="checkbox" title="'+uid+'" value="'+uid+'" checked="checked" /> ');
					});
					zmiMarkReindexed();
				},
			});

			// -------------------------------
			// Handle Status
			// -------------------------------
			const panel = document.getElementById('reindex-status');
			const statusUrl = panel.dataset.statusUrl;
			let polling = false;
			let timer = null;
			let lastMessage = '';

			async function refreshStatus() {
				if (polling) return;
				polling = true;
				try {
					const response = await fetch(statusUrl, {
						credentials: 'same-origin',
						cache: 'no-store',
						headers: {'Accept': 'application/json'}
					});
					if (!response.ok) {
						throw new Error('HTTP ' + response.status);
					}
					const status = await response.json();
					const lines = [];
					if (lastMessage) {
						lines.push(lastMessage);
					}
					lines.push(
						'State: ' + status.state,
						'ZMS-nodes completed: ' + (status.completed_clients || []).length +
							' / ' + (status.total_clients || 0),
						'Content nodes processed: ' + (status.nodes_completed || 0) +
							(status.total_nodes ? ' / ' + status.total_nodes + ' expected' : ' (total unknown)'),
						'Catalog objects collected: ' + (status.objects || 0) +
							' (one per node and language, plus file parts)',
						'Catalog objects added: ' + (status.success || 0) +
							' / failed: ' + (status.failed || 0)
					);
					zmiSetProgress(status);
					reindexDone = status.completed_clients || [];
					reindexFailed = status.failed_clients || [];
					zmiMarkReindexed();
					if (reindexDone.length) {
						lines.push('Completed ZMS-nodes:');
						reindexDone.forEach(function(id) { lines.push('  ' + id); });
					}
					if (reindexFailed.length) {
						lines.push('ZMS-nodes with errors:');
						reindexFailed.forEach(function(id) { lines.push('  ' + id); });
					}
					if (status.current_path) {
						lines.push('Current: ' + status.current_path);
					}
					if (status.current_uid) {
						lines.push('UID: ' + status.current_uid);
					}
					if (status.updated_at) {
						lines.push('Updated: ' + status.updated_at);
					}
					if (status.error) {
						lines.push('Error: ' + status.error);
					}
					panel.classList.remove('d-none');
					panel.textContent = lines.join('\\n');
					panel.className = status.state === 'failed'
						? 'zmi-log alert alert-danger'
						: status.state === 'running' || status.state === 'stopping'
							? 'zmi-log alert alert-info'
							: 'zmi-log alert alert-secondary';
					if (status.state !== 'running' && status.state !== 'stopping' && timer) {
						clearInterval(timer);
						timer = null;
					}
				} catch (error) {
					panel.textContent = 'Unable to refresh reindex status: ' + error.message;
					panel.className = 'zmi-log alert alert-warning';
				} finally {
					polling = false;
				}
			}

			function startPolling() {
				if (!timer) {
					timer = setInterval(refreshStatus, 2000);
				}
				refreshStatus();
			}

			// Submit Start/Stop in the background, so that the sitemap keeps
			// its expansion and selection (Zope reads form data from POST, not PUT)
			const form = document.forms['form0'];
			form.addEventListener('submit', async function(event) {
				event.preventDefault();
				const submitter = event.submitter;
				if (!submitter || !submitter.value) return;
				const data = new FormData(form);
				data.set('btn', submitter.value);
				data.set('control', '1');
				const buttons = form.querySelectorAll('button[name=btn]');
				buttons.forEach(b => b.disabled = true);
				try {
					const response = await fetch(form.getAttribute('action') || window.location.pathname, {
						method: 'POST',
						body: data,
						credentials: 'same-origin',
						cache: 'no-store',
						headers: {'Accept': 'application/json'}
					});
					if (!response.ok) {
						throw new Error('HTTP ' + response.status);
					}
					const result = await response.json();
					lastMessage = result.message || '';
				} catch (error) {
					lastMessage = 'Request failed: ' + error.message;
				} finally {
					buttons.forEach(b => b.disabled = false);
				}
				startPolling();
			});

			startPolling();
		})();
		</script>
	""")
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
	parser.add_argument("--meta-ids", nargs="+", help="Reindex only these meta_ids (default: all nodes)")
	args = parser.parse_args()

	reindexer = ZMSIndexSchematizedReindexer(
		base_url=args.base_url,
		connector=args.connector,
		uid=args.uid,
		page_size=args.page_size,
		fileparsing=args.fileparsing,
		meta_ids=args.meta_ids,
	)

	print("Starting reindex…")
	stats = reindexer.run(write_line=print)
	print("Summary:", stats)


if __name__ == "__main__":
	main()