"""
ZMSZCatalogAdapterQueue.py - Background (in-process) reindexing of ZMS content.

A job traverses the selected ZMS clients and reindexes the nodes via
ZMSZCatalogConnector.reindex_nodes. The job runs in a daemon thread with its
own ZODB connection and its own transaction (one commit per page of nodes);
there is no HTTP round trip.

Control is file based (single-flight lock, status JSON, pause/stop markers in
the temp dir), so status, pause and stop work across Zope processes on one
host. The file layout and the status fields are the same as in the former
external method manage_reindex_content_bg, so existing status pollers keep
working.

License: GNU General Public License v2 or later,
Organization: ZMS Publishing
"""

# Imports.
from datetime import datetime, timezone
import fcntl
import json
import logging
import os
import tempfile
import threading
import time
import uuid

LOGGER = logging.getLogger("ZMSReindex")

DEFAULT_PAGE_SIZE = 25
CONFLICT_RETRIES = 3

# Directory of lock/status/marker files (default: temp dir).
CONTROL_DIR = None

IDLE_STATUS = {
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
  "current_client": None,
}


def _timestamp():
  return datetime.now(timezone.utc).isoformat(timespec="seconds")


################################################################################
#  File based job control
################################################################################

class JobControl:
  """Single-flight lock, status and pause/stop markers of one job key."""

  def __init__(self, key, directory=None):
    safe = "".join(ch if ch.isalnum() else "_" for ch in key)
    self.base = os.path.join(directory or CONTROL_DIR or tempfile.gettempdir(), "zms_reindex_%s.lock" % safe)
    self.lock_path = self.base
    self.guard_path = self.base + ".guard"
    self.stop_path = self.base + ".stop"
    self.pause_path = self.base + ".pause"
    self.status_path = self.base + ".status.json"
    self.stop_event = threading.Event()

  # -- markers ---------------------------------------------------------------

  def _touch(self, path):
    os.close(os.open(path, os.O_CREAT | os.O_WRONLY | os.O_TRUNC, 0o644))

  def _remove(self, path):
    try:
      os.unlink(path)
    except FileNotFoundError:
      pass

  def stop_requested(self):
    return self.stop_event.is_set() or os.path.exists(self.stop_path)

  def pause_requested(self):
    return os.path.exists(self.pause_path)

  def request_stop(self):
    self.stop_event.set()
    self._touch(self.stop_path)

  def request_pause(self):
    self._touch(self.pause_path)

  def clear_pause(self):
    self._remove(self.pause_path)

  def clear_markers(self):
    self._remove(self.stop_path)
    self._remove(self.pause_path)

  # -- single-flight lock ----------------------------------------------------

  def _acquire_guard(self):
    fd = os.open(self.guard_path, os.O_CREAT | os.O_RDWR, 0o644)
    fcntl.flock(fd, fcntl.LOCK_EX)
    return fd

  def _release_guard(self, fd):
    try:
      fcntl.flock(fd, fcntl.LOCK_UN)
    finally:
      os.close(fd)

  def try_acquire(self):
    """Return the lock fd or None if another job holds the lock."""
    guard = self._acquire_guard()
    try:
      fd = os.open(self.lock_path, os.O_CREAT | os.O_RDWR, 0o644)
      try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return fd
      except OSError:
        os.close(fd)
        return None
    finally:
      self._release_guard(guard)

  def release(self, fd):
    if fd is None:
      return
    guard = self._acquire_guard()
    try:
      fcntl.flock(fd, fcntl.LOCK_UN)
    finally:
      try:
        os.close(fd)
        self._remove(self.lock_path)
      finally:
        self._release_guard(guard)

  def is_locked(self):
    """True if a job (in any process) currently holds the lock."""
    guard = self._acquire_guard()
    try:
      try:
        fd = os.open(self.lock_path, os.O_RDWR)
      except FileNotFoundError:
        return False
      try:
        try:
          fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
          return True
        # Stale lock file of a dead job.
        fcntl.flock(fd, fcntl.LOCK_UN)
        self._remove(self.lock_path)
        return False
      finally:
        os.close(fd)
    finally:
      self._release_guard(guard)

  # -- status ----------------------------------------------------------------

  @staticmethod
  def _read_fd(fd):
    size = os.fstat(fd).st_size
    if not size:
      return None
    os.lseek(fd, 0, os.SEEK_SET)
    return json.loads(os.read(fd, size).decode("utf-8"))

  def read_status(self):
    try:
      fd = os.open(self.status_path, os.O_RDONLY)
    except FileNotFoundError:
      return None
    try:
      fcntl.flock(fd, fcntl.LOCK_SH)
      return self._read_fd(fd)
    finally:
      os.close(fd)

  def update_status(self, updates, expected_job_id=None, replace=False):
    fd = os.open(self.status_path, os.O_CREAT | os.O_RDWR, 0o600)
    try:
      fcntl.flock(fd, fcntl.LOCK_EX)
      status = {} if replace else (self._read_fd(fd) or {})
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


