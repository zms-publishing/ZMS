## Script (Python) "manage_change_primary_lang"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Change primary language...
##
from Products.zms import standard
request = container.REQUEST
RESPONSE =  request.RESPONSE

def traverse(node, prim_lang, new_prim_lang):
  c = 1
  coverage = node.attr('attr_dc_coverage') 
  standard.writeLog(node,'coverage=%s'%str(coverage))
  if coverage == 'global.%s'%prim_lang:
    node.attr('attr_dc_coverage','global.%s'%new_prim_lang)
  for child_node in node.getChildNodes():
    c += traverse(child_node, prim_lang, new_prim_lang)
  if node.meta_id == 'ZMS':
    standard.writeLog(node,'Change primary language: %s -> %s'%(prim_lang,new_prim_lang))
    langs = context.getLangs()
    context.setLanguage(prim_lang, langs[prim_lang]['label'], new_prim_lang, langs[prim_lang]['manage'])
    context.setLanguage(new_prim_lang, langs[new_prim_lang]['label'], '', langs[new_prim_lang]['manage'])
    for portal_client in node.getPortalClients():
      if portal_client is not None:
        c += traverse(portal_client, prim_lang, new_prim_lang)
  return c

print('<!DOCTYPE html>')
print('<html lang="en">')
print(context.zmi_html_head(context,request))
print('<body class="%s">'%(' '.join(['zmi',request['lang'],'transition',context.meta_id])))
print(context.zmi_body_header(context,request,options=[{'action':'#','label':'Change primary language...'}]))
print('<div id="zmi-tab">')
print(context.zmi_breadcrumbs(context,request))
print('<form class="form-horizontal card" method="post" enctype="multipart/form-data">')
print('<input type="hidden" name="form_id" value="manage_change_primary_lang"/>')
print('<input type="hidden" name="lang" value="%s"/>'%request['lang'])
print('<legend>Change primary language...</legend>')
print('<div class="card-body">')

# --- Execute.
# ---------------------------------
if request.form.get('btn')=='BTN_EXECUTE':
    message = []
    c = traverse(context, context.getPrimaryLanguage(), request.form.get('new_prim_lang'))
    message.append('%s: %i'%(context.getZMILangStr('MSG_CHANGED'),c))
    return request.response.redirect(context.url_append_params('%s/manage_main'%context.absolute_url(),{'lang':request['lang'],'manage_tabs_message':'<br/>'.join(message)}))

# --- Display initial insert form.
# ---------------------------------
else:
	print('<div class="alert alert-danger">Change primary language</div>')
	lang_ids = context.getLangIds(sort=True)
	print('<div class="form-group row">')
	print('<div class="col-sm-2 control-label">Primary language</div>')
	print('<div class="col-sm-10">')
	print('<select name="new_prim_lang" class="form-control">')
	print('<option value="">----- %s -----</option>'%(context.getZMILangStr('ACTION_SELECT')%context.getZMILangStr('ATTR_LANG')))
	for lang_id in lang_ids:
		if lang_id != context.getPrimaryLanguage():
			selected = (lang_id == context.getPrimaryLanguage()) and 'selected' or ''
			print('<option value="%s">%s -&gt; %s (%s)</option>'%(lang_id,context.getPrimaryLanguage(),lang_id,context.getLanguageLabel(lang_id)))
	print('</select>') 
	print('</div><!-- .col-sm-10 -->')
	print('</div><!-- .form-group -->')
	print('<div class="form-group row">')
	print('<div class="controls save">')
	print('<button type="submit" name="btn" class="btn btn-primary" value="BTN_EXECUTE">%s</button> '%(context.getZMILangStr('BTN_EXECUTE')))
	print('<button type="submit" name="btn" class="btn btn-secondary" value="BTN_CANCEL">%s</button> '%(context.getZMILangStr('BTN_CANCEL')))
	print('</div><!-- .controls.save -->')
	print('</div><!-- .form-group -->')

# ---------------------------------

print('</div><!-- .card-body -->')
print('</form><!-- .form-horizontal -->')
print('</div><!-- #zmi-tab -->')
print(context.zmi_body_footer(context,request))
print('</body>')
print('</html>')

return printed
