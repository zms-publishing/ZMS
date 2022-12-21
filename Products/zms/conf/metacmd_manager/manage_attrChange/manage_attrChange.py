## Script (Python) "manage_attrChange"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=cselected=None,aselected=None,searchstr=None,replacestr=None,mode=None,lang='ger'
##title=*** DO NOT DELETE OR MODIFY ***
##
request = container.REQUEST
RESPONSE =  request.RESPONSE
zms = context.content
thisobj = context.this()
# cselected = request.get('cselected',None)
# aselected = request.get('aselected',None)
# mode = request.get('mode',None)
# request.set('lang',request.get('lang','eng'))
request.set('manage_lang',request.get('manage_lang',request.get('lang','eng')))
request.set( 'ZMI_TIME',DateTime().timeTime())
request.set('attrChangeCount',0)

#################################################
# Version 5.0, FH 2021-10-26
# Fitted to ZMS5
# Refactored for ZMS3, Version 3.0, FH 2016-03-15
# based on V.1.2 (2010-06-03) Onkodin Bildatlas
#################################################

#################################################
# Vorgaben fuer Contentklassen und Attributarten
#################################################
excl_ids, types=[],[]
excl_ids=['ZMS','ZMSLib','ZMSSysFolder','ZMSTable','ZMSSqlDb','ZMSNote']
basictypes=['string','text','select','multiselect','multiautocomplete']


def decodeURIString(s):
  s = s.replace('%20',' ')
  s = s.replace('%22','"')
  s = s.replace('%26','&')
  s = s.replace('%28','(')
  s = s.replace('%29',')')
  s = s.replace('%2C',',')
  s = s.replace('%3A',':')
  s = s.replace('%3D','=')
  s = s.replace('%C4','Ä')
  s = s.replace('%D6','Ö')
  s = s.replace('%DC','Ü')
  s = s.replace('%DF','ß')
  s = s.replace('%E4','ä')
  s = s.replace('%F6','ö')
  s = s.replace('%FC','ü')

  return s

#################################################
# FUNCTION Alle relevanten Meta-Attributtypen
#################################################
def getAttrTypes():
  relevanttypes=basictypes
  for i in zms.metaobj_manager.getMetadictAttrs():
    t = zms.metaobj_manager.getMetadictAttr(i)['type']
    if t in basictypes:
      relevanttypes.append(i)
  return relevanttypes

#################################################
# FUNCTION Render LANG-Selector
#################################################
def renderLangSelector():
  s='<select class="form-control" id="lang" name="lang" title="Sprache ausw&auml;len">'
  for l in zms.getLanguages():
    s+='<option value="%s">%s</option>'%(l,l)
  s+='</select>'
  return s

#################################################
# FUNCTION Render CONTENT-Selector
#################################################
def renderContentClassSelector():
  s='<select class="form-control" id="cselected" name="cselected" title="Content-Klassen" onchange="javascript:ajaxAttrSelector(this.options[selectedIndex].value); return true;">\n'
  s+='<option value="">Content-Klasse w&auml;hlen:</option>\n'
  for i in zms.getMetaobjIds(excl_ids=excl_ids):
    s+='<option value="%s">%s</option>\n'%(i,i)
  s+='</select>'
  return s

#################################################
# FUNCTION Render ATTRIBUT-Selector
#################################################
def renderAttrSelector(cselected):
  s='<select class="form-control" id="aselected" title="Attribut-Namen" name="aselected">'
  if cselected!=None and cselected!='':
    relevanttypes=getAttrTypes()
    for a in zms.getMetaobjAttrIds(cselected,types=relevanttypes):
      s+='<option value="%s">%s</option>'%(a,a)
  else:
    s+='<option value="">Attribute:</option>\n'
  s+="</select>"
  return s


#################################################
# FUNCTION Execute in Preview or Replace Mode
#################################################
def ececuteAttrChange(cselected, aselected, searchstr,replacestr):
  searchstr = decodeURIString(searchstr)
  replacestr = decodeURIString(replacestr)
  attrFindCount=0
  attrChangeCount=0
  sError='<ol>'
  s='<ol>'
  l = []
  l.extend(thisobj.getTreeNodes(request, meta_types=[str(cselected)]))
  if len(l)>0:
    for e in l:
      v = e.getObjProperty(aselected,request)
      s+='<li><a target="_blank" href="%s/manage" title="%s: %s"><code class="text-white bg-dark px-2">%s</code></a><samp>: %s</samp>'%(str(e.absolute_url()),e.meta_id,str(e.absolute_url()), e.getId(), v )
      # type string/select
      # http://osdir.com/ml/python.general.german/2005-12/msg00061.html
      if isinstance(v, (str,bytes)) and searchstr==v.strip():
        s+='<strong style="color:green"><i class="fas fa-exchange-alt px-2"></i> %s </strong>'%(replacestr)
        attrFindCount+=1
      # Execute type string/select
        if mode=='Replace':
          try:
            e.setObjStateModified(request)
            e.setObjProperty(aselected, replacestr, lang=lang)
            e.onChangeObj(request,forced=1)
            e.commitObj(request)
            s+=' <span style="color:green">Changed.</span> '
            attrChangeCount+=1
          except:
            s+=' <span style="color:red">ERROR: not replaced</span> '
      # type multiselect
      elif searchstr!='' and searchstr in v:
        new_list_val = [ i if i!=searchstr else replacestr for i in v ]
        try:
          s+=' <strong style="color:green;"><i class="fas fa-exchange-alt px-2"></i><samp>%s</samp></strong>'%(new_list_val)
          attrFindCount+=1
        except:
          sError += '<li style="list-style-type:square;">No Specified Object Classes <em>%s</em> found. <a href="%s/manage_system" target="_blank">Iteration Error</a></li>'%(str(cselected), str(e.absolute_url()))
          # return s
      # Execute type multiselect
        if mode=='Replace':
          try:
            e.setObjStateModified(request)
            e.setObjProperty(aselected, new_list_val, lang=lang)
            e.onChangeObj(request,forced=1)
            e.commitObj(request)
            s+=' <span style="color:green">Changed.</span> '
            attrChangeCount+=1
          except:
            s+=' <span style="color:red">ERROR: not replaced</span> '
      s+='</li>'
    s+='</ol>'
    request.set('attrChangeCount',attrChangeCount)
    s+= '<pre>Changed: %i</pre>'%(request.get('attrChangeCount',0))
  else:
    s = '<ol><list-style-type:square;">No Object Classes <em>%s</em> found</li></ol>'%(str(cselected))
  sError += '</ol>'
  if sError == '<ol></ol>':
    sError = ''
  s += sError
  return s


