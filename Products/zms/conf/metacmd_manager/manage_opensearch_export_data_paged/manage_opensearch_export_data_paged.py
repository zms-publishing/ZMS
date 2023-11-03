from Products.zms import standard
from opensearchpy import OpenSearch
from opensearchpy.helpers import bulk
from abc import abstractmethod

def get_catalog_source(catalog_adapter, node):
  # Initialize sources.
  sources = [None]
  # Callback for node: add dict to sources
  def callback(node, d):
    sources.append(d)
  # Get sitemap for for single (recursive=False) document.
  catalog_adapter.get_sitemap(callback, node, recursive=False)
  # Return source (or None).
  return sources[-1]

# Process nodes of this page.
def traverse(data, root_node, clients, node, page_size=100):
  catalog_adapter = root_node.getCatalogAdapter()
  meta_ids = catalog_adapter.getIds()
  count = 0
  root_path = '/'.join(root_node.getPhysicalPath())
  while node and count < page_size:
    path = '/'.join(node.getPhysicalPath())
    log = {'index':count,'path':path,'meta_id':node.meta_id}
    if node.meta_id in meta_ids:
      source = get_catalog_source(catalog_adapter, node)
      if source:
        log['source'] = source
    data['log'].append(log)
    node = node.get_next_node(clients)
    if node \
      and not '/'.join(node.getPhysicalPath()).startswith(root_path) \
      and not node.meta_id == 'ZMS' and not clients:
      node = None
    data['next_node'] = None if not node else '{$%s}'%node.get_uid()
    count += 1

# Get Opensearch Client:
#
# ${opensearch.url:https://localhost:9200}
# ${opensearch.username:admin}
# ${opensearch.password:admin}
# ${opensearch.ssl.verify:}
def get_opensearch_client(self):
  url = self.getConfProperty('opensearch.url')
  if not url:
    return None
  username = self.getConfProperty('opensearch.username', 'admin')
  password = self.getConfProperty('opensearch.password', 'admin')
  verify = bool(self.getConfProperty('opensearch.ssl.verify', False))
  use_ssl = url.find('https://')>-1
  url = url.split('://')[-1]
  host = url[:url.find(':')]
  port = int(url[url.find(':')+1:])
  auth = (username, password)
  standard.writeBlock(self, "host=%s, port=%i, username=%s, password=%s"%(host,port,username,password))
  return OpenSearch(
    hosts = [{'host': host, 'port': port}],
    http_compress = True, # enables gzip compression for request bodies
    http_auth = auth,
    use_ssl = use_ssl,
    verify_certs = verify,
    ssl_assert_hostname = False,
    ssl_show_warn = False,
  ) 

def bulk_opensearch_index(self, sources):
  client = get_opensearch_client(self)
  index = self.getRootElement().getHome().id
  actions = [{"_op_type":"index", "_index":index, "_id":x['id'], "source":x} for x in sources]
  if client: 
    return bulk(client, actions)
  return 0, len(actions)


