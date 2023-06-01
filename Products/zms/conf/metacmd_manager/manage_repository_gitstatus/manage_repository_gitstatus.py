from Products.zms import standard
import os

def manage_repository_gitstatus( self ):

	html = []
	request = self.REQUEST
	git_branch = self.getConfProperty('ZMSRepository.git.server.branch','main')
	if request.get('lang',None) is None:
		request['lang'] = 'ger'
	if request.get('manage_lang',None) is None:
		request['manage_lang'] = 'ger'
	RESPONSE =  request.RESPONSE
	btn = request.form.get('btn')
	came_from = request.get('came_from',request['HTTP_REFERER'])
	if came_from.find('?') > 0:
		came_from = came_from[:came_from.find('?')]

	if btn=='BTN_CANCEL':
		request.response.redirect(standard.url_append_params(came_from,{'lang':request['lang']}))
	elif btn=='BTN_GITPULL':
		request.response.redirect('manage_repository_gitpull')
	elif btn=='BTN_GITPUSH':
		request.response.redirect('manage_repository_gitpush')
	else:
		# --- Display form.
		# -------------------------
		base_path = self.getConfProperty('ZMS.conf.path', self.get_conf_basepath(id=''))
		base_status = ''
		try:
			standard.localfs_readPath(base_path)
		except:
			base_status = standard.writeError(self,'can\'t read base_path')

		html.append('<!DOCTYPE html>')
		html.append('<html lang="en">')
		html.append(self.zmi_html_head(self,request))
		html.append('<body class="%s">'%(' '.join(['zmi',request['lang'],self.meta_id])))
		html.append(self.zmi_body_header(self,request,options=self.repository_manager.customize_manage_options()))
		html.append('<div id="zmi-tab">')
		html.append(self.zmi_breadcrumbs(self,request,extra=[self.manage_sub_options()[0]]))
		html.append('<div class="card">')
		html.append('<form class="form-horizontal" method="post" enctype="multipart/form-data">')
		html.append('<input type="hidden" name="lang" value="%s"/>'%request['lang'])
		html.append('<input type="hidden" name="came_from" value="%s"/>'%came_from)
		html.append('<legend>GIT-Status, Current Branch = %s</legend>'%(git_branch))

		message = ''
		git_commands = []
		if len([x for x in request['AUTHENTICATED_USER'].getRolesInContext(self) if x in ['Manager','ZMSAdminstrator']]) > 0:
			os.chdir(base_path)

			# GIT checkout branch
			if self.getConfProperty('ZMSRepository.git.server.branch.checkout', 0) == 1:
				git_commands.append( 'git checkout %s'%(git_branch) )
				git_commands.append( 'echo ""' )

			# GIT list branches
			git_commands.append( 'echo "# BRANCHES:"' )
			git_commands.append( 'git branch -l' )
			git_commands.append( 'echo ""' )

			# GIT status
			git_commands.append( 'git status' )
			git_commands.append( 'echo ""' )

			# GIT history
			git_commands.append( 'echo "# HISTORY:"' )
			git_commands.append( 'git log -10 --pretty="format:%ad : #%h %s [%an]" --date=short' )

			gcmd = ';'.join(git_commands)
			result = os.popen(gcmd).read()
			# result = os.system(command)
			message = '<pre class="zmi-code d-block m-0 p-4" style="color: #dee2e6;background-color: #354f67;"><b style="color:#8d9eaf;">>> %s</b><br/><br/>%s</pre>'%(gcmd,str(result))
		else:
			message = 'Error: To execute this function a user role Manager or ZMSAdministrator is needed.'
		html.append(message)
		html.append('<div class="card-body">')
		html.append('<div class="form-group row">')
		html.append('<div class="controls save">')
		html.append('<button type="submit" name="btn" class="btn btn-danger" value="BTN_GITPULL"><i class="fas fa-backward"></i>&nbsp;&nbsp;%s</button> '%(self.getZMILangStr('BTN_GITPULL')))
		html.append('<button type="submit" name="btn" class="btn btn-success" value="BTN_GITPUSH"><i class="fas fa-forward"></i>&nbsp;&nbsp;%s</button> '%(self.getZMILangStr('BTN_GITPUSH')))
		html.append('<button type="submit" name="btn" class="btn btn-secondary btn-default" value="BTN_CANCEL">Cancel</button>')
		html.append('</div>')
		html.append('</div><!-- .form-group -->')
		html.append('</div><!-- .card-body -->')

		# ---------------------------------

		html.append('</form><!-- .form-horizontal -->')
		html.append('</div><!-- .card -->')
		html.append('</div><!-- #zmi-tab -->')

		try:
			html.append(self.zmi_body_footer(self,request))
		except:
			html.append(self.zmi_body_footer(self,request).encode('utf-8'))

		html.append('<script>$ZMI.registerReady(function(){ $(\'#tabs_items li a\').removeClass(\'active\');$(\'#tabs_items li[data-action*=\"repository_manager\"] a\').addClass(\'active\'); })</script>')
		html.append('</body>')
		html.append('</html>')

		return '\n'.join(list(html))