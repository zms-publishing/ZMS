from Products.zms import standard
import os

def manage_repository_gitpull(self, request=None):
	printed = []
	request = self.REQUEST
	RESPONSE =  request.RESPONSE
	btn = request.form.get('btn')
	came_from = request.get('came_from',request['HTTP_REFERER'])
	if came_from.find('?') > 0:
		came_from = came_from[:came_from.find('?')]
	base_path = self.get_conf_basepath()

	printed.append('<!DOCTYPE html>')
	printed.append('<html lang="en">')
	printed.append(self.zmi_html_head(self,request))
	printed.append('<body class="repository_manager_main %s">'%(' '.join(['zmi',request['lang'],self.meta_id])))
	# printed.append(self.zmi_body_header(self,request,options=[{'action':'#','label':'%s...'%self.getZMILangStr('BTN_GITPULL')}]))
	printed.append(self.zmi_body_header(self,request,options=self.repository_manager.customize_manage_options()))
	printed.append('<div id="zmi-tab">')
	printed.append(self.zmi_breadcrumbs(self,request,extra=[self.manage_sub_options()[0]]))
	printed.append('<div class="card">')
	printed.append('<form class="form-horizontal" method="post" enctype="multipart/form-data">')
	printed.append('<input type="hidden" name="lang" value="%s"/>'%request['lang'])
	printed.append('<input type="hidden" name="came_from" value="%s"/>'%came_from)
	printed.append('<legend>%s...</legend>'%self.getZMILangStr('BTN_GITPULL'))

	# --- PULL. +++IMPORTANT+++: Use SSH/cert and git credential manager
	# ---------------------------------
	if btn=='BTN_GITPULL':
		message = []
		### update from repository
		# userid = self.getConfProperty('ZMSRepository.git.server.userid')
		# password = self.getConfProperty('ZMSRepository.git.server.password') # TODO: decrypt
		# url = self.getConfProperty('ZMSRepository.git.server.url')
		command = 'git checkout master;git pull'
		if request.get('revision')!='HEAD' and request.get('revision') is not None:
			command = 'git checkout %s'%(request.get('revision'))
		os.chdir(base_path)
		result = os.system(command)
		message.append('<code class="d-block mb-3">%s [%s]</code>'%(command, str(result)))
		### import from working-copy
		# success = self.updateChanges(REQUEST.get('ids',[]),btn=='override')
		# message.append(self.getZMILangStr('MSG_IMPORTED')%('<em>%s</em>'%' '.join(success)))
		### return with message
		request.response.redirect(self.url_append_params('manage_main',{'lang':request['lang'],'manage_tabs_message':''.join(message)}))

	# --- Cancel.
	# ---------------------------------
	elif btn=='BTN_CANCEL':
		request.response.redirect(self.url_append_params(came_from,{'lang':request['lang']}))

	# --- Display initial form.
	# -------------------------
	else:
		printed.append('<div class="card-body">')
		printed.append('<div class="form-group row">')
		printed.append('<label for="revision" class="col-sm-2 control-label mandatory">Revision</label>')
		printed.append('<div class="col-sm-10"><input class="form-control" name="revision" type="text" size="25" value="HEAD" title="Default value HEAD pulls the latest revision. Please, enter the hexadecimal ID for checking out a specific revision." placeholder="Enter HEAD or Revision-ID"></div>')
		printed.append('</div><!-- .form-group -->')
		printed.append('<div class="form-group">')
		printed.append('<div class="controls save">')
		printed.append('<button type="submit" name="btn" class="btn btn-primary" value="BTN_GITPULL">%s</button>'%(self.getZMILangStr('BTN_GITPULL')))
		printed.append('<button type="submit" name="btn" class="btn btn-secondary" value="BTN_CANCEL">%s</button>'%(self.getZMILangStr('BTN_CANCEL')))
		printed.append('</div>')
		printed.append('</div><!-- .form-group -->')
		# printed.append(self.manage_main_diff(self,request))
		printed.append('</div><!-- .card-body -->')
	# ---------------------------------

	printed.append('</form><!-- .form-horizontal -->')
	printed.append('</div><!-- .card -->')
	printed.append('</div><!-- #zmi-tab -->')
	printed.append(self.zmi_body_footer(self,request))
	printed.append('<script>$ZMI.registerReady(function(){ $(\'#tabs_items li a\').removeClass(\'active\');$(\'#tabs_items li[data-action*=\"repository_manager\"] a\').addClass(\'active\'); })</script>')
	printed.append('</body>')
	printed.append('</html>')

	return '\n'.join(printed)