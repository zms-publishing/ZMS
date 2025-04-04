## Script (Python) "manage_stereotype"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=*** DO NOT DELETE OR MODIFY ***
##
from Products.zms import standard
request = container.REQUEST
RESPONSE =  request.RESPONSE

if request.get('btn') == 'BTN_EXECUTE':
	def traverse(node):
		rtn = []
		if node.meta_id == request['src_meta_id']:
			attrs = {}
			for x in request.form:
				if x.startswith('meta_attr_'):
					key = x[len('meta_attr_'):]
					type = key[key.rfind('_')+1:]
					name = key[:key.rfind('_')]
					if type in ['*']+context.getMetaobjIds():
						attrs[request.form[x]] = name
					else:
						attrs[request.form[x]] = {}
						for lang in node.getLangIds():
							req = {'lang':lang}
							attrs[request.form[x]][lang] = node.getObjProperty(name,req)
			node.operator_setattr(node,'meta_id',request['meta_id'])
			for x in request.form:
				if x.startswith('meta_attr_'):
					key = x[len('meta_attr_'):]
					type = key[key.rfind('_')+1:]
					name = key[:key.rfind('_')]
					new_key = request.form[x]
					if new_key:
						new_type = new_key[new_key.rfind('(')+1:-1]
						new_name = new_key[:new_key.rfind('(')]
						if new_name != name:
							value = attrs[request.form[x]]
							if new_type in ['*']+context.getMetaobjIds():
								for id in node.objectIds(list(context.dGlobalAttrs)):
									id_prefix = context.get_id_prefix(id)
									if id_prefix==name:
										new_id = new_name + id[len(id_prefix):]
										node.manage_renameObject(id=id,new_id=new_id)
							else:
								for lang in value:
									node.setObjProperty(new_name,value[lang],lang)
		if int(request.get('recursive',0)):
			for childNode in node.getChildNodes():
				rtn.extend(traverse(childNode))
		return rtn
	result = traverse(context)
	request.set('manage_tabs_message',context.getZMILangStr('MSG_CHANGED')+'<br>'.join([str(x) for x in result]))

html = ''
html += '<!DOCTYPE html>'
html += '<html lang="en">'
html += context.zmi_html_head(context,request)
html += '<body hx-push-url="true" class="%s">'%(' '.join(['zmi',request['lang'],context.meta_id]))
html += context.zmi_body_header(context,request,options=[
	{'label': 'TAB_EDIT', 'action': 'manage_main'},
	{'label': 'TAB_PROPERTIES', 'action': 'manage_properties'},
	{'label': 'TAB_IMPORTEXPORT', 'action': 'manage_importexport'},
	{'label': 'TAB_REFERENCES', 'action': 'manage_RefForm'},
	{'label': 'TAB_SEARCH', 'action': 'manage_tab_search'},
	{'label': 'TAB_TASKS', 'action': 'manage_tab_tasks'},
	{'label': 'ATTR_STATISTICS', 'action': 'manage_tab_statistics'},
	{'label': 'Stereotypes', 'action': 'manage_stereotype'},
])
html += '<div id="zmi-tab">'
html += context.zmi_breadcrumbs(context,request)
html += '<form class="form-horizontal card" method="post" enctype="multipart/form-data">'

html += '<legend>Select Attribute Mappings</legend>'
html += '<div class="card-body">'
html += '<div class="alert alert-warning mx-0">For migration one content-object into an aother please choose the target stereotype and select its target attributes</div>'
html += '<div class="form-group row">'
html += '<label class="col-sm-2 control-label mandatory"><span>Stereotype</span></label>'
html += '<div class="col-sm-10">'
html += '<div class="formgroup row">'
html += '<div class="col-sm-6">'
html += '<label class="control-label" style="margin-bottom:0.5em"><i class="text-muted">Source</i></label>'
html += '<select class="form-control" style="background:#f2dede;"name="src_meta_id">'
for meta_id in context.getMetaobjIds(sort=True):
	metaObj = context.getMetaobj(meta_id)
	if metaObj['type'] in ['ZMSDocument','ZMSObject']:
		data_attrs = [context.getMetaobjAttr(metaObj['id'],x['id']) for x in metaObj['attrs'] if x['id'] not in ['icon','icon_clazz','levelnfc'] and x['type'] not in ['constant','delimiter','hint','interface','method','py','resource','zpt']]
		data_attrs= ','.join(['%s(%s)'%(x['id'],x['type']) for x in data_attrs])
		html += '<option value="%s" data-attrs="%s"%s>%s (%s)</option>'%(metaObj['id'],data_attrs,['',' selected="selected"'][int(request.get('src_meta_id',context.meta_id)==metaObj['id'])],str(context.display_type(request,metaObj['id'])),metaObj['id'])
