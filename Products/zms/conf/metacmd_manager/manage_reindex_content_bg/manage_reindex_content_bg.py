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
import time
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
			cancellation_file=None, progress_callback=None, meta_ids=None,
			pause_file=None):
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
		# While this marker file exists, the run waits before the next node
		self.pause_file = pause_file
		self._last_position = (None, None)
		self.progress_callback = progress_callback
		# None: reindex every node; otherwise only nodes with these meta_ids
		self.meta_ids = None if meta_ids is None else set(meta_ids)

	def _report_progress(self, stats, state="running", current_uid=None, current_path=None):
		if state == "running" and current_uid:
			self._last_position = (current_uid, current_path)
		elif state == "paused" and not current_uid:
			current_uid, current_path = self._last_position
		if self.progress_callback is not None:
			self.progress_callback(
				stats, state=state, current_uid=current_uid,
				current_path=current_path,
			)

	def _pause_requested(self):
		return self.pause_file is not None and os.path.exists(self.pause_file)

	def _wait_while_paused(self, stats, write_line):
		if not self._pause_requested() or self._stop_requested():
			return
		write_line("Paused")
		self._report_progress(stats, state="paused")
		while self._pause_requested() and not self._stop_requested():
			time.sleep(0.5)
		if not self._stop_requested():
			write_line("Proceeding")
			self._report_progress(stats)

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
			"current_client": None,
		}
		self._report_progress(stats)

		clients = self.start_nodes if self.start_nodes else [None]
		seen = set()
		stopped = False
		for client in clients:
			self._wait_while_paused(stats, write_line)
			if self._stop_requested():
				break
			errors_before = self.traversal_errors
			failed_before = stats["failed"]
			if client is not None:
				stats["current_client"] = client.get("home_id")
				self._report_progress(stats)
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

		stats["current_client"] = None
		self._report_progress(
			stats, state="stopped" if self._stop_requested() else "completed",
			current_uid=None, current_path=None,
		)
		return stats

	def _run_client(self, client, seen, stats, write_line):
		"""Reindex one client; returns True if the run has been stopped."""
		for uid, meta_id, node_path in self._iter_client_nodes(client, seen):
			self._wait_while_paused(stats, write_line)
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

# ----------------------------------------------------------------
# 2A) ZOPE EXTERNAL-METHOD: Job control
# The job itself (in-process worker thread, lock, status, pause/stop)
# is implemented by the catalog adapter, see ZMSZCatalogAdapterQueue.
# ----------------------------------------------------------------

def _sum_expected(start_nodes):
	"""Total of expected nodes, or None if any client count is unknown."""
	counts = [node.get("expected") for node in start_nodes or []]
	if not counts or any(count is None for count in counts):
		return None
	return sum(counts)

def start(self):
	request = self.REQUEST
	home_ids = request.get("home_ids", [])
	return self.getCatalogAdapter().start_reindex_job(
		home_ids,
		connector_id=request.get("connector_id") or None,
		page_size=max(1, int(request.get("page_size", 1))),
		fileparsing=bool(request.get("fileparsing", False)),
	)

def pause(self):
	return self.getCatalogAdapter().pause_reindex_job()

def proceed(self):
	return self.getCatalogAdapter().proceed_reindex_job()

