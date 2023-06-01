from Products.zms import standard
import os

def manage_repository_gitpush(self, request=None):
	html = []
	request = self.REQUEST
	RESPONSE =  request.RESPONSE
	git_branch = self.getConfProperty('ZMSRepository.git.server.branch','main')
	btn = request.form.get('btn')
	came_from = request.get('came_from',request['HTTP_REFERER'])
	if came_from.find('?') > 0:
		came_from = came_from[:came_from.find('?')]
	base_path = self.getConfProperty('ZMS.conf.path', self.get_conf_basepath(id=''))

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
	html.append('<legend>%s, Current Branch = %s</legend>'%(self.getZMILangStr('BTN_GITPUSH'), git_branch))


	# --- COMMIT/PUSH. +++IMPORTANT+++: Use SSH/cert and git credential manager
	# ---------------------------------
	if btn=='BTN_GITPUSH':
		message = []
		git_commands = []

		if len([x for x in request['AUTHENTICATED_USER'].getRolesInContext(self) if x in ['Manager','ZMSAdminstrator']]) > 0:
			userid = 'zms_%s'%(str(request.get('AUTHENTICATED_USER'))[0:3])
			os.chdir(base_path)

			# GIT checkout branch
			if self.getConfProperty('ZMSRepository.git.server.branch.checkout', 0) == 1:
				git_commands.append( 'git checkout %s'%(git_branch) )

			# GIT add
			git_commands.append( 'git add .' )

			# GIT commit
			git_commit = 'git commit -a -m'
			if int(request.get('git_sign',0))==1:
				git_commit = 'git commit -a -S -m'
				self.setConfProperty('ZMSRepository.git.commit.sign', 1)
			elif self.getConfProperty('ZMSRepository.git.commit.sign', 0) == 1:
				self.setConfProperty('ZMSRepository.git.commit.sign', 0)
			git_commands.append( '%s "%s" --author="%s <>"'%( git_commit, request.get('git_message').replace('"','').replace(';',''), userid ) )

			# GIT push
			git_commands.append( 'git push')

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
		html.append('<label for="git_message" class="col-sm-2 control-label mandatory">Message</label>')
		html.append('<div class="col-sm-10"><input class="form-control" name="git_message" type="text" size="25" value="" placeholder="Enter commit message here"></div>')
		html.append('</div><!-- .form-group -->')
		html.append('<div class="form-group row">')
		html.append('<label for="git_sign" class="col-sm-2 control-label mandatory">Sign</label>')
		html.append('<div class="col-sm-10">')
		html.append('<span class="btn btn-secondary btn-default"><input type="checkbox" name="git_sign" value="1" %s title="Adds the -S param to the commit. Please make sure a certificate without passphrase is installed." /></span>'%(self.getConfProperty('ZMSRepository.git.commit.sign', 0)==1 and 'checked=\042checked\042' or ''))
		html.append('<small class="px-2 pull-right float-right"><a class="text-info" target="_blank" href="https://git-scm.com/book/en/v2/Git-Tools-Signing-Your-Work">More about Git signing...</a></small>')
		html.append('</div>')
		html.append('</div><!-- .form-group -->')
		html.append('<div class="form-group">')
		html.append('<div class="controls save">')
		html.append('<button type="submit" name="btn" class="btn btn-primary" value="BTN_GITPUSH">%s</button>'%(self.getZMILangStr('BTN_GITPUSH')))
		html.append('<button type="submit" name="btn" class="btn btn-secondary btn-default" value="BTN_CANCEL">%s</button>'%(self.getZMILangStr('BTN_CANCEL')))
		html.append('</div>')
		html.append('</div><!-- .form-group -->')
		# html.append(self.manage_main_diff(self,request))
		html.append('</div>')
	# ---------------------------------

	html.append('</form><!-- .form-horizontal -->')
	html.append('</div><!-- .card -->')
	html.append('</div><!-- #zmi-tab -->')
	html.append(self.zmi_body_footer(self,request))
	html.append('<script>$ZMI.registerReady(function(){ $(\'#tabs_items li a\').removeClass(\'active\');$(\'#tabs_items li[data-action*=\"repository_manager\"] a\').addClass(\'active\'); })</script>')
	html.append('</body>')
	html.append('</html>')

	return '\n'.join(html)