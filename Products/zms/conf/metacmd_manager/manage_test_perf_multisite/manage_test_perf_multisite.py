def manage_test_perf_multisite( self):
  request = self.REQUEST
  prt = []
  prt.append('<!DOCTYPE html>')
  prt.append('<html lang="en">')
  prt.append(self.zmi_html_head(self,request))
  prt.append('<body class="%s">'%self.zmi_body_class(id=''))
  prt.append(self.zmi_body_header(self,request,options=self.customize_manage_options()))
  prt.append('<div id="zmi-tab">')
  prt.append(self.zmi_breadcrumbs(self,request,extra=[{'label':'Index','action':'manage_main'}]))
  prt.append('<form class="form-horizontal card" name="form0" method="post" enctype="multipart/form-data">')
  prt.append('<input type="hidden" name="lang" value="%s"/>'%request['lang'])
  prt.append('<legend>Test Performance Multisite</legend>')
  prt.append('<div class="card-body">')
  prt.append("""
	<div class="form-group zmi-form-container zms4-row mb-0">
		<div class="col-sm-12" data-label="ZMS-Clients">
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
    <label class="col-sm-2 control-label">URL</label>
    <div class="col-sm-10">
      <input class="form-control" id="url" name="url" type="text" value="index_ger.html" />
      <small class="form-text text-muted">manage_main / index_ger.html / etc.</small>
    </div>
  </div><!-- .form-group -->
  <div class="form-group row">
    <label class="col-sm-2 control-label">Count</label>
    <div class="col-sm-10">
      <input class="form-control" id="count" name="count:int" type="text" value="20" />
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
  """)

  prt.append('</div><!-- .card-body -->')
  prt.append('</form><!-- .form-horizontal -->')
  prt.append('</div><!-- #zmi-tab -->')
  prt.append(self.zmi_body_footer(self,request))
  prt.append('''
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
    var inputs;
    var index = 0;
             
function run() {
    const runAjax = (index) => {
        if (!started || index >= $inputs.length) {
            stop();
            return;
        }

        const $input = $($inputs[index]);
        const $a = $input.next("a");
        const messageId = "progress" + index;
        $a.after('<span class="response">&nbsp;&nbsp;<i class="fas fa-spinner fa-spin text-primary"></i>&nbsp;&nbsp;<span id="' + messageId + '"></span></span>');
        const $message = $("#" + messageId);
        const href = $a.attr('href');
        const url = $('#url').val();
        const index_html = href.substring(0, href.lastIndexOf('/')) + '/' + url;
        const count = parseInt($('#count').val());
        let total_time = 0;

        const ajaxRequest = (j) => {
            return new Promise((resolve) => {
                const t0 = performance.now();
                $.ajax({
                    url: index_html,
                    data: { ts: new Date().getTime() },
                    method: 'GET',
                    success: function () {
                        const t1 = performance.now();
                        const response_time = t1 - t0;
                        total_time += response_time;
                        const message = index + '/' + count + ': ' + response_time.toFixed(2) + ' ms';
                        $message.text(message);
                        console.log(message);
                        resolve();
                    }
                });
            });
        };

        // Execute AJAX requests sequentially for the current input
        const ajaxSequence = async () => {
            for (let j = 0; j < count; j++) {
                if (!started) return;
                await ajaxRequest(j);
            }
            const message = (total_time / count).toFixed(2) + ' ms';
            $message.text(message);
            console.log(message);
            runAjax(index + 1); // Move to the next input
        };

        ajaxSequence();
    };

    runAjax(0); // Start with the first input
}

    function start() {
        console.log('Start');
        started = true;
        $("#start-button").prop("disabled","disabled");
        $("#stop-button").prop("disabled","");
        $(".zmi-sitemap .response").remove();
        $inputs = $(".zmi-sitemap input:checked");
        index = 0;
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
  prt.append('</body>')
  prt.append('</html>')
  
  return '\n'.join(prt)