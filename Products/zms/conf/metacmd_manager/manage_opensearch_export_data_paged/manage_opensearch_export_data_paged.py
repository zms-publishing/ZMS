from Products.zms import standard
from abc import abstractmethod

# Abstract Interface for Handler
class IHandler:
    @abstractmethod
    def handle(self): raise NotImplementedError

# Implementation of Opensearch Handler
class OpensearchHandler(IHandler):
    def __init__(self, catalog_adapter, client, index, meta_ids):
       self.catalog_adapter = catalog_adapter
       self.client = client
       self.index = index
       self.meta_ids = meta_ids
    def handle(self, node):
        # Node in Meta-IDs of ZCatalog-Adapter
        if not self.meta_ids or node.meta_id in self.meta_ids:
          response = [None]
          # Callback for document
          def callback(node, document):
            response.append(self.client.index(
                index = self.index,
                body = document,
                id = node.get_uid(),
                refresh = True
            ))
          document = self.catalog_adapter.get_sitemap(callback, node, recursive=False)
          return response[-1]
        return None

# Traverse and handle nodes of this page.
def traverse(data, root_node, node, handler, page_size=100):
  count = 0
  root_path = '/'.join(root_node.getPhysicalPath())
  while node and count < page_size:
    path = '/'.join(node.getPhysicalPath())
    log = {'index':count,'path':path,'meta_id':node.meta_id}
    log['action'] = handler.handle(node);
    data['log'].append(log)
    node = node.get_next_node()
    if node and not '/'.join(node.getPhysicalPath()).startswith(root_path): node = None
    data['next_node'] = None if not node else '{$%s}'%node.get_uid()
    count += 1

# Get Opensearch Client:
#
# ${opensearch.url:https://localhost:9200}
# ${opensearch.username:admin}
# ${opensearch.password:admin}
# ${opensearch.ssl.verify:}
def get_opensearch_client(self):
  from opensearchpy import OpenSearch
  url = self.getConfProperty('opensearch.url', 'https://localhost:9200')
  username = self.getConfProperty('opensearch.username', 'admin')
  password = self.getConfProperty('opensearch.password', 'admin')
  verify = bool(self.getConfProperty('opensearch.ssl.verify', ''))
  url = url[len('https://'):]
  host = url[:url.find(':')]
  port = int(url[url.find(':')+1:])
  auth = (username, password)
  standard.writeBlock(self, "host=%s, port=%i, username=%s, password=%s"%(host,port,username,password))
  return OpenSearch(
    hosts = [{'host': host, 'port': port}],
    http_compress = True, # enables gzip compression for request bodies
    http_auth = auth,
    use_ssl = True,
    verify_certs = verify,
    ssl_assert_hostname = False,
    ssl_show_warn = False,
  ) 

def manage_opensearch_export_data_paged( self):
  request = self.REQUEST
  RESPONSE =  request.RESPONSE
  lang = self.getPrimaryLanguage()
  catalog = self.getZMSIndex().get_catalog()
  catalog_adapter = self.getCatalogAdapter()
  ids = catalog_adapter.getIds()

  # REST Endpoints  
  if request.get('json'):
    import json
    request.RESPONSE.setHeader("Content-Type","text/json")
    root_node = self.getLinkObj(request['root_node'])
    data = {'pid':self.Control_Panel.process_id(),'root_node':request['root_node']}
    # REST Endpoint: ajaxCount
    if request.get('count'):
      path = '/'.join(root_node.getPhysicalPath())
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
      opensearch_client = get_opensearch_client(self)
      root_id = self.getRootElement().getHome().id
      handler = OpensearchHandler(catalog_adapter, opensearch_client, root_id, ids)
      traverse(data,root_node,node,handler,page_size)
    return json.dumps(data)
  
  home_id = self.getHome().id
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
  prt.append('<div class="col-sm-5">')
  prt.append('<input class="form-control" id="page_size"  name="page_size:int" type="number" value="100">')
  prt.append('</div>')
  prt.append('</div><!-- .form-group -->')
  prt.append('<div class="form-group row">')
  prt.append('<label class="col-sm-2 control-label">Root</label>')
  prt.append('<div class="col-sm-5">')
  prt.append('<input class="form-control url-input" id="root_node" name="root_node" type="text" value="{$}">')
  prt.append('</div>')
  prt.append('</div><!-- .form-group -->')
  prt.append('<div class="form-group row d-none">')
  prt.append('<label class="col-sm-2 control-label">Node</label>')
  prt.append('<div class="col-sm-5">')
  prt.append('<input class="form-control url-input" id="uid" name="uid" type="text" readonly="readonly">')
  prt.append('</div>')
  prt.append('</div><!-- .form-group -->')
  prt.append('<div class="form-group row">')
  prt.append('<label class="col-sm-2 control-label"></label>')
  prt.append('<div class="col-sm-5">')
  prt.append('<button id="start-button" class="btn btn-secondary mr-2">')
  prt.append('<i class="fas fa-play text-success"></i>')
  prt.append('</button>')
  prt.append('<button id="stop-button" class="btn btn-secondary" disabled="disabled">')
  prt.append('<i class="fas fa-stop"></i>')
  prt.append('</button>')
  prt.append('</div>')
  prt.append('</div><!-- .form-group -->')
  prt.append('<div class="form-group row">')
  prt.append('<label class="col-sm-2 control-label"></label>')
  prt.append('<div class="col-sm-5">')
  prt.append('<div id="count">')
  prt.append('</div>')
  prt.append('</div>')
  prt.append('</div><!-- .form-group -->')
  prt.append('<div class="d-none progress mx-3">')
  prt.append('<div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100"></div>')
  prt.append('</div>')
  prt.append('<div class="d-none alert alert-info" role="alert">')
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
    const params = {'json':true,'count':true,'root_node':root_node};
    $.get('manage_opensearch_export_data_paged',params,function(data) {
        $('#uid').val(root_node);
        var html = '';
        html += '<table id="count_table" class="table table-bordered">';
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
        html += '<td class="count">' + 0 + '</td>';
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
    const params = {'json':true,'traverse':true,'root_node':root_node,'uid':uid,'page_size':page_size};
    $.get('manage_opensearch_export_data_paged',params,function(data) {
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