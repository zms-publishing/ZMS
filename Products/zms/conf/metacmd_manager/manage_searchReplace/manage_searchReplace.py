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
btn_text_exec = context.getZMILangStr('BTN_EXECUTE')
btn_text_cncl = context.getZMILangStr('BTN_CANCEL')
html=[]
old = request.form.get('old','')
new = request.form.get('new','')
did_replace = str(request.form.get('replace',0))=='1'

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
						rtn.append({'node':here,'attr_name':str(objAttrName),'text':objAttrVal})
	for childNode in here.getChildNodes():
		rtn.extend(run(childNode,old,new))
	return rtn

html.append('<!DOCTYPE html>')
html.append('<html lang="en">')
html.append(context.zmi_html_head(context,request))
html.append('<body class="%s">'%(' '.join(['zmi',request['lang'],'search_replace',did_replace and 'replaced' or '', context.meta_id])))
html.append(context.zmi_body_header(context,request,options=[{'action':'#','label':'Search+Replace...'}]))
html.append('<div id="zmi-tab">')
html.append(context.zmi_breadcrumbs(context,request))

html.append('<form class="form-horizontal card" method="post" enctype="multipart/form-data">')
html.append('<input type="hidden" name="form_id" value="manage_searchReplace"/>')
html.append('<input type="hidden" name="lang" value="%s"/>'%request['lang'])
html.append('<legend>Search+Replace...</legend>')
html.append('<div class="card-body">')

# --- Display insert form.
# ---------------------------------
html.append('''
	<div class="form-group row">
		<label for="old" class="col-sm-2 control-label mandatory">Search for</label>
		<div class="col-sm-10">
			<input class="form-control" name="old" type="text" size="25" value="%s" />
		</div>
	</div><!-- .form-group -->
	<div class="form-group row">
		<label for="new" class="col-sm-2 control-label">Replace with</label>
		<div class="col-sm-10">
			<div class="input-group">
				<div class="input-group-prepend btn btn-warning">
					<input type="checkbox" name="replace" value="1" class="mt-1" %s>
				</div>
				<input class="form-control" name="new" type="text" size="25" value="%s" />
			</div>
		</div>
	</div><!-- .form-group -->
	<div class="form-row">
		<div class="controls save">
			<button type="submit" name="btn" class="btn btn-primary" value="BTN_EXECUTE">%s</button> 
			<button type="submit" name="btn" class="btn btn-secondary" value="BTN_CANCEL">%s</button>
		</div><!-- .controls.save -->
	</div>
'''%( old, did_replace and 'checked="checked"' or '', new, btn_text_exec, btn_text_cncl ))

# --- Execute.
# ---------------------------------
if request.form.get('btn')=='BTN_EXECUTE':
	message = []
	res = run(context,old,new)
	if did_replace:
		message.append('<p>%s Results found for <em>%s</em> and changed to <i>%s</i>.</p>'%(len(res),old,new))
	else:
		message.append('<p>%s Results found for <em>%s</em> and NOT changed.</p>'%(len(res),old))
	message.append('<ol>')
	message.extend(['<li title="Found Item"><a title="<b>%s.%s</b> %s" class="found_item" data-toggle="tooltip" data-html="true" data-placement="left" href="%s/manage_main" target="_blank">%s</a></li>'%(x['node'].meta_id, x['attr_name'], str(standard.remove_tags(x['text'])).replace(old,'<em>%s</em><i>%s</i>'%(old,new)), x['node'].absolute_url(),x['node'].absolute_url()) for x in res])
	message.append('</ol>')

	html.append('''
		<div class="alert alert-success my-3 %s">
			<a class="close" style="font-size:1rem" data-dismiss="alert" href="#"><i class="fas fa-times"></i></a>
			%s
		</div>
	'''%(did_replace and 'replaced' or '', '\n'.join(message)))

elif request.form.get('btn')=='BTN_CANCEL':
	request.response.redirect(context.url_append_params('manage_main',{'lang':request['lang']}))


html.append('</div><!-- .card-body -->')
html.append('</form><!-- .form-horizontal -->')
html.append('</div><!-- #zmi-tab -->')
html.append(context.zmi_body_footer(context,request))

html.append('''
	<style>
		div.tooltip div.tooltip-inner {
			text-align: left !important;
			background:aliceblue;
			color:#000;
			border:1px solid  #0056b3 !important;
			min-width:30vw;
			width:fit-content;
			max-width:50vw;
		}
		div.tooltip div.tooltip-inner b {
			font-family:SFMono-Regular,Menlo,Monaco,Consolas,"Liberation Mono","Courier New",monospace;
			font-weight:bold;
			display:block;
			background:#759bbd;
			color:white;
			padding:.15em .5em .15em .5em;
			margin:-.35em -.6em 0 -.6em;
			border-top-left-radius:4px;
			border-top-right-radius:4px;
		}
		div.alert > p > em,
		div.tooltip div.tooltip-inner em {
			font-style:normal;
			font-weight:normal;
			background-color: #f8d7da!important;
		}
		.zmi.replaced > p > em,
		.zmi.replaced div.tooltip div.tooltip-inner em {
			text-decoration: line-through;
		}
		div.alert > p > i,
		div.tooltip div.tooltip-inner i {
			font-style:normal;
			font-weight:normal;
			background-color: #d4edda!important;
		}
		div.alert > p > i {
			background-color:#acd7c6!important;
		}
		div.tooltip div.arrow {
			display:none
		}
		div.tooltip {
			opacity:1 !important;
		}
	</style>
''')

html.append('</body>')
html.append('</html>')

return '\n'.join(list(html))