html += '</select><!-- .form-control -->'
html += '</div>'
html += '<div class="col-sm-6">'
html += '<label class="control-label" style="margin-bottom:0.5em"><i class="text-muted">Target</i></label>'
html += '<select class="form-control" style="background:#d9edf7;" name="meta_id">'
for meta_id in context.getMetaobjIds(sort=True):
	metaObj = context.getMetaobj(meta_id)
	if metaObj['type'] in ['ZMSDocument','ZMSObject']:
		data_attrs = [context.getMetaobjAttr(metaObj['id'],x['id']) for x in metaObj['attrs'] if x['id'] not in ['icon','icon_clazz','levelnfc'] and x['type'] not in ['constant','delimiter','hint','interface','method','py','resource','zpt']]
		data_attrs= ','.join(['%s(%s)'%(x['id'],x['type']) for x in data_attrs])
		html += '<option value="%s" data-attrs="%s"%s>%s (%s)</option>'%(metaObj['id'],data_attrs,['',' selected="selected"'][int(request.get('meta_id',context.meta_id)==metaObj['id'])],str(context.display_type(request,metaObj['id'])),metaObj['id'])
html += '</select><!-- .form-control -->'
html += '</div>'
html += '</div>'
html += '</div><!--.col-sm-10 -->'
html += '</div>'

html += '<div class="form-group row">'
html += '<label class="col-sm-2 control-label mandatory"><span>Attributes</span></label>'
html += '<div class="col-sm-10 attrs">'
html += '</div><!--.col-sm-10 -->'
html += '</div>'

html += '<div class="form-group row">'
html += '<label class="col-sm-2 control-label mandatory"><span>Recursive</span></label>'
html += '<div class="col-sm-10">'
html += '<span class="btn btn-secondary"><input name="recursive" type="checkbox" value="1" checked="checked"/></span>'
html += '</div><!--.col-sm-10 -->'
html += '</div>'

html += '<div class="form-row">'
html += '<div class="controls save">'
html += '<button type="submit" name="btn" class="btn btn-primary" value="BTN_EXECUTE">%s</button> '%(standard.pystr(context.getZMILangStr('BTN_EXECUTE')))
html += '<button type="submit" name="btn" class="btn btn-secondary" value="BTN_CANCEL">%s</button> '%(standard.pystr(context.getZMILangStr('BTN_CANCEL')))
html += '</div><!-- .controls.save -->'
html += '</div><!-- .form-row -->'

# ---------------------------------

html += '</div><!--. card-body -->'
html += '</form><!-- .form-horizontal -->'
html += '</div><!-- #zmi-tab -->'
html += context.zmi_body_footer(context,request)
html += '''<script>
function onSelectMetaIdChange() {
	var $selectSrc = $("select[name=src_meta_id]");
	var $selectedSrc = $("option:selected",$selectSrc);
	var attrsSrc = $selectedSrc.attr("data-attrs").split(",");
	var $select = $("select[name=meta_id]");
	var $selected = $("option:selected",$select);
	var attrs = $selected.attr("data-attrs").split(",");
	var html = "";
	for (var i = 0; i < attrsSrc.length; i++) {
		var src = attrsSrc[i];
		var name = src.substr(0,src.indexOf('('));
		var type = src.substr(src.indexOf('(')+1);
		type = type.substr(0,type.indexOf(')'));
		html += '<div class="form-group row">'
		html += '<label class="col-sm-6 control-label text-right">' + src+'</label>';
		html += '<div class="col-sm-6">';
		html += '<select class="form-control" style="background:#d9edf7" name="meta_attr_'+name+"_"+type+'">';
		html += '<option></option>';
		for (var j = 0; j < attrs.length; j++) {
		var target = attrs[j];
		html += '<option' + (target.indexOf(name+'(')==0?' selected="selected"':'')+' value="'+target+'">'+target+'</option>';
		}
		html += '</select>';
		html += '</div>';
		html += '</div>';
	}
	$(".attrs").html(html);
}
$("select[name$=meta_id].form-control").each(function() {
	$(this).change(onSelectMetaIdChange).change();
});
$(function(){
	$('li.nav-item[data-action=manage_tab_stereotypes]').addClass('active');
})
</script>'''
html += '</body>'
html += '</html>'

return html
