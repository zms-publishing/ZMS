from Products.zms import standard

def manage_tab_ZMSIndexZCatalog( self):
  request = self.REQUEST
  RESPONSE =  request.RESPONSE
  btn = request.form.get('btn')
  catalog = self.zcatalog_index
  
  prt = []
  prt.append('<!DOCTYPE html>')
  prt.append('<html lang="en">')
  prt.append(self.zmi_html_head(self,request))
  prt.append('<body class="%s">'%self.zmi_body_class(id='tab_ZMSIndexZCatalog'))
  prt.append(self.zmi_body_header(self,request))
  prt.append('<div id="zmi-tab">')
  prt.append(self.zmi_breadcrumbs(self,request))
  prt.append('<form class="form-horizontal card" method="post" enctype="multipart/form-data">')
  prt.append('<input type="hidden" name="lang" value="%s"/>'%request['lang'])
  prt.append('<legend>ZMSIndexZCatalog</legend>')
  prt.append('<div class="card-body">')
  
  uid = request.form.get('uid','')
  prt.append('<div class="form-group zms4-row">')
  prt.append('<label class="col-sm-2 control-label">UID</label>')
  prt.append('<div class="col-sm-5">')
  prt.append('<div class="input-group" title="SEARCH for a given uid and show the index details.">')
  prt.append('<input class="form-control" type="text" name="uid" value="%s" placeholder="Enter uid: xxx-yyy-zzz"/>'%uid)
  prt.append('<div class="input-group-append input-group-btn">')
  prt.append('<button class="btn btn-primary" name="btn" value="search">')
  prt.append('<i class="icon-search fas fa-search"></i>')
  prt.append('</button>')
  prt.append('</div>')
  prt.append('</div><!-- .input-group -->')
  prt.append('</div>')
  prt.append('</div><!-- .form-group -->')
  if uid:
    if uid.startswith('{$') and uid.endswith('}'):
      uid = uid[2:-1]
    q = catalog({'get_uid':uid})
    prt.append('<div class="form-group zms4-row" tal:condition="uid">')
    prt.append('<label class="col-sm-2 control-label">&nbsp;</label>')
    prt.append('<div class="col-sm-10">')
    prt.append('<strong>%s: %i</strong>'%(self.getZMILangStr('SEARCH_RETURNEDRESULTS'),len(q)))
    prt.append('<ul>')
    for r in q:
      prt.append('<li><a href="%s/manage" target="_blank">%s</a></li>'%(r['getPath'],r['getPath']))
    prt.append('</ul>')
    prt.append('</div>')
    prt.append('</div>')
  
  path = request.form.get('path','')
  prt.append('<div class="form-group zms4-row">')
  prt.append('<label class="col-sm-2 control-label">Path</label>')
  prt.append('<div class="col-sm-5">')
  prt.append('<div class="input-group">')
  prt.append('<input class="form-control" type="text" name="path" value="%s" placeholder="Enter path /xxx/yyy/zzz"/>'%path)
  prt.append('<div class="input-group-append input-group-btn">')
  prt.append('<button class="btn btn-primary" name="btn" value="search" title="SEARCH for a given path and show the index details.">')
  prt.append('<i class="icon-search fas fa-search"></i>')
  prt.append('</button>')
  prt.append('<button class="btn btn-danger" name="btn" value="uncatalog" title="DELETE all items from index for a given path.">')
  prt.append('<i class="icon-search fas fa-times"></i>')
  prt.append('</button>')
  prt.append('</div>')
  prt.append('</div><!-- .input-group -->')
  prt.append('</div>')
  prt.append('</div><!-- .form-group -->')
  if path:
    q = catalog({'path':path})
    prt.append('<div class="form-group zms4-row" tal:condition="uid">')
    prt.append('<label class="col-sm-2 control-label">&nbsp;</label>')
    prt.append('<div class="col-sm-10">')
    if btn == 'uncatalog':
      prt.append('<strong>%s</strong>'%(self.getZMILangStr('MSG_DELETED')%len(q)))
    else:
      prt.append('<strong>%s: %i</strong>'%(self.getZMILangStr('SEARCH_RETURNEDRESULTS'),len(q)))
    prt.append('<ol>')
    for r in q:
      if btn == 'uncatalog':
        catalog.uncatalog_object(r['getPath'])
        prt.append('<li class="uncataloged">')
      else:
        prt.append('<li class="cataloged">')
      prt.append('<a href="%s/manage" target="_blank">%s</a>'%(r['getPath'],r['getPath']))
      prt.append('</li>')

    prt.append('</ul>')
    prt.append('</div>')
    prt.append('</div>')
  
  prt.append('</div><!-- .card-body -->')
  prt.append('</form><!-- .form-horizontal -->')
  prt.append('</div><!-- #zmi-tab -->')
  prt.append(self.zmi_body_footer(self,request))
  prt.append('''
    <style>
    li.uncataloged a:before,
    li.cataloged a:before {
      font-family: 'Font Awesome 5 Free';
      font-weight: 900;
      -moz-osx-font-smoothing: grayscale;
      -webkit-font-smoothing: antialiased;
      display: inline-block;
      font-style: normal;
      font-variant: normal;
      text-rendering: auto;
      line-height: 1;
      margin-right: .25rem;
    }
    li.cataloged a:before {
      content: "\\f058";
      color: #286090;
    }
    li.uncataloged a {
        color:#dc3545 !important;
    }
    li.uncataloged a:before {
      content: "\\f057";
    }
    <style>
  ''')
  prt.append('</body>')
  prt.append('</html>')
  
  return '\n'.join(prt)