################################################################################
#  Traversal and run loop (independent of threads and ZODB connections)
################################################################################

def iter_nodes(start, meta_ids=None, meta_types=None):
  """
  Yield start and its descendants in document order. Other ZMS clients are not
  entered. meta_ids=None yields every node.
  """
  if meta_types is None:
    meta_types = list(start.dGlobalAttrs)

  def children(node):
    if node.meta_id == 'ZMSLinkElement' or not hasattr(node, 'objectValues'):
      return []
    return node.objectValues(meta_types)

  def indexable(node):
    return meta_ids is None or node.meta_id in meta_ids

  if indexable(start):
    yield start
  stack = [iter(children(start))]
  while stack:
    node = next(stack[-1], None)
    if node is None:
      stack.pop()
      continue
    if indexable(node):
      yield node
    stack.append(iter(children(node)))


def _new_stats(start_nodes):
  counts = [n.get("expected") for n in start_nodes]
  return {
    "candidates": 0, "requests": 0, "objects": 0, "success": 0, "failed": 0,
    "skipped": 0, "nodes_completed": 0,
    "total_clients": len(start_nodes),
    "total_nodes": None if not counts or None in counts else sum(counts),
    "completed_clients": [], "failed_clients": [], "current_client": None,
  }


def run_reindex(connector, start_nodes, control, progress=None, meta_ids=None,
                fileparsing=False, page_size=DEFAULT_PAGE_SIZE, commit=None, abort=None):
  """
  Reindex the nodes of the given clients page by page.

  start_nodes: list of dicts {home_id, expected, node} with the resolved
  client node. commit/abort finish the transaction of each page. A page that
  hits a ConflictError is retried. Returns the final stats.
  """
  commit = commit or (lambda: None)
  abort = abort or (lambda: None)
  stats = _new_stats(start_nodes)
  last = {"uid": None, "path": None}

  def report(state="running", uid=None, path=None):
    if uid:
      last["uid"], last["path"] = uid, path
    elif state == "paused":
      uid, path = last["uid"], last["path"]
    if state == "running" and control.stop_requested():
      state = "stopping"
    elif state == "running" and control.pause_requested():
      state = "pausing"
    if progress:
      progress(dict(stats), state, uid, path)

  def wait_while_paused():
    if not control.pause_requested() or control.stop_requested():
      return
    report("paused")
    while control.pause_requested() and not control.stop_requested():
      time.sleep(0.5)
    if not control.stop_requested():
      report()

  def reindex_page(page):
    from ZODB.POSException import ConflictError
    for attempt in range(CONFLICT_RETRIES + 1):
      try:
        result = connector.reindex_nodes(page, fileparsing)
        commit()
        return result
      except ConflictError:
        abort()
        if attempt == CONFLICT_RETRIES:
          raise

  def process(page):
    stats["candidates"] += len(page)
    stats["requests"] += 1
    uid = page[-1].get_uid()
    path = "/".join(page[-1].getPhysicalPath())
    report(uid=uid, path=path)
    # A failing page is retried node by node, so one bad node
    # does not fail the others.
    parts = [page]
    try:
      results = [reindex_page(page)]
    except Exception:
      abort()
      if len(page) == 1:
        LOGGER.exception("Reindex failed for %s", path)
        results = [None]
      else:
        LOGGER.warning("Reindex failed for page ending at %s, retrying node by node", path, exc_info=True)
        parts, results = [], []
        for node in page:
          parts.append([node])
          try:
            results.append(reindex_page([node]))
          except Exception:
            abort()
            LOGGER.exception("Reindex failed for %s", "/".join(node.getPhysicalPath()))
            results.append(None)
    for part, result in zip(parts, results):
      if result is None:
        stats["failed"] += len(part)
        continue
      stats["success"] += result.get("success", 0)
      stats["failed"] += result.get("failed", 0)
      stats["objects"] += sum(sum(e.get("objects", {}).values()) for e in result["log"])
    stats["nodes_completed"] += len(page)
    report(uid=uid, path=path)

  report()
  for client in start_nodes:
    wait_while_paused()
    if control.stop_requested():
      break
    stats["current_client"] = client.get("home_id")
    report()
    failed_before = stats["failed"]
    page = []
    for node in iter_nodes(client["node"], meta_ids):
      wait_while_paused()
      if control.stop_requested():
        break
      page.append(node)
      if len(page) >= page_size:
        process(page)
        page = []
        # Don't let the connection cache grow with the traversed tree.
        if hasattr(connector, "_p_jar") and connector._p_jar is not None:
          connector._p_jar.cacheGC()
    if page and not control.stop_requested():
      process(page)
    if control.stop_requested():
      break
    (stats["failed_clients"] if stats["failed"] > failed_before
      else stats["completed_clients"]).append(client.get("home_id"))
    report()
  stats["current_client"] = None
  progress and progress(dict(stats), "stopped" if control.stop_requested() else "completed", None, None)
  return stats


