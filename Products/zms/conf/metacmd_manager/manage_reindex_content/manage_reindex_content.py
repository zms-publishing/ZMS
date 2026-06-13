from Products.zms import standard

def manage_reindex_content( self, request=None):
	request = self.REQUEST
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
	html.append(self.zmi_body_header(self,request,options=self.customize_manage_options()))
	html.append('<div id="zmi-tab">')
	html.append(self.zmi_breadcrumbs(self,request,extra=[{'label':'Reindex Content','action':'manage_reindex_content'}]))
	html.append('<form class="form-horizontal card" name="form0" method="post" enctype="multipart/form-data">')
	html.append('<input type="hidden" name="lang" value="%s"/>'%request['lang'])
	html.append('<legend>Reindex Content Recursively</legend>')
	html.append('<div class="card-body">')
	html.append("""
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
					<div class="progress-bar progress-bar-striped progress-bar-animated active d-none"
						role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100">
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
			<input class="form-control" id="count" name="count:int" type="text" value="1" />
			<small class="form-text text-muted">API batch size per call (1 = one node per call)</small>
		</div>
		</div><!-- .form-group -->
		<div class="form-group row">
		<label class="col-sm-2 control-label"></label>
		<div class="col-sm-10">
			<button id="start-button" class="btn btn-secondary mr-2">
			<i class="fas fa-play text-success"></i>
			</button>
			<button id="stop-button" class="btn btn-secondary" disabled="disabled">
			<i class="fas fa-stop"></i>
			</button>
		</div>
	</div><!-- .form-group -->
	"""%standard.html_quote(connector_url))

	html.append('</div><!-- .card-body -->')
	html.append('</form><!-- .form-horizontal -->')
	html.append('</div><!-- #zmi-tab -->')
	html.append(self.zmi_body_footer(self,request))
	html.append('''
		<script>

		// //////////////////////////////////////////////////////////////////////             
		// Sitemap
		// //////////////////////////////////////////////////////////////////////             

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

		$(function() {
			// Sitemap
			var href = $ZMI.getPhysicalPath();
			$ZMI.objectTree.init('.zmi-sitemap', href, {
				params: {'meta_types':'0'},
				'init.callback': function() {
					var $currentNode = $('.zmi-sitemap a[data-uid]:last').closest('ul.zmi-page').first();
					if ($currentNode.length) {
						$('.zmi-sitemap').html($currentNode);
					}
					zmiExpandObjectTree(-1);
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
						var uid = '{'+'$'+phys_path.substring(1).replace(/\/content/gi,'@')+'}'; // $a.attr('data-uid');
						$a.before('<input name="home_ids:list" type="checkbox" title="'+uid+'" value="'+uid+'" checked="checked" /> ');
					});
				},
			});
			$('#zmsindex .zmi-sitemap-container').removeClass('loading');
		});

		// //////////////////////////////////////////////////////////////////////
		// Start / Stop Button
		// //////////////////////////////////////////////////////////////////////
			var started = false;
			var $inputs = [];

		function run() {
			const connectorUrl = $('#catalog_connector_url').val();
			if (!connectorUrl) {
				alert('No catalog connector available.');
				stop();
				return;
			}

			let pagecounter = 1;
			
			const reindexNode = async (uid, $message) => {
				if (!uid) {
					$message.text('Skipped: missing uid');
					return {success: 0, failed: 0, calls: 0, nodes: 0};
				}
				const data = await $.ajax({
					url: connectorUrl + '/reindex_page',
					method: 'GET',
					dataType: 'json',
					data: {
						'uid': uid,
						'page_size:int': 1,
						'clients:int': 0,
						'fileparsing:int': 1,
					},
				});
				const success = data.success || 0;
				const failed = data.failed || 0;
				$message.text('Catalog entries written: ' + success + ', failed: ' + failed);
				return {success: success, failed: failed, calls: 1, nodes: 1};
			};

			const runSequential = async () => {
				for (let i = 0; i < $inputs.length && started; i++) {
					const $input = $($inputs[i]);
					const uid = $input.val();
					const $a = $input.next('a');
					const messageId = 'progress' + pagecounter;
					$a.after('<span class="response"><i class="fas fa-spinner fa-spin text-primary my-2"></i><span class="message" id="' + messageId + '"></span></span>');
					const $message = $('#' + messageId);
					try {
						await reindexNode(uid, $message);
						$message.closest('.response').find('.fa-spinner').remove();
					} catch (e) {
						$message.text('Failed: ' + (e.status || '?') + ' ' + (e.statusText || 'request error'));
						$message.closest('.response').find('.fa-spinner').remove();
					}
					pagecounter++;
				}
				stop();
			};

			runSequential();
		}

			function start() {
				console.log('Start');
				started = true;
				$("#start-button").prop("disabled","disabled");
				$("#stop-button").prop("disabled","");
				$(".zmi-sitemap .response").remove();

				var checkedInputs = $(".zmi-sitemap input:checked").toArray();
				var uidToInput = {};
				$inputs = [];
				checkedInputs.forEach(function(input) {
					var uid = $(input).val();
					if (uid && !uidToInput[uid]) {
						uidToInput[uid] = true;
						$inputs.push(input);
					}
				});
				console.log('Selected nodes: ' + checkedInputs.length + ', unique selected nodes: ' + $inputs.length);

				run();
				return false;
			}

			function stop() {
				console.log('Stop');
				started = false;
				$("#start-button").prop("disabled","");
				$("#stop-button").prop("disabled","disabled");
				$(".zmi-sitemap .response .fa-spinner").remove();
				return false;
			}

			$(function() {
			$('#start-button').click(start);
			$('#stop-button').click(stop);
			});

		</script>
		''')
	
	html.append('''
		<style>
		/*<!--*/
			.zmi.manage_reindex_content .response span.message {
				overflow-y: auto;
				font-size:smaller !important;
				margin: .35rem;
				margin-bottom: 1rem;
				padding: .25em .5rem;
				border:0;
				background:none;
				color: #607D8B;
			}
			.zmi.manage_reindex_content .response span.message:before {
				content: "\\f058";
				color:#4CAF50;
				font-weight: 900;
				font-family: 'Font Awesome 5 Free';
				display:inline-block;
				margin-right:.35rem;
				font-style: normal;
				font-variant: normal;
				text-rendering: auto;
				-moz-osx-font-smoothing: grayscale;
				-webkit-font-smoothing: antialiased;
			}
		/*-->*/
		</style>
		''')
	html.append('</body>')
	html.append('</html>')

	return '\n'.join(html)