# README ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# This ZMS action adds a list of strings to the ZMS multidict attribute named
# internal_dict. The list values may be rendered into element the elements html
# output as additional CSS classes:
# -----------------------------------------------------------------------------------
# tal:attributes="class python:' '.join(zmscontext.attr('internal_dict').get('css_classes',[]))"
# -----------------------------------------------------------------------------------
# This allows special GUI modifications of any individual ZMS object corresponding 
# to the selected class values. The example code uses the list of ZMS roles for 
# specific class names. You can change the code to other name lists fitting to your needs.
# Hint: You can use the function get_css_classes() to add the css classes to
# the third view templates (standard_html)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def get_css_classes(ob):
	internal_dict = ob.attr('internal_dict')
	css_classes = internal_dict.get('css_classes',[])
	return (css_classes)

def set_css_classes(ob,css_classes):
	internal_dict = ob.attr('internal_dict')
	internal_dict['css_classes'] = css_classes
	ob.setObjStateModified(ob.REQUEST)
	ob.setObjProperty('internal_dict',internal_dict)
	ob.onChangeObj(ob.REQUEST)
	# Workflow: Auto-Commit
	ob.commitObj(ob.REQUEST)
	# return ob.attr('internal_dict')['css_classes']
	return True


def manage_css_classes(self):
	request = self.REQUEST
	html = ''
	html += '<!DOCTYPE html>'
	html += '<html lang="en">'
	html += self.zmi_html_head(self,request)
	html += '<body class="%s">'%(' '.join(['zmi',request['lang'],'transition',self.meta_id]))
	html += self.zmi_body_header(self,request,options=[{'action':'#','label':'CSS Classes'}])
	html += '<div id="zmi-tab">'
	html += self.zmi_breadcrumbs(self,request)
	html += '<form class="form-horizontal card" method="post" enctype="multipart/form-data">'
	html += '<input type="hidden" name="form_id" value="manage_css_classes"/>'
	html += '<input type="hidden" name="lang" value="%s"/>'%request['lang']
	html += '<legend>Add Special CSS Classes:</legend>'

	# --- Insert css_classes.
	# ---------------------------------
	if request.form.get('btn')=='BTN_INSERT':
		message = []
		css_classes = request.get('css_classes',[])
		if css_classes:
			set_css_classes(self,css_classes)
			message.append('CSS classes added: %s'%(css_classes))
		else:
			set_css_classes(self,[])
			message.append('No CSS classes added, existing CSS classes removed')
		request.response.redirect(self.url_append_params('%s/manage_main'%self.absolute_url(),{'lang':request['lang'],'manage_tabs_message':'<br/>'.join(message)}))

	# --- Display initial insert form.
	# ---------------------------------
	else:

		# GENERATE CSS LIST (Example Code)
		css_classes = list(self.getRootElement().getSecurityRoles().keys())
		css_classes.extend(['ZMSAdministrator','ZMSEditor','ZMSAuthor','ZMSSubscriber','ZMSUserAdministrator'])
		css_classes = map(lambda r: [str(r)+'_special',str(r)+'_special'],css_classes)
		# /GENERATE CSS LIST

		html += '<div class="card-body form-group row">'
		html += '<div class="col-sm-12">'
		html += self.zmi_input_multiselect(self,name='css_classes',value=get_css_classes(self),lang_str='CSS Classes',options=css_classes)
		html += '</div>'
		html += '</div><!-- .form-group -->'
		html += '<div class="form-group row">'
		html += '<div class="controls save">'
		html += '<button type="submit" name="btn" class="btn btn-primary" value="BTN_INSERT">%s</button>'%(self.getZMILangStr('BTN_INSERT'))
		html += '&nbsp;<button type="submit" name="btn" class="btn btn-secondary" value="BTN_CANCEL">%s</button>'%(self.getZMILangStr('BTN_CANCEL'))
		html += '&nbsp;</div>'
		html += '</div><!-- .form-group -->'

	# ---------------------------------

	html += '</form><!-- .form-horizontal -->'
	html += '</div><!-- #zmi-tab -->'
	html += self.zmi_body_footer(self,request)
	html += '</body>'
	html += '</html>'

	return html