################################################################################
#  Job lifecycle (thread, own ZODB connection)
################################################################################

_JOBS_LOCK = threading.Lock()
_JOBS = {}


def get_status(key):
  return JobControl(key).read_status() or dict(IDLE_STATUS)


def pause(key):
  control = JobControl(key)
  with _JOBS_LOCK:
    if not control.is_locked():
      return "No background job is running"
    status = control.read_status() or {}
    state = status.get("state")
    if state in ("pausing", "paused"):
      return "Background Job is already paused"
    if state != "running":
      return "Background Job cannot be paused (state: %s)" % state
    control.request_pause()
    control.update_status({"state": "pausing"}, expected_job_id=status.get("job_id"))
    return "Pause requested; the worker pauses after its current page"


def proceed(key):
  control = JobControl(key)
  with _JOBS_LOCK:
    if not control.is_locked():
      return "No background job is running"
    status = control.read_status() or {}
    if status.get("state") not in ("pausing", "paused"):
      return "Background Job is not paused"
    control.clear_pause()
    control.update_status({"state": "running"}, expected_job_id=status.get("job_id"))
    return "Background Job proceeds"


def stop(key):
  control = JobControl(key)
  with _JOBS_LOCK:
    if not control.is_locked():
      return "No background job is running"
    control.clear_pause()
    job = _JOBS.get(key)
    if job is not None:
      job["control"].stop_event.set()
    control.request_stop()
    control.update_status({"state": "stopping"})
    return "Stop requested; the worker stops after its current page"


def _open_zodb_app(db, request_env):
  """Open an own connection and return (app, close) for the worker thread."""
  from AccessControl.SecurityManagement import newSecurityManager, noSecurityManager
  from AccessControl.SpecialUsers import nobody
  from Testing.makerequest import makerequest
  import transaction
  conn = db.open()
  app = makerequest(conn.root()["Application"])
  request = app.REQUEST
  # Restore the URL context of the originating request.
  if request_env.get("server_url"):
    request.other["SERVER_URL"] = request_env["server_url"]
  request._script[:] = request_env.get("script", [])
  if request_env.get("virtual_root_physical_path"):
    request.other["VirtualRootPhysicalPath"] = request_env["virtual_root_physical_path"]
  request._resetURLS()
  # Like the former anonymous REST calls, index what the public sees.
  request.other["AUTHENTICATED_USER"] = nobody
  newSecurityManager(request, nobody)

  def close():
    noSecurityManager()
    transaction.abort()
    conn.close()
  return app, close


def _capture_request_env(request):
  return {
    "server_url": request.other.get("SERVER_URL"),
    "script": list(getattr(request, "_script", [])),
    "virtual_root_physical_path": request.other.get("VirtualRootPhysicalPath"),
  }


def _resolve_start_nodes(context, home_ids, meta_ids):
  """Describe the selected ZMS clients (by physical path) for the worker."""
  try:
    catalog = context.getZMSIndex().get_catalog()
  except Exception:
    catalog = None
  start_nodes = []
  for home_id in dict.fromkeys(home_ids):
    node = context.getLinkObj(home_id)
    if node is None or getattr(node, "meta_id", None) != "ZMS":
      LOGGER.warning("Skipping unresolvable ZMS-node %s", home_id)
      continue
    path = node.getPhysicalPath()
    expected = None
    if catalog is not None:
      try:
        expected = len(catalog({"path": "/".join(path), "meta_id": list(meta_ids)}))
      except Exception:
        LOGGER.exception("Unable to count nodes of %s", "/".join(path))
    start_nodes.append({"home_id": home_id, "path": path, "expected": expected})
  return start_nodes


