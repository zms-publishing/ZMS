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
old = request.form.get('old','')
new = request.form.get('new','')
cselected = request.form.get('cselected',None)
aselected = request.form.get('aselected',None)
lselected = request.form.get('lselected','')
mode = request.form.get('mode','html')
did_replace = str(request.form.get('replace',0))=='1'
did_filter = str(request.form.get('filter',0))=='1'

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
	keys = here.getObjAttrs().keys()
	if cselected:
		keys = [aselected]
	for key in keys:
		objAttr = here.getObjAttr(key)
		langIds = ['']
		if objAttr['multilang']:
			langIds = here.getLangIds()
			if lselected:
				langIds = [lselected]
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


#################################################
# Preset Content Classes and Attributes
#################################################
excl_ids, types=[],[]
excl_ids=['ZMS','ZMSLib','ZMSSysFolder','ZMSTable','ZMSSqlDb','ZMSNote','ZMSPackage']
basictypes=['string','text','richtext','select','multiselect','multiautocomplete']

#################################################
# FUNCTION Alle relevanten Meta-Attributtypen
#################################################
def getAttrTypes():
	relevanttypes=basictypes
	for i in context.metaobj_manager.getMetadictAttrs():
		t = context.metaobj_manager.getMetadictAttr(i)['type']
		if t in basictypes:
			relevanttypes.append(i)
	return relevanttypes

#################################################
# FUNCTION Render LANG-Selector
#################################################
def renderLangSelector():
	s='<select class="form-control" id="lselected" name="lselected" title="Choose Language">'
	for l in context.getLanguages():
		s+='<option value="%s" %s>%s</option>'%(l, l==lselected and 'selected="selected"' or '', l)
	s+='</select>'
	return s

#################################################
# FUNCTION Render CONTENT-Selector
#################################################
def renderContentClassSelector():
	s='<select class="form-control" id="cselected" name="cselected" title="Content Class Name" onchange="javascript:ajaxAttrSelector(this.options[selectedIndex].value); return true;">\n'
	s+='<option value="">Choose Content Class ...</option>\n'
	for i in context.getMetaobjIds(excl_ids=excl_ids):
		s+='<option value="%s" %s>%s</option>\n'%(i, i==cselected and 'selected="selected"' or '', i) 
	s+='</select>'
	return s

#################################################
# FUNCTION Render ATTRIBUT-Selector
#################################################
def renderAttrSelector(cselected):
	s='<select class="form-control" id="aselected" title="Attributes of Class %s" name="aselected">'%(cselected)
	if cselected:
		relevanttypes=getAttrTypes()
		for a in context.getMetaobjAttrIds(cselected,types=relevanttypes):
			s+='<option value="%s" %s>%s</option>'%(a, a==aselected and 'selected="selected"' or '', a)
	else:
		s+='<option value="">Choose Attribute ...</option>\n'

	s+="</select>"
	return s

#################################################
# Render HTML-Page
#################################################
def renderHtml():
	html=[]
	html.append('<!DOCTYPE html>')
	html.append('<html lang="en">')
	html.append(context.zmi_html_head(context,request))
	html.append('<body class="%s">'%(' '.join(['zmi',request['lang'],'search_replace',did_replace and 'replaced' or '', context.meta_id])))
	html.append(context.zmi_body_header(context,request,options=[{'action':'#','label':'Search+Replace...'}]))
	html.append('<div id="zmi-tab">')
	html.append(context.zmi_breadcrumbs(context,request))

	html.append('<form id="form_searchreplace" class="form-horizontal card" method="post" enctype="multipart/form-data">')
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

		<div class="form-group row" id="filterset">
			<label for="new" class="col-sm-2 control-label">Attribute Filter</label>
			<div class="col-sm-10">
				<div class="input-group">
				<div class="input-group-prepend btn bg-secondary">
					<input type="checkbox" name="filter" value="1" class="mt-1" %s onclick="javascript:toggle_filterset()">
				</div>
				%s
				%s
				%s
				</div>
			</div>
		</div><!-- .form-group -->

		<div class="form-row">
			<div class="controls save">
				<button type="submit" name="btn" class="btn btn-primary" value="BTN_EXECUTE">%s</button> 
				<button type="submit" name="btn" class="btn btn-secondary" value="BTN_CANCEL">%s</button>
			</div><!-- .controls.save -->
		</div>
	'''%(	old, 
			did_replace and 'checked="checked"' or '', 
			new, did_filter and 'checked="checked"' or '', 
			renderContentClassSelector(), 
			renderAttrSelector(cselected), 
			renderLangSelector(), 
			btn_text_exec, 
			btn_text_cncl 
		)
	)

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
		for e in res:
			node_url = e['node'].absolute_url()
			node_meta = e['node'].meta_id
			node_attr = e['attr_name']
			node_text = str(standard.remove_tags(e['text'])).replace('\"','').replace(old,'<em>%s</em><i>%s</i>'%(old,new))
			message.append('<li title="Found Item"><a title="<b>%s.%s</b> %s" class="found_item" data-toggle="tooltip" data-html="true" data-placement="left" href="%s/manage_main" target="_blank">%s</a></li>'%( node_meta, node_attr, node_text, node_url, node_url))
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
				border:1px solid #0056b3 !important;
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
			form_searchreplace#fAttrChange select {
				width:fit-content;
			}
			form_searchreplace#fAttrChange input {
				min-width:10rem; border:1px solid #ced4da;
			}
			div#ObjList ol {
				border:1px solid #ccc;
				border-radius:4px;
				background-color:#fff;
				padding:1rem 2rem;
				margin:0;
				overflow:hidden;}
			div#ObjList pre {
				margin-top:1em;
			}
		</style>
		<script>
			$(function() {
				toggle_filterset();
			})
			function toggle_filterset() {
				if ($('#filterset input[type="checkbox"]').prop('checked')) {
					$('#filterset select').removeAttr('disabled');
				} else {
					$('#filterset select').attr('disabled','disabled');
				}
			};
			function ajaxAttrSelector(cselected) {
				$('#aselected').load('manage_searchReplace?mode=ajax&cselected=' + cselected );
			};
			// function ajaxPreview(cselected, aselected, searchstr, replacestr, lang) {
			// 	$('div#ObjList').html('<i class="text-primary fas fa-spinner fa-spin fa-3x"></i>');
			// 	$('div#ObjList').load('manage_attrChange?cselected=' + cselected + '&aselected=' + aselected + '&searchstr=' + encodeURI(searchstr) + '&replacestr=' + encodeURI(replacestr) + '&lang=' + lang + '&mode=Preview' );
			// }
			// function ajaxReplace(cselected, aselected, searchstr, replacestr, lang) {
			// 	Check = confirm("Wollen Sie wirklich ersetzen?");
			// 	if (Check == true) {
			// 		$('div#ObjList').html('<i class="text-primary fas fa-spinner fa-spin fa-3x"></i>');
			// 		$('div#ObjList').load('manage_attrChange?cselected=' + cselected + '&aselected=' + aselected + '&searchstr=' + encodeURI(searchstr) + '&replacestr=' + encodeURI(replacestr) + '&lang=' + lang + '&mode=Replace' );
			// 	};
			// }
		</script>
	''')

	html.append('</body>')
	html.append('</html>')
	return '\n'.join(list(html))

if mode=='ajax' and cselected:
	return renderAttrSelector(cselected=cselected)
else:
	return renderHtml()