#################################################
# FUNCTION Render HTML-Page: Default
#################################################
def renderHtml():
  s=''
  s+= '<!DOCTYPE html><html lang="en">'
  s+= thisobj.zmi_html_head(context,request)
  s+= '<body class="zmi" id="manage_attrChange" data-path="%s">'%(thisobj.getRootElement().getRefObjPath(thisobj))
  s+= thisobj.zmi_body_header(context,request)
  s+='<div id="zmi-tab">'
  s+=thisobj.zmi_breadcrumbs(context,request)

  s+= '''
    <script type="text/javascript">
      function ajaxAttrSelector(cselected) {
       $('#aselected').load('manage_attrChange?cselected=' + cselected );
      };
      function ajaxPreview(cselected, aselected, searchstr, replacestr, lang) {
       $('div#ObjList').html('<i class="text-primary fas fa-spinner fa-spin fa-3x"></i>');
       $('div#ObjList').load('manage_attrChange?cselected=' + cselected + '&aselected=' + aselected + '&searchstr=' + encodeURI(searchstr) + '&replacestr=' + encodeURI(replacestr) + '&lang=' + lang + '&mode=Preview' );
      }
      function ajaxReplace(cselected, aselected, searchstr, replacestr, lang) {
       Check = confirm("Wollen Sie wirklich ersetzen?");
       if (Check == true) {
         $('div#ObjList').html('<i class="text-primary fas fa-spinner fa-spin fa-3x"></i>');
         $('div#ObjList').load('manage_attrChange?cselected=' + cselected + '&aselected=' + aselected + '&searchstr=' + encodeURI(searchstr) + '&replacestr=' + encodeURI(replacestr) + '&lang=' + lang + '&mode=Replace' );
        };
      }
    </script>

    <style type="text/css">
      form#fAttrChange select {width:fit-content;}
      form#fAttrChange input {min-width:10rem; border:1px solid #ced4da;}
      div#ObjList ol {border:1px solid #ccc;border-radius:4px;background-color:#fff;padding:1rem 2rem;margin:0;overflow:hidden;}
      div#ObjList pre {margin-top:1em;}
    </style>
    '''

  s+= '''
    <form id="fAttrChange" class="card">
    <legend>Change Attribute Values by Search &amp; Replace</legend>
    <div class="card-body"><div class="form-inline">
    <div class="input-group my-3 mr-3">
  '''
  s+= renderContentClassSelector()
  s+= renderAttrSelector(cselected=None)
  s+= '''
    <input class="form-control alert-info text-monospace" id="searchstr" name="searchstr" type="text" title="Search for" value="" size="24" placeholder="Enter Old String..."/>
    <input class="form-control alert-danger text-monospace" id="replacestr" name="replacestr" type="text" title="Replace with" value="" size="24" placeholder="Enter New String..."/>
  '''
  s+= renderLangSelector()
  s+='</div>'
  s+= '''
    <div class="controls my-3">
    <button type="submit" class="btn btn-info"" id="Preview" name="Preview" value="Preview" onclick="javascript:ajaxPreview($('#cselected option:selected').val(), $('#aselected option:selected').val(), escape($('#searchstr').val()), escape($('#replacestr').val()), $('#lang').val() ); return false;">Preview</button>
    <button type="submit" class="btn btn-danger ml-3"" id="Replace" name="Replace" value="Replace" onclick="javascript:ajaxReplace($('#cselected option:selected').val(), $('#aselected option:selected').val(), escape($('#searchstr').val()), escape($('#replacestr').val()), $('#lang').val() ); return false;">Replace</button>
    </div></div></div>
    </form>
    <div id="ObjList" class="p-3"> </div>
  '''

  s+='</div><!-- #zmi-tab -->'
  s+= thisobj.zmi_body_footer(context,request)
  s+='</body></html>'
  return s


#################################################
# OUTPUT HTML
#################################################
html = ''
# View Default
if cselected==None:
  html = renderHtml()
# View Selected Object's Attrs
elif cselected!=None and mode==None:
  html = renderAttrSelector(cselected=cselected)
# View Execute-Mode Preview or Excute
elif cselected!=None and aselected!=None and mode!=None:
  html += ececuteAttrChange(cselected=cselected, aselected=aselected, searchstr=searchstr, replacestr=replacestr)

print(html)
# print(request)
RESPONSE.setHeader('Content-Type','text/html;charset=utf-8')
return printed