def start(context, home_ids, key=None, connector_id=None, page_size=DEFAULT_PAGE_SIZE,
          fileparsing=False, open_app=None):
  """
  Start a background reindex job for the given ZMS clients (e.g.
  "{$portal/clientA@}"). Returns None if started, otherwise a message.

  open_app: optional callable () -> (app, close), replacing the own ZODB
  connection (used by tests).
  """
  if isinstance(home_ids, str):
    home_ids = [home_ids]
  root = context.getRootElement()
  key = key or root.absolute_url()
  adapter = root.getCatalogAdapter()
  meta_ids = set(context.getMetaobjManager().getTypedMetaIds(adapter.getIds()))
  start_nodes = _resolve_start_nodes(context, home_ids or [], meta_ids)
  if not start_nodes:
    return "No ZMS-node selected"
  connectors = adapter.get_connectors()
  connector = adapter.get_connector(connector_id) if connector_id else (connectors[0] if connectors else None)
  if connector is None:
    return "No catalog connector found"
  connector_path = connector.getPhysicalPath()

  if open_app is None:
    jar = getattr(root, "_p_jar", None)
    if jar is None:
      return "Context is not stored in a ZODB"
    request_env = _capture_request_env(context.REQUEST)
    open_app = lambda: _open_zodb_app(jar.db(), request_env)

  control = JobControl(key)
  with _JOBS_LOCK:
    lock_fd = control.try_acquire()
    if lock_fd is None:
      return "Background Job is already running"
    control.clear_markers()
    job_id = uuid.uuid4().hex
    counts = [n["expected"] for n in start_nodes]
    try:
      control.update_status({
        "job_id": job_id, "state": "running", "started_at": _timestamp(),
        "current_uid": None, "current_path": None, "candidates": 0,
        "nodes_completed": 0, "requests": 0, "objects": 0, "success": 0,
        "failed": 0, "skipped": 0, "total_clients": len(start_nodes),
        "total_nodes": None if None in counts else sum(counts),
        "completed_clients": [], "failed_clients": [], "current_client": None,
        "error": None,
      }, replace=True)
    except Exception:
      control.release(lock_fd)
      raise
    job = {"key": key, "job_id": job_id, "control": control}
    _JOBS[key] = job

  def progress(stats, state, uid, path):
    updates = dict(stats)
    updates.update({"state": state, "current_uid": uid, "current_path": path})
    control.update_status(updates, expected_job_id=job_id)

  def worker():
    stats = {}
    close = None
    try:
      LOGGER.info("Starting background reindex job %s", key)
      app, close = open_app()
      import transaction
      connector_obj = app.unrestrictedTraverse(connector_path)
      nodes = [dict(n, node=app.unrestrictedTraverse(n["path"])) for n in start_nodes]
      stats = run_reindex(
        connector_obj, nodes, control, progress, meta_ids=meta_ids,
        fileparsing=fileparsing, page_size=page_size,
        commit=transaction.commit, abort=transaction.abort)
      LOGGER.info("Finished reindex job %s: %s", key, stats)
    except Exception as error:
      LOGGER.exception("Reindex job %s failed", key)
      try:
        control.update_status({
          **stats, "state": "failed", "current_uid": None, "current_path": None,
          "current_client": None, "error": str(error)}, expected_job_id=job_id)
      except Exception:
        LOGGER.exception("Unable to save failed reindex job status")
    finally:
      try:
        if close:
          close()
      except Exception:
        LOGGER.exception("Unable to close reindex job connection")
      try:
        control.update_status({
          "finished_at": _timestamp(), "current_uid": None, "current_path": None},
          expected_job_id=job_id)
      except Exception:
        LOGGER.exception("Unable to save final reindex job status")
      with _JOBS_LOCK:
        control.clear_markers()
        if _JOBS.get(key) is job:
          del _JOBS[key]
        control.release(lock_fd)

  thread = threading.Thread(target=worker, name="zms_reindex_job", daemon=True)
  job["thread"] = thread
  try:
    thread.start()
  except Exception as error:
    control.update_status({"state": "failed", "finished_at": _timestamp(), "error": str(error)}, expected_job_id=job_id)
    with _JOBS_LOCK:
      _JOBS.pop(key, None)
      control.release(lock_fd)
    raise
  return None