def manage_opensearch_export_data_paged( self):
  request = self.REQUEST
  catalog = self.getZMSIndex().get_catalog()
  catalog_adapter = self.getCatalogAdapter()
  ids = catalog_adapter.getIds()

  # REST Endpoints  
  if request.get('json'):
    import json
    request.RESPONSE.setHeader("Content-Type","text/json")
    root_node = self.getLinkObj(request['root_node'])
    clients = standard.pybool(request['clients'])
    data = {'pid':self.Control_Panel.process_id(),'root_node':request['root_node'],'clients':request['clients']}
    # REST Endpoint: ajaxCount
    if request.get('count'):
      path = '/'.join((root_node.aq_parent if clients else root_node).getPhysicalPath())
      data['count'] = {}
      for meta_id in ids:
        r = catalog({'meta_id':meta_id}, path={'query':path})
        data['count'][meta_id] = len(r)
      r = catalog(path={'query':path})
      data['total'] = len(r)
    # REST Endpoint: ajaxTraverse
    if request.get('traverse'):
      node = self.getLinkObj(request['uid'])
      page_size = int(request['page_size'])
      data['log'] = []
      data['next_node'] = None
      traverse(data,root_node,clients,node,page_size)
      sources = [x['source'] for x in data['log'] if x.get('source')]
      success, failed = bulk_opensearch_index(self, sources)
      data['success'] =  success
      data['failed'] = failed
    return json.dumps(data)
  
  prt = []
  prt.append('<!DOCTYPE html>')
  prt.append('<html lang="en">')
  prt.append(self.zmi_html_head(self,request))
  prt.append('<body class="%s">'%self.zmi_body_class(id='manage_zcatalog_export_data_paged'))
  prt.append(self.zmi_body_header(self,request))
  prt.append('<div id="zmi-tab">')
  prt.append(self.zmi_breadcrumbs(self,request))
  prt.append('<form class="form-horizontal card" name="form0" method="post" enctype="multipart/form-data">')
  prt.append('<input type="hidden" name="lang" value="%s"/>'%request['lang'])
  prt.append('<legend>Opensearch: Paged Data Transfer to Index</legend>')
  prt.append('<div class="card-body">')
  prt.append('<div class="form-group row">')
  prt.append('<label class="col-sm-2 control-label">Page-Size</label>')
  prt.append('<div class="col-sm-10">')
  prt.append('<input class="form-control" id="page_size"  name="page_size:int" type="number" value="100">')
  prt.append('</div>')
  prt.append('</div><!-- .form-group -->')
  prt.append('<div class="form-group row">')
  prt.append('<label class="col-sm-2 control-label">Root</label>')
  prt.append('<div class="col-sm-10">')
  prt.append('<input class="form-control url-input" id="root_node" name="root_node" type="text" value="{$}">')
  prt.append('</div>')
  prt.append('</div><!-- .form-group -->')
  prt.append('<div class="form-group row d-none">')
  prt.append('<label class="col-sm-2 control-label">Node</label>')
  prt.append('<div class="col-sm-10">')
  prt.append('<input class="form-control url-input" id="uid" name="uid" type="text" readonly="readonly">')
  prt.append('</div>')
  prt.append('</div><!-- .form-group -->')

  prt.append('<div class="form-group row" title="Under Construction">')
  prt.append('<label class="col-sm-2 control-label"><i class="fas fa-hammer fa-lg mr-2"></i> Options</label>')
  prt.append('<div class="col-sm-10">')
  if self.getPortalClients():
    prt.append('<div class="form-check form-check-inline">')
    prt.append('<input class="form-check-input" id="clients" name="clients:int" type="checkbox" value="1" checked="checked">')
    prt.append('<label class="form-check-label text-black-50">Recursive ZMS-Cients</label>')
    prt.append('</div>')
  prt.append('<div class="form-check form-check-inline">')
  prt.append('<input class="form-check-input" id="fileparsing" name="fileparsing:int" type="checkbox" value="1" checked="checked">')
  prt.append('<label class="form-check-label text-black-50">Parse Binary-Files</label>')
  prt.append('</div>')
  prt.append('</div>')
  prt.append('</div><!-- .form-group -->')

  prt.append('<div class="form-group row">')
  prt.append('<label class="col-sm-2 control-label">Start</label>')
  prt.append('<div class="col-sm-10">')
  prt.append('<button id="start-button" class="btn btn-secondary mr-2"><i class="fas fa-play text-success"></i></button>')
  prt.append('<button id="stop-button" class="btn btn-secondary" disabled="disabled"><i class="fas fa-stop"></i></button>')
  prt.append('</div>')
  prt.append('</div><!-- .form-group -->')
  prt.append('<div class="form-group row">')
  prt.append('<label class="col-sm-2 control-label"></label>')
  prt.append('<div class="col-sm-10">')
  prt.append('<div id="count">')
  prt.append('</div>')
  prt.append('</div>')
  prt.append('</div><!-- .form-group -->')
  prt.append('<div class="d-none progress">')
  prt.append('<div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100"></div>')
  prt.append('</div>')
  prt.append('<div class="d-none alert alert-info mx-0" role="alert">')
  prt.append('</div>')
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
    $(".progress .progress-bar").removeClass("bg-danger bg-warning bg-success");
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
    $(".progress .progress-bar").removeClass("bg-success bg-warning bg-success");
    $("#start-button i").removeClass("fa-pause").addClass("fa-play");
    $("#stop-button").prop("disabled","disabled");
    $(".progress .progress-bar").addClass("bg-warning");
    return false;
}

function progress() {
  const count = parseInt($("#count_table tr.Total .count").text());
  const total = parseInt($("#count_table tr.Total .total").text());
  const perc = Math.round(Math.floor(10.0*count*100/total)/10.0);
  $(".progress .progress-bar").css("width",perc+"%").attr({"aria-valuenow":perc,"title":count+"/"+total}).html(perc+"%");
}

function ajaxCount(cb) {
    const root_node = $('#root_node').val();
    const clients = $('#clients').prop('checked')?true:false;
    const params = {'json':true,'count':true,'root_node':root_node,'clients':clients};
    $.get('manage_opensearch_export_data_paged',params,function(data) {
        $('#uid').val(root_node);
        var html = '';
        html += '<table id="count_table" class="table table-sm table-bordered">';
        Object.entries(data['count']).forEach((k,v) => {
          html += '<tr class="' + k[0] + '">';
          html += '<td class="id">' + k[0] + '</td>';
          html += '<td class="total">' + k[1] + '</td>';
          html += '<td class="count">' + 0 + '</td>';
          html += '</tr>';
        });
        html += '<tr class="Total">';
        html += '<td class="id"><strong>Total</strong></td>';
        html += '<td class="total">' + data['total'] + '</td>';
        html += '<td class="count" width="100%">' + 0 + '</td>';
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
    const clients = $('#clients').prop('checked')?true:false;
    const uid = $('#uid').val();
    const page_size = $("input#page_size").val();
    const params = {'json':true,'traverse':true,'root_node':root_node,'clients':clients,'uid':uid,'page_size':page_size};
    $.get('manage_opensearch_export_data_paged',params,function(data) {
        $(".alert.alert-info").html($('<pre/>',{text:JSON.stringify(data,null,2)}))
        if (!stopped && !paused) {
          const log = data['log'];
          if (log) {
            log.filter(x => x['source']).forEach(x =>  {
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
            $(".progress .progress-bar").removeClass("bg-warning").addClass("bg-success")
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