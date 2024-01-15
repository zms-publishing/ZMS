from Products.PythonScripts.standard import html_quote
from Products.zms import standard

def manage_addBulk(self):
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
	html += '<input type="hidden" name="form_id" value="manage_addBulk"/>'
	html += '<input type="hidden" name="lang" value="%s"/>'%request['lang']
	html += '<legend>Insert new ZMS-Bulk test-data</legend>'
	html += '<div class="card-body">'

	# --- Insert client.
	# ---------------------------------
	if request.form.get('btn')=='BTN_INSERT':
		message = []
		maxdepth = request['depth']
		page_elements = request['page_elements']
		pages = request['pages']
		def traverse(context, seq):
			l = []
			for page_element in range(page_elements):
				l.append(1)
				textarea = context.manage_addZMSCustom(meta_id='ZMSTextarea', values={'text':'<p><strong>Lorem ipsum dolor&nbsp;</strong></p>\n<p>Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua.'}, REQUEST=request)
				standard.writeBlock(textarea,"manage_addBulk: added page-element")
			if len(seq) < maxdepth:
				for page in range(pages):
					l.append(1)
					seq[-1] = seq[-1] - 1
					seqno = '.'.join([str(x) for x in seq])
					folder = context.manage_addZMSCustom(meta_id='ZMSFolder', values={'title':'Bulk test-data %s'%seqno, 'titlealt':'Bulk test-data %s'%seqno, 'attr_dc_description':'Bulk test-data'}, REQUEST=request)
					standard.writeBlock(folder,"manage_addBulk: added page")
					l.extend(traverse(folder, seq+[pages]))
			return l
		container = self.manage_addZMSCustom(meta_id='ZMSFolder', values={'title':'Bulk test-data', 'titlealt':'Bulk test-data', 'attr_dc_description':'Bulk test-data'}, REQUEST=request)
		l = traverse(container, [pages])
		message.append(self.getZMILangStr('MSG_INSERTED')%str(len(l)))
		request.response.redirect(standard.url_append_params('%s/manage_main'%container.absolute_url(),{'lang':request['lang'],'manage_tabs_message':'<br/>'.join(message)}))

	# --- Display initial insert form.
	# ---------------------------------
	else:
		html += '<div class="form-group row">'
		html += '<label for="depth" class="col-sm-3 control-label mandatory">Depth</label>'
		html += '<div class="col-sm-9"><input class="form-control" name="depth:int" type="number" value="5"></div>'
		html += '</div><!-- .form-group -->'
		html += '<div class="form-group row">'
		html += '<label for="page_elements" class="col-sm-3 control-label mandatory">Page-Elements</label>'
		html += '<div class="col-sm-9"><input class="form-control" name="page_elements:int" type="number" value="5"></div>'
		html += '</div><!-- .form-group -->'
		html += '<div class="form-group row">'
		html += '<label for="pages" class="col-sm-3 control-label mandatory">Pages</label>'
		html += '<div class="col-sm-9"><input class="form-control" name="pages:int" type="number" value="5"></div>'
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