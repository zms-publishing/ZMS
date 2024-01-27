from Products.zms import standard

def reindex_page(self, uid, zmsindex, catalog, page_size=100, regenerate_duplicates=False):
  log = []
  nodes, next_node = self.get_next_page(uid, page_size, clients=True) 
  for node in nodes:
    log.append({'index':nodes.index(node),
      'path':'/'.join(node.getPhysicalPath()),
      'meta_id':node.meta_id,
      'action':zmsindex.reindex_node(node, catalog, regenerate_duplicates)})
  return {'log':log, 'next_node':next_node}

def manage_zmsindex_reindex( self):
  self = self.getZMSIndex()
  request = self.REQUEST
  RESPONSE = request.RESPONSE
  zmsindex = self.getZMSIndex()

  # REST Endpoints  
  if request.get('json'):
    import json
    root_node = self.getLinkObj(request['root_node'])
    result = {}
    # REST Endpoint: ajaxCount
    if request.get('count'):
      path = '/'.join((root_node.aq_parent).getPhysicalPath())
      catalog = zmsindex.get_catalog()
      r = catalog(path={'query':path})
      result['count'] = {}
      ## for i in r:
      ##    meta_id = i['meta_id']
      ##    result['count'][meta_id] += 1
      result['total'] = len(r)
    # REST Endpoint: ajaxTraverse
    if request.get('traverse'):
      uid = request['uid']
      catalog = zmsindex.get_catalog(uid == '{$}')
      page_size = int(request['page_size'])
      regenerate_duplicates = standard.pybool(request['regenerate_duplicates'])
      result = reindex_page(self, uid, zmsindex, catalog, page_size, regenerate_duplicates)
    RESPONSE.setHeader('Cache-Control', 'no-cache')
    RESPONSE.setHeader('Content-Type', 'application/json; charset=utf-8')
    return json.dumps(result,indent=2)
  
  prt = []
  prt.append('<!DOCTYPE html>')
  prt.append('<html lang="en">')
  prt.append(self.zmi_html_head(self,request))
  prt.append('<body class="%s">'%self.zmi_body_class(id='zmsindex config reindex paged'))
  prt.append(self.zmi_body_header(self,request,options=self.customize_manage_options()))
  prt.append('<div id="zmi-tab">')
  prt.append(self.zmi_breadcrumbs(self,request,extra=[{'label':'Index','action':'manage_main'}]))
  prt.append('<form class="form-horizontal card" name="form0" method="post" enctype="multipart/form-data">')
  prt.append('<input type="hidden" name="lang" value="%s"/>'%request['lang'])
  prt.append('<legend>ZMSIndex: Incremental Re-Indexing</legend>')
  prt.append('<div class="card-body">')
  prt.append("""
    <div class="form-group row">
      <label for="page_size" class="col-sm-2 control-label" title="Page Size" >Increment Size</label>
      <div class="col-sm-10">
        <input class="form-control" id="page_size" name="page_size:int" type="number" value="100" />
      </div>
    </div><!-- .form-group -->
    <div class="form-group row">
      <label for="root_node" class="col-sm-2 control-label">Root</label>
      <div class="col-sm-10">
        <input class="form-control url-input" id="root_node" name="root_node" type="text" value="{$}" />
      </div>
    </div><!-- .form-group -->
    """)

  if self.getPortalClients():
    prt.append("""
      <div class="form-group row">
        <label class="col-sm-2 control-label">Traversing</label>
        <div class="col-sm-10">
          <input class="btn btn-secondary mr-2" id="clients" name="clients:int" type="checkbox" value="1" checked="checked" />
          All Clients
        </div>
      </div><!-- .form-group -->
      """)

  prt.append("""
    <div class="form-group row mb-4">
      <label class="col-sm-2 control-label">UID-Handling</label>
      <div class="col-sm-10">
        <input class="btn btn-secondary mr-2" id="regenerate_duplicates" name="regenerate_duplicates" type="checkbox" value="1" checked="0"
          onclick="if( $('#regenerate_duplicates').prop('checked') ){ $('#regenerate_duplicates').prop('checked', false) } else { $('#regenerate_duplicates').prop('checked', true) }"/>
        Regenerate UID Doublicates
      </div>
    </div><!-- .form-group -->
    <div class="form-group row d-none">
      <label class="col-sm-2 control-label">Node</label>
      <div class="col-sm-10">
        <input class="form-control url-input" id="uid" name="uid" type="text" readonly="readonly" />
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
    <div class="form-group row">
      <label class="col-sm-2 control-label"></label>
      <div class="col-sm-10">
        <div id="count"></div>
      </div>
    </div><!-- .form-group -->
    <div class="d-none progress">
      <div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100"></div>
    </div>
    <div class="d-none alert alert-info mx-0" role="alert"></div>
    """)

  prt.append('</div><!-- .card-body -->')
  prt.append('</form><!-- .form-horizontal -->')
  prt.append('</div><!-- #zmi-tab -->')
  prt.append(self.zmi_body_footer(self,request))
  prt.append('''
    <style>
      @media (prefers-reduced-motion: reduce) {
        .progress-bar-animated {
          -webkit-animation: 1s linear infinite progress-bar-stripes;
          animation: 1s linear infinite width;
        }
        .progress-bar {
          transition: width .6s ease;
        }
      }
    </style>
    <script>
    var map = undefined;
    var started = false;
    var paused = false;
    var stopped = false;

    function start() {
        stopped = false;
        $(".progress .progress-bar").addClass("progress-bar-striped").removeClass("bg-danger bg-warning bg-success");
        $("#stop-button").prop("disabled","");
        $(".progress.d-none").removeClass("d-none");
        $(".alert.alert-info").removeClass("d-none");
        $(".alert.alert-info").html('<div class="spinner-border text-primary mx-auto" role="status"><span class="sr-only">Loading...</span></div>');
        if (!started) {
          // prepare counters
          map = {};
          $("#count_table tr td.id").each(function() {
            map[$(this).text()] = 0;
          });
          started = true;
          paused = false;
          $("#start-button i").removeClass("fa-play text-success").addClass("fa-pause text-info");
          ajaxCount(ajaxTraverse);
        }
        else if (!paused) {
          paused = true;
          $("#start-button i").removeClass("fa-pause text-info").addClass("fa-play text-success");
          $(".progress .progress-bar").addClass("bg-warning");
        }
        else {
          paused = false;
          $("#start-button i").removeClass("fa-play text-success").addClass("fa-pause text-info");
          ajaxTraverse();
        }
        return false;
    }

    function stop() {
        started = false;
        stopped = true;
        $(".progress .progress-bar").removeClass("bg-success bg-warning");
        $("#start-button i").removeClass("fa-pause").addClass("fa-play");
        $("#stop-button").prop("disabled","disabled");
        $(".progress .progress-bar").addClass("bg-warning");
        return false;
    }

    function progress() {
      const count = parseInt($("#count_table tr.Total .count").text());
      const total = parseInt($("#count_table tr.Total .total").text());
      let perc = Math.round(Math.floor(10.0*count*100/total)/10.0);
      perc = (perc > 100) ? 100 : perc;
      $(".progress .progress-bar").css("width",perc+"%").attr({"aria-valuenow":perc,"title":count+"/"+total}).html(perc+"%");
    }

    function ajaxCount(cb) {
        const root_node = $('#root_node').val();
        const params = {'json':true,'count':true,'root_node':root_node};
        $.get('manage_zmsindex_reindex',params,function(data) {
            $('#uid').val(root_node);
            var html = '';
            html += '<table id="count_table" class="table table-bordered">';
            Object.entries(data['count']).forEach((k,v) => {
              html += '<tr class="' + k[0] + '">';
              html += '<td class="id">' + k[0] + '</td>';
              html += '<td class="total">' + k[1] + '</td>';
              html += '<td class="count w-100">' + 0 + '</td>';
              html += '</tr>';
            });
            html += '<tr class="Total">';
            html += '<td class="id"><strong>Total</strong></td>';
            html += '<td class="total">' + data['total'] + '</td>';
            html += '<td class="count w-100">' + 0 + '</td>';
            html += '</tr>';
            html += '</table>';
            $("#count").html(html);
            // show progress
            progress();
            // execute callback
            cb(uid);
        });
    }

    function ajaxTraverse() {
        const root_node = $('#root_node').val();
        const uid = $('#uid').val();
        const page_size = $("input#page_size").val();
        const regenerate_duplicates = $('#regenerate_duplicates').prop('checked')?true:false;
        const params = {'json':true,'traverse':true,'root_node':root_node,'uid':uid,'page_size':page_size,'regenerate_duplicates':regenerate_duplicates};
        $.get('manage_zmsindex_reindex',params,function(data) {
            $(".alert.alert-info").html($('<pre/>',{text:JSON.stringify(data,null,2)}))
            if (!stopped && !paused) {
              const log = data['log'];
              if (log) {
                log.filter(x => x['action']).forEach(x =>  {
                  // increase counter
                  const meta_id = x['meta_id'];
                  map[meta_id] = map[meta_id] + 1;
                  $("#count_table tr." + meta_id + " .count").html(map[meta_id]);
                });
                // absolute total
                map['Total'] = map['Total'] + log.length;
                $("#count_table tr." + 'Total' + " .count").html(map['Total']);
                // show progress
                progress();
              }
              const next_node = data['next_node'];
              if (next_node) {
                $('#uid').val(next_node);
                ajaxTraverse();
              }
              else {
                stop();
                $(".progress .progress-bar").removeClass("bg-warning progress-bar-striped").addClass("bg-success")
              }
            }
        })
        .fail(function(e) {
          stop();
          alert(JSON.stringify(e));
        });
    }

    $(function() {
      $('#start-button').click(start);
      $('#stop-button').click(stop);
      $('#root_node').change( function() {
        // Hide progress/log infos
        $('.progress').addClass('d-none');
        $('.progress .progress-bar').css("width",0);
        $('.alert.alert-info').addClass('d-none').empty();
        $("#count").html('<div class="spinner-border text-primary mx-auto" role="status"><span class="sr-only">Loading...</span></div>');
        // Show object classes table
        ajaxCount(stop);
      }).change();
    });
    </script>
  ''')
  prt.append('</body>')
  prt.append('</html>')
  
  return '\n'.join(prt)