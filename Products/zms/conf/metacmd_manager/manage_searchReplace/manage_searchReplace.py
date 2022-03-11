## Script (Python) "manage_searchReplace"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
from Products.zms import standard
request = container.REQUEST
RESPONSE = request.RESPONSE
btn_text_exec = standard.pystr(context.getZMILangStr('BTN_EXECUTE'), encoding='utf-8', errors='replace')
btn_text_cncl = standard.pystr(context.getZMILangStr('BTN_CANCEL'), encoding='utf-8', errors='replace')
html=[]

def replace(o, old, new):
	if isinstance(o,(str,bytes)):
		return o.replace(old,new)
	elif standard.operator_gettype(o) is standard.operator_gettype({}):
		for k in o:
			o[k] = replace(o[k],old,new)
	elif standard.operator_gettype(o) is standard.operator_gettype([]):
		o = [replace(x,old,new) for x in o]
	return o

def run(here, old, new):
	# import pdb; pdb.set_trace()
	rtn = []
	for key in here.getObjAttrs().keys():
		objAttr = here.getObjAttr(key)
		langIds = ['']
		if objAttr['multilang']:
			langIds = here.getLangIds()
		for objVers in here.getObjVersions():
			for langId in langIds:
				objAttrName = here.getObjAttrName(objAttr,langId)
				objAttrVal = here.operator_getattr(objVers,objAttrName,None)
				if objAttrVal:
					# Important: our replace() differs data type: string, list and dict
					newVal = replace(objAttrVal,old,new)
					if newVal != objAttrVal:
						if request.get('replace'):
							# Do only replace if checkbox 'replace' was clicked
							here.operator_setattr(objVers,objAttrName, newVal)
						rtn.append(here)
	for childNode in here.getChildNodes():
		rtn.extend(run(childNode,old,new))
	return rtn

html.append('<!DOCTYPE html>')
html.append('<html lang="en">')
html.append(context.zmi_html_head(context,request))
html.append('<body class="%s">'%(' '.join(['zmi',request['lang'],'transition',context.meta_id])))
html.append(context.zmi_body_header(context,request,options=[{'action':'#','label':'Search+Replace...'}]))
html.append('<div id="zmi-tab">')
html.append(context.zmi_breadcrumbs(context,request))

html.append('<form class="form-horizontal card" method="post" enctype="multipart/form-data">')
html.append('<input type="hidden" name="form_id" value="manage_searchReplace"/>')
html.append('<input type="hidden" name="lang" value="%s"/>'%request['lang'])
html.append('<legend>Search+Replace...</legend>')
html.append('<div class="card-body">')

# --- Display initial insert form.
# ---------------------------------
html.append('''
	<div class="form-group row">
		<label for="old" class="col-sm-2 control-label mandatory">Search for</label>
		<div class="col-sm-10">
			<input class="form-control" name="old" type="text" size="25" value="" />
		</div>
	</div><!-- .form-group -->
	<div class="form-group row">
		<label for="new" class="col-sm-2 control-label">Replace with</label>
		<div class="col-sm-10">
			<div class="input-group">
				<div class="input-group-prepend btn btn-warning">
					<input type="checkbox" name="replace" value="1" class="mt-1">
				</div>
				<input class="form-control" name="new" type="text" size="25" value="" />
			</div>
		</div>
	</div><!-- .form-group -->
	<div class="form-row">
		<div class="controls save">
			<button type="submit" name="btn" class="btn btn-primary" value="BTN_EXECUTE">%s</button> 
			<button type="submit" name="btn" class="btn btn-secondary" value="BTN_CANCEL">%s</button>
		</div><!-- .controls.save -->
	</div>
'''%( btn_text_exec, btn_text_cncl))

# --- Execute.
# ---------------------------------
if request.form.get('btn')=='BTN_EXECUTE':
	message = []
	old = request['old']
	new = request['new']
	res = run(context,old,new)
	if str(request.form.get('replace'))=='1':
		message.append('%s Results found for <i>%s</i> and changed to <i>%s</i>.'%(len(res),old,new))
	else:
		message.append('%s Results found for <i>%s</i> and NOT changed.'%(len(res),old))
	message.append('<ol>')
	message.extend(['<li><a href="%s/manage_main" target="_blank">%s</a></li>'%(x.absolute_url(),x.absolute_url()) for x in res])
	message.append('</ol>')

	html.append('''
		<div class="alert alert-success my-3">
			<a class="close" style="font-size:1rem" data-dismiss="alert" href="#"><i class="fas fa-times"></i></a>
			%s
		</div>
	'''%('\n'.join(message)))

elif request.form.get('btn')=='BTN_CANCEL':
	request.response.redirect(context.url_append_params('manage_main',{'lang':request['lang']}))


html.append('</div><!-- .card-body -->')
html.append('</form><!-- .form-horizontal -->')
html.append('</div><!-- #zmi-tab -->')
html.append(context.zmi_body_footer(context,request))
html.append('</body>')
html.append('</html>')

return '\n'.join(list(html))