def stop(self):
	return self.getCatalogAdapter().stop_reindex_job()

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
		status = self.getCatalogAdapter().get_reindex_job_status()
		request.response.setHeader(
			"Content-Type", "application/json; charset=utf-8",
		)
		request.response.setHeader("Cache-Control", "no-store")
		return json.dumps(status)

	message = None
	btn = request.form.get('btn')
	if btn == "BTN_START":
		message = start(self)
	elif btn == "BTN_PAUSE":
		message = pause(self)
	elif btn == "BTN_PROCEED":
		message = proceed(self)
	elif btn == "BTN_STOP":
		message = stop(self)
	if btn in ("BTN_START", "BTN_PAUSE", "BTN_PROCEED", "BTN_STOP") and request.get("control") == "1":
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
						<button id="start-button" class="btn btn-secondary mr-2" name="btn" value="BTN_START" title="Start">
							<i class="fas fa-play text-success"></i>
						</button>
						<button id="stop-button" class="btn btn-secondary" name="btn" value="BTN_STOP" title="Stop" disabled="disabled">
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
			.zmi-sitemap li.zmi-reindex-done > a { 
				color: var(--success, #28a745); 
			}
			.zmi-sitemap li.zmi-reindex-done > a::after,
			.zmi-sitemap li.zmi-reindex-running > a::after {
				content: "\\f058";
				font-weight: bold;
				font-weight: 900;
				font-family: 'Font Awesome 5 Free';
				display: inline-block;
				margin-left: .35rem;
				font-style: normal;
				font-variant: normal;
				text-rendering: auto;
				-moz-osx-font-smoothing: grayscale;
				-webkit-font-smoothing: antialiased;
				line-height:16px;
			}
			.zmi-sitemap li.zmi-reindex-failed > a { 
				color: var(--danger, #dc3545); 
			}
			.zmi-sitemap li.zmi-reindex-running > a::after {
				content: "\\f110";
				animation: spin 2s linear infinite;
			}
			@keyframes spin {
				0% { transform: rotate(0deg); }
				100% { transform: rotate(360deg); }
			}
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
			var running = status.state === 'running' || status.state === 'stopping' || status.state === 'pausing';
			var paused = status.state === 'paused';
			var total = status.total_nodes;
			var done = status.nodes_completed || 0;
			$bar.removeClass('bg-primary bg-success bg-warning bg-danger');
			if (total) {
				var perc = Math.min(100, Math.round(done / total * 1000) / 10);
				if (status.state === 'completed') { perc = 100; }
				$bar.attr('aria-valuenow', perc).css('width', perc + '%')
					.find('span').text(perc + '% (' + done + ' / ' + total + ')');
			} else {
				$bar.attr('aria-valuenow', running || paused ? 100 : 0)
					.css('width', running || paused ? '100%' : '0%')
					.find('span').text(running || paused ? done + ' nodes' : '');
			}
			$bar.toggleClass('progress-bar-striped', running || paused)
				.toggleClass('progress-bar-animated', running);
			$bar.addClass(
				status.state === 'failed' ? 'bg-danger'
				: status.state === 'stopped' || status.state === 'stopping' || status.state === 'pausing' || paused ? 'bg-warning'
				: status.state === 'completed' ? 'bg-success' : 'bg-primary');
		}

		// Mark sitemap nodes: ZMS-nodes completed (or failed) so far
		var reindexDone = [];
		var reindexFailed = [];
		var reindexRunning = null;
		function zmiMarkReindexed() {
			$(".zmi-sitemap input[name='home_ids:list']").each(function() {
				var $li = $(this).closest("li");
				var val = $(this).val();
				$li.toggleClass("zmi-reindex-done", reindexDone.indexOf(val) >= 0);
				$li.toggleClass("zmi-reindex-failed", reindexFailed.indexOf(val) >= 0);
				$li.toggleClass("zmi-reindex-running", reindexRunning !== null && reindexRunning === val);
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

			// Controller: encapsulates the Start / Pause / Proceed / Stop interactions.
			// The button behind #start-button depends on the job state reported by the server.
			const Controller = () => {
				const ACTIVE = ['running', 'pausing', 'paused', 'stopping'];
				const that = {
					state: 'idle',
					isActive: () => ACTIVE.indexOf(that.state) >= 0,
					// Command (btn value) issued by the start button in the current state
					command: () => {
						if (that.state === 'running') return 'BTN_PAUSE';
						if (that.state === 'pausing' || that.state === 'paused') return 'BTN_PROCEED';
						return 'BTN_START';
					},
					render: (state) => {
						that.state = state || 'idle';
						const $icon = $('#start-button i');
						const showPause = that.state === 'running';
						$icon.toggleClass('fa-pause text-info', showPause)
							.toggleClass('fa-play text-success', !showPause);
						$('#start-button')
							.attr('title', {BTN_PAUSE: 'Pause', BTN_PROCEED: 'Proceed', BTN_START: 'Start'}[that.command()])
							.prop('disabled', that.state === 'stopping');
						$('#stop-button')
							.toggleClass('text-danger', that.isActive())
							.prop('disabled', !that.isActive() || that.state === 'stopping');
					}
				};
				return that;
			};
			const controller = Controller();
			controller.render('idle');

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
					controller.render(status.state);
					reindexRunning = controller.isActive()
						? (status.current_client || null) : null;
					zmiMarkReindexed();
					if (reindexRunning) {
						lines.push('Running ZMS-node: ' + reindexRunning);
					}
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
						: status.state === 'paused' || status.state === 'pausing'
							? 'zmi-log alert alert-warning'
							: controller.isActive()
								? 'zmi-log alert alert-info'
								: 'zmi-log alert alert-secondary';
					if (!controller.isActive() && timer) {
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
				const command = submitter.id === 'start-button' ? controller.command() : submitter.value;
				const data = new FormData(form);
				data.set('btn', command);
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
					controller.render(controller.state);
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