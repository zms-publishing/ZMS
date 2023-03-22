from Products.zms import standard
import os

def manage_repository_gitpull(self, request=None):
	html = []
	request = self.REQUEST
	RESPONSE =  request.RESPONSE
	btn = request.form.get('btn')
	came_from = request.get('came_from',request['HTTP_REFERER'])
	if came_from.find('?') > 0:
		came_from = came_from[:came_from.find('?')]
	base_path = self.getConfProperty('ZMS.conf.path', self.get_conf_basepath(id=''))
	git_branch = self.getConfProperty('ZMSRepository.git.server.branch','main').replace('"','').replace(';','')

	html.append('<!DOCTYPE html>')
	html.append('<html lang="en">')
	html.append(self.zmi_html_head(self,request))
	html.append('<body class="repository_manager_main %s">'%(' '.join(['zmi',request['lang'],self.meta_id])))
	html.append(self.zmi_body_header(self,request,options=self.repository_manager.customize_manage_options()))
	html.append('<div id="zmi-tab">')
	html.append(self.zmi_breadcrumbs(self,request,extra=[self.manage_sub_options()[0]]))
	html.append('<div class="card">')
	html.append('<form class="form-horizontal" method="post" enctype="multipart/form-data">')
	html.append('<input type="hidden" name="lang" value="%s"/>'%request['lang'])
	html.append('<input type="hidden" name="came_from" value="%s"/>'%came_from)
	html.append('<legend>%s, Current Branch = %s</legend>'%(self.getZMILangStr('BTN_GITPULL'),git_branch))


	# --- PULL. +++IMPORTANT+++: Use SSH/cert and git credential manager
	# ---------------------------------
	if btn=='BTN_GITPULL':
		message = []
		git_commands = []
		### update from repository
		if len([x for x in request['AUTHENTICATED_USER'].getRolesInContext(self) if x in ['Manager','ZMSAdminstrator']]) > 0:
			os.chdir(base_path)

			# GIT reset hard
			if request.get('git_hardreset'):
				git_commands.append( 'git reset --hard origin/%s'%(git_branch) )

			# GIT checkout branch
			if self.getConfProperty('ZMSRepository.git.server.branch.checkout', 0) == 1:
				git_commands.append( 'git checkout %s'%(git_branch) )

			# GIT checkout revision
			if request.get('git_revision')!='HEAD' and request.get('git_revision') is not None:
				git_commands.append( 'git checkout %s'%(request.get('git_revision').replace('"','').replace(';','')) )

			# GIT pull
			git_commands.append( 'git pull' )

			# EXECUTE GIT COMMANDS
			for gcmd in git_commands:
				res = os.system(gcmd)
				message.append('<code class="d-block">%s [%s]</code>'%(gcmd, str(res)))
			message.append('<code class="d-block mb-3"># Done</code>')

		else:
			message.append('Error: To execute this function a user role Manager or ZMSAdministrator is needed.')
		### return with message
		request.response.redirect(standard.url_append_params('manage_main',{'lang':request['lang'],'manage_tabs_message':''.join(message)}))

	# --- Cancel.
	# ---------------------------------
	elif btn=='BTN_CANCEL':
		request.response.redirect(standard.url_append_params(came_from,{'lang':request['lang']}))

	# --- Display initial form.
	# -------------------------
	else:
		html.append('<div class="card-body">')
		html.append('<div class="form-group row">')
		html.append('<label for="git_revision" class="col-sm-2 control-label mandatory">Revision</label>')
		html.append('<div class="col-sm-10"><input class="form-control" name="git_revision" type="text" size="25" value="HEAD" title="Default value HEAD pulls the latest revision. Please, enter the hexadecimal ID for checking out a specific revision." placeholder="Enter HEAD or Revision-ID"></div>')
		html.append('</div><!-- .form-group -->')
		html.append('<div class="form-group row">')
		html.append('<label for="git_hardreset" class="col-sm-2 control-label mandatory">Use Hard Reset</label>')
		html.append('<div class="col-sm-10"><span class="btn btn-secondary btn-default"><input type="checkbox" name="git_hardreset" value="git_hardreset" title="git reset --hard origin/%s" /></span></div>'%(git_branch))
		html.append('</div><!-- .form-group -->')
		html.append('<div class="form-group">')
		html.append('<div class="controls save">')
		html.append('<button type="submit" name="btn" class="btn btn-primary" value="BTN_GITPULL">%s</button>'%(self.getZMILangStr('BTN_GITPULL')))
		html.append('<button type="submit" name="btn" class="btn btn-secondary btn-default" value="BTN_CANCEL">%s</button>'%(self.getZMILangStr('BTN_CANCEL')))
		html.append('</div>')
		html.append('</div><!-- .form-group -->')
		# html.append(self.manage_main_diff(self,request))
		html.append('</div><!-- .card-body -->')
	# ---------------------------------

	html.append('</form><!-- .form-horizontal -->')
	html.append('</div><!-- .card -->')
	html.append('</div><!-- #zmi-tab -->')
	html.append(self.zmi_body_footer(self,request))
	html.append('<script>$ZMI.registerReady(function(){ $(\'#tabs_items li a\').removeClass(\'active\');$(\'#tabs_items li[data-action*=\"repository_manager\"] a\').addClass(\'active\'); })</script>')
	html.append('</body>')
	html.append('</html>')

	return '\n'.join(html)