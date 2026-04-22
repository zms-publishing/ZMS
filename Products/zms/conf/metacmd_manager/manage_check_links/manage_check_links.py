import Products.zms.standard as standard
import re

def manage_check_links( self):
  request = self.REQUEST
  html = ''
  html += '<!DOCTYPE html>'
  html += '<html lang="en">'
  html += self.zmi_html_head(self,request)
  html += '<body class="%s">'%(' '.join(['zmi',request.get('manage_lang', 'eng'),'transition',self.meta_id]))
  html += self.zmi_body_header(self,request,options=[{'action':'manage_check_links','label':'Check links...'}])
  html += '<div id="zmi-tab">'
  html += self.zmi_breadcrumbs(self,request)
  html += '<form id="form" class="card form-horizontal" method="post" enctype="multipart/form-data">'
  html += '<input type="hidden" name="form_id" value="manage_check_links"/>'
  html += '<input type="hidden" name="lang" value="%s"/>'%request.get('manage_lang', 'eng')
  html += '<legend class="card-header row mb-3">Check links...</legend>'
  html += '<div class="col-sm-12">'
  html += '<div class="form-group form-inline">'
  html += '<button class="btn btn-primary" value="Start" name="btn" type="submit">Start</button>'

  manage_lang = request.get('manage_lang', 'eng')
  manage_lang = manage_lang in ['ger', 'eng'] and manage_lang or 'eng'
  options_dict = {
      'all': {
          'ger': 'Alle',
          'eng': 'All'
      },
      'missing': {
          'ger': 'Defekt',
          'eng': 'Missing'
      },
      'inactive': {
          'ger': 'Inaktiv',
          'eng': 'Inactive'
      },
      'trashcan': {
          'ger': 'Papierkorb',
          'eng': 'Trashcan'
      }
  }
  for opt in options_dict.keys():
    html += f'''<div class="radio btn btn-default btn-secondary">
        <label>
          <input type="radio" name="check_links_option" value="{opt}" {['','checked="checked" '][int(opt == request.get('check_links_option',''))]}>
          &nbsp;{options_dict[opt][manage_lang]}
          </label>
        </div>'''

  html += '</div><!-- .form-group -->'
  html += '</div><!-- .col-sm-12 -->'

  # id = 'zcatalog_index'
  # catalog = getattr(self,id,None)

  def find_node(base,path):
    ref = base
    for id in path.split('/'):
      if id == '..':
        parent = ref.getParentNode()
        if parent is not None:
          ref = ref.getParentNode()
      elif id not in ['','.'] and id.find('.')<0:
        if id.startswith('#'):
          id = id[1:]
        childNode = getattr(ref,id,None)
        if childNode is None and self.getConfProperty( 'ZMS.pathhandler', 0) != 0:
          for o in list(filter(lambda x:x.meta_type not in ['External Method'],ref.getChildNodes())):
            for l in o.getLanguages():
              r = {'lang':l}
              try:
                if o.getDeclId(r)==id:
                  childNode = o
              except:
                pass
              if childNode is not None:
                break
            if childNode is not None:
              break
        ref = childNode
        if ref is None:
          break
    return ref
  
  def assembleRow(l,ref,old):
    if ref is not None:
      inactive = not ref.isActive(request)
      trashcan = self.getTrashcan().isAncestor(ref)
      if (not 'missing' == request.get('check_links_option','')) and \
        (inactive or not 'inactive' == request.get('check_links_option','')) and \
        (trashcan or not 'trashcan' == request.get('check_links_option','')):
        l.append('<span class="alert-success'+['',' inactive'][int(inactive)]+['',' trashcan'][int(trashcan)]+'">'+old+'</span> <i class="fas fa-arrow-right mx-2"></i> '+ref.zmi_breadcrumbs_obj_path(ref,request))
          
    else:
      if (not 'inactive' == request.get('check_links_option','')) and \
        (not 'trashcan' == request.get('check_links_option','')):
        l.append('<span class="alert-danger missing">'+old+'</span>')
  
  def handleInline(node,v): 
    l = []
    p = '<a(.*?)>(.*?)<\\/a>'
    r = re.compile(p)
    for f in r.findall(v):
      internal = False
      ref = None
      d = dict(re.findall('\\s(.*?)="(.*?)"',f[0]))
      if d.get('data-id',None)!=None:
        data_id = d['data-id']
        ref = node.getLinkObj(data_id)
        internal = True
      if ref is None and d.get('href',None)!=None:
        href = d['href']
        href = re.sub('http://localhost:(\\d)*/','',href)
        for prefix in [request['SERVER_URL'],self.getConfProperty('ASP.ip_or_domain','?')]:
          if href.startswith(prefix):
            href = href[len(prefix):]
        if href.startswith('.') or href.startswith('/'):
          ref = find_node(node,href)
          internal = True
      if internal:
        old = (p.replace('\\','').replace('(.*?)','%s'))%tuple(f)
        assembleRow(l,ref,old)
    return l
  
  def handleUrl(node,v):
    l = []
    ref = None
    if v.startswith('{$') and v.endswith('}'):
      if not (v.startswith('{$__') and v.endswith('__}')) \
         and not (v.startswith('{$') and v.find('id:')>0 and v.endswith('}')):
        ref = find_node(node,v[2:-1].replace('@','/content/'))
      elif v.startswith('{$') and v.find('id:')>0 and v.endswith('}'):
        data_id = v
        ref = node.getLinkObj(data_id)
      old = v
      assembleRow(l,ref,old)
    return l

  def visit(node, html=[]):
    try:
      if node.meta_id!='ZMSLinkElement' and node.getType()=='ZMSRecordSet':
        objAttrs = node.getMetaobjAttrs(node.meta_id)
        key = list(filter(lambda x:x['type']=='list',objAttrs))[0]['id']
      else:
        th = False
        for key in list(filter(lambda x:not x.startswith('manage'),node.getObjAttrs().keys())):
          objAttr = node.getObjAttr(key)
          datatype = objAttr['datatype']
          if datatype in ['richtext','string','text','url']:
            v = node.getObjAttrValue(objAttr,request)
            if v is not None:
              v = str(v)
              o = v
              l2 = []
              if datatype in ['richtext','string','text']:
                l2.extend(handleInline(node,v))
              elif datatype in ['url']:
                l2.extend(handleUrl(node,v))
              if l2:
                if not th:
                  html.append(''
                    + '<tr>'
                    + '<th colspan="2" class="checklinks_path">%s</td>'%(node.zmi_breadcrumbs_obj_path(node,request))
                    + '</tr>')
                  th = True
                for i2 in l2:
                  html.append(''
                    + '<tr>'
                    + '<td class="checklinks_name"><code>%s</code> <strong>%s</strong></td>'%(datatype,key)
                    + '<td class="checklinks_link"><div>%s</div></td>'%i2
                    + '</tr>')
    except:
      html.append(standard.writeError(node,"can't visit"))
    for childNode in node.getChildNodes():
      visit(childNode,html)

  html += """
    <style>
      #zmi-tab #form .btn {
        margin-right:1em;
      }
      #zmi-tab #form .btn label {
        cursor: pointer;
      }
      .zmi ul.breadcrumb li {
        white-space: initial;
      }
      table.checklinks td, 
      table.checklinks th {
        border: 1px solid #9393933d;
      }
      th.checklinks_path, 
      th.checklinks_path * {
        background: #40617e;
        color: #ddd !important;
        padding: 0.1em !important;
      }
      th.checklinks_path {
        white-space: normal;
      }
      th.checklinks_path .breadcrumb {
        max-width: calc( 100vw - 100px);
        text-overflow: ellipsis;
        overflow: hidden;
        padding: 0;
      }
      th.checklinks_path .breadcrumb>li+li:before {
        padding: 0 0 0 6px;
        color: #f5f5f5;
      }
      th.checklinks_path .breadcrumb li.active a {
        font-weight: bold;
        color: white !important;
      }
      table.checklinks .checklinks_name {
        width: 200px !important;
        background: #eaedef;
      }
      table.checklinks .checklinks_name code {
        background: #333;
        color: white;
        padding: 2px 4px;
        border-radius: 4px;
      }
      table.checklinks td.checklinks_name,
      table.checklinks td.checklinks_link,
      table.checklinks th.checklinks_path,
      table.checklinks ul.breadcrumb {
        font-weight: normal;
        font-size: 12px;
        padding: 8px;
      }
      table.checklinks ul.breadcrumb {
        padding: 0;
        margin: 0;
        white-space: nowrap;
      }
      table.checklinks {
        white-space: nowrap;
      }
      td.checklinks_link>div {
        display: flex;
      }
      td.checklinks_link>div>span {
        background-color: unset;
      }
      td.checklinks_link>div>span.inactive,
      td.checklinks_link>div>span.trashcan,
      td.checklinks_link:has(span.inactive),
      td.checklinks_link:has(span.trashcan) {
        color: #666!important;
        background-color: #EEE!important;
      }
      td.checklinks_link:has(span.alert-danger) {
        background-color:#f8d7da;
        color: #843534!important;
      }
      table.checklinks .alert-success + ul.breadcrumb {
        background-color: #dff0d8;
      }
      table.checklinks .alert-success.inactive + ul.breadcrumb {
        background-color: #eee;
      }
      td.checklinks_link .alert-success + ul.breadcrumb a {
        color: #3c763d;
      }
      td.checklinks_link .alert-success.inactive + ul.breadcrumb a {
        color: #666;
      }
      .loader-wrapper {
        width: 100%;
        height: 100%;
        position: absolute;
        top: 0;
        left: 0;
        background-color: #40617e;
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 10;
        opacity: 0.8;
      }
      .loader {
        display: inline-block;
        width: 40px;
        height: 40px;
        border: 4px solid rgba(255, 255, 255, 0.35);
        border-top-color: #fff;
        border-left-color: #fff;
        border-radius: 50%;
        animation: spinner-rotate 0.85s linear infinite;
      }
      @keyframes spinner-rotate {
        100% { transform: rotate(360deg); }
      }
    </style>
    <table class="table checklinks table-sm">
    <tr>
      <th class="checklinks_name">Type</th>
      <th class="checklinks_link">Link</th>
    </tr>
  """

  l = []
  if request.form.get('btn', None) == 'Start' and (
    'missing' == request.get('check_links_option','') or
    'inactive' == request.get('check_links_option','') or
    'trashcan' == request.get('check_links_option','') or
    'all' == request.get('check_links_option','')):
    visit(self.getTrashcan(),l)
    visit(self,l)
  if len(l)==0:
    l.append('<tr><td class="checklinks_name">&mdash;</td><td class="checklinks_link">&mdash;</td></tr>')
  html += '\n'.join(l)
  html += '</table><!-- .table -->'

  html += '</form><!-- .form-horizontal -->'
  html += '</div><!-- #zmi-tab -->'
  html += self.zmi_body_footer(self,request)
  html += """
    <div class="loader-wrapper">
      <span class="loader"></span>
    </div>
    <script>
      // https://redstapler.co/add-loading-animation-to-website/
      // https://codepen.io/tashfene/pen/raEqrJ
      $(window).on("load", function() {
        $(".loader-wrapper").fadeOut("slow");
      });
      $(document).ready(function() {
        $(".loader-wrapper").fadeOut("slow");
        $("#form").submit(function() {
          $.ajax({
            method: "POST",
            url: "manage_check_links",
            dataType: "html",
            beforeSend: function() {
              $(".loader-wrapper").show();
            }
          });
        });
        $("#form .btn.radio").on("click", function() {
          $(this).find("input[type='radio']").prop("checked", true);
          $("#form button[type='submit']").click();
        });
      });
    </script>
  """
  html += '</body>'
  html += '</html>'

  return html