from Products.PythonScripts.standard import html_quote
from Products.zms import standard

def manage_addClient(self):
	request = self.REQUEST
	html = ''
	html += '<!DOCTYPE html>'
	html += '<html lang="en">'
	html += self.zmi_html_head(self,request)
	html += '<body class="%s">'%(' '.join(['zmi',request['lang'],'transition',self.meta_id]))
	html += self.zmi_body_header(self,request,options=[{'action':'#','label':'Insert client...'}])
	html += '<div id="zmi-tab">'
	html += self.zmi_breadcrumbs(self,request)
	html += '<form class="form-horizontal card" method="post" enctype="multipart/form-data">'
	html += '<input type="hidden" name="form_id" value="manage_addClient"/>'
	html += '<input type="hidden" name="lang" value="%s"/>'%request['lang']
	html += '<legend>Insert new ZMS-Client</legend>'
	html += '<div class="card-body">'

	# --- Insert client.
	# ---------------------------------
	if request.form.get('btn')=='BTN_INSERT':
		message = []
		home = self.getHome()
		home.manage_addFolder(id=request['id'],title=request['title'])
		folder_inst = getattr(home,request['id'])
		request.set('lang_label',self.getLanguageLabel(request['lang']))
		zms_inst = self.initZMS(folder_inst, 'content', request['titlealt'], request['title'], request['lang'], request['manage_lang'], request)
		zms_inst.setConfProperty('Portal.Master',home.id)
		if request.get('acquire'):
			for id in [id for id in self.getMetaobjIds() if id not in ['ZMSIndexZCatalog','com.zms.index']]:
				zms_inst.metaobj_manager.acquireMetaobj(id)
		self.setConfProperty('Portal.Clients',self.getConfProperty('Portal.Clients',[])+[request['id']])
		message.append(self.getZMILangStr('MSG_INSERTED')%request['id'])
		request.response.redirect(standard.url_append_params('%s/manage_main'%zms_inst.absolute_url(),{'lang':request['lang'],'manage_tabs_message':'<br/>'.join(message)}))

	# --- Display initial insert form.
	# ---------------------------------
	else:
		html += '<div class="form-group row">'
		html += '<label for="id" class="col-sm-3 control-label mandatory">%s</label>'%(self.getZMILangStr('ATTR_ID'))
		html += '<div class="col-sm-9"><input class="form-control" name="id" type="text" size="25" value="client0"></div>'
		html += '</div><!-- .form-group -->'
		html += '<div class="form-group row">'
		html += '<label for="titlealt" class="col-sm-3 control-label mandatory">%s</label>'%(self.getZMILangStr('ATTR_TITLEALT'))
		html += '<div class="col-sm-9"><input class="form-control" name="titlealt" type="text" size="80" value="Client0 home"></div>'
		html += '</div><!-- .form-group -->'
		html += '<div class="form-group row">'
		html += '<label for="title" class="col-sm-3 control-label mandatory">%s</label>'%(self.getZMILangStr('ATTR_TITLE'))
		html += '<div class="col-sm-9"><input class="form-control" name="title" type="text" size="50" value="Client0 - Python-based contentmanagement system for science, technology and medicine"></div>'
		html += '</div><!-- .form-group -->'
		html += '<div class="form-group row">'
		html += '<label for="titlealt" class="col-sm-3 control-label">%s</label>'%(self.getZMILangStr('TAB_CONFIGURATION'))
		html += '<div class="col-sm-9"><input name="acquire:int" type="checkbox" value="1" checked="checked"> %s</div>'%(self.getZMILangStr('BTN_ACQUIRE'))
		html += '</div><!-- .form-group -->'
		html += '<div class="form-group row">'
		html += '<div class="controls save">'
		html += '<button type="submit" name="btn" class="btn btn-primary" value="BTN_INSERT">%s</button>'%self.getZMILangStr('BTN_INSERT')
		html += '<button type="submit" name="btn" class="btn btn-secondary" value="BTN_CANCEL">%s</button>'%self.getZMILangStr('BTN_CANCEL')
		html += '</div><!-- .controls.save -->'
		html += '</div><!-- .form-group -->'

	# ---------------------------------

	html += '</div><!-- .card-body -->'
	html += '</form><!-- .form-horizontal -->'
	html += '</div><!-- #zmi-tab -->'
	html += self.zmi_body_footer(self,request)
	html += '</body>'
	html += '</html>'

	return html