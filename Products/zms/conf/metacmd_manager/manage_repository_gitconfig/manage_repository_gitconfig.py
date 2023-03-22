from Products.zms import standard
import os

def manage_repository_gitconfig(self, request=None):
	html = []
	request = self.REQUEST
	git_branch = self.getConfProperty('ZMSRepository.git.server.branch','main')
	git_url = self.getConfProperty('ZMSRepository.git.server.url','git@github.com:myname/myproject.git')
	if request.get('lang',None) is None:
		request['lang'] = 'ger'
	if request.get('manage_lang',None) is None:
		request['manage_lang'] = 'ger'
	RESPONSE =  request.RESPONSE
	btn = request.form.get('btn')
	came_from = request.get('came_from',request['HTTP_REFERER'])
	if came_from.find('?') > 0:
		came_from = came_from[:came_from.find('?')]
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
	html.append('<legend>GIT-%s, Current Branch = %s</legend>'%(self.getZMILangStr('TAB_CONFIGURATION'), git_branch))

	# --- Change.
	# ---------------------------------
	if btn=='BTN_CHANGE':
		message = []
		self.setConfProperty('ZMSRepository.git.server.url',request.get('git_url'))
		self.setConfProperty('ZMSRepository.git.server.branch',request.get('git_branch'))
		self.setConfProperty('ZMSRepository.git.server.branch.checkout', int(request.get('git_checkout',0)))
		message.append(self.getZMILangStr('MSG_CHANGED'))
		request.response.redirect(standard.url_append_params('manage_main',{'lang':request['lang'],'manage_tabs_message':'<br/>'.join(message)}))

	# --- Checkout.
	# ---------------------------------
	elif btn=='BTN_CLONE':
		os.chdir(base_path)
		command = "git clone %s ."%(git_url)
		result = os.system(command)
		html.append('<div class="alert alert-info my-3"><code class="d-block">%s [%s]</code></div>'%(command, str(result)))

	# --- Cancel.
	# ---------------------------------
	elif btn=='BTN_CANCEL':
		request.response.redirect(standard.url_append_params(came_from,{'lang':request['lang']}))

	# --- Display initial form.
	# -------------------------
	else:
		html.append('<div class="card-body">')
		html.append('<div class="alert alert-info m-0 mb-4">IMPORTANT NOTE: Please make sure that a certificate based communication with the GIT server is configured properly on the system</div>')
		html.append('<div class="form-group row">')
		html.append('<label for="url" class="col-sm-2 control-label mandatory">Working-copy</label>')
		html.append('<div class="col-sm-10"><input class="form-control" name="path" type="text" size="25" value="%s" readonly></div>'%base_path)
		html.append('</div><!-- .form-group -->')
		html.append('<div class="form-group row">')
		html.append('<label for="url" class="col-sm-2 control-label mandatory">Server</label>')
		html.append('<div class="col-sm-10"><input class="form-control" name="git_url" type="text" size="25" value="%s"></div>'%(git_url))
		html.append('</div><!-- .form-group -->')
		html.append('<div class="form-group row">')
		html.append('<label for="branch" class="col-sm-2 control-label mandatory">Branch Name</label>')
		html.append('<div class="col-sm-10"><input class="form-control" name="git_branch" placeholder="main" type="text" size="25" value="%s"></div>'%(git_branch))
		html.append('</div><!-- .form-group -->')
		html.append('<div class="form-group row">')
		html.append('<label for="branch" class="col-sm-2 control-label mandatory">Always checkout first</label>')
		html.append('<div class="col-sm-10"><span class="btn btn-secondary btn-default"><input type="checkbox" name="git_checkout" id="git_checkout" value="1" %s title=" Any git command starts with: git checkout %s" /></span></div>'%(self.getConfProperty('ZMSRepository.git.server.branch.checkout', 0)==1 and 'checked=\042checked\042' or '', git_branch))
		html.append('</div><!-- .form-group -->')
		html.append('<div class="form-group row">')
		html.append('<div class="controls save">')
		html.append('<button type="submit" name="btn" class="btn btn-primary" value="BTN_CHANGE">%s</button> '%(self.getZMILangStr('BTN_CHANGE')))
		html.append('<button type="submit" name="btn" class="btn btn-warning" value="BTN_CLONE">%s</button> '%(self.getZMILangStr('BTN_CLONE')=='BTN_CLONE' and 'Clone' or self.getZMILangStr('BTN_CLONE')))
		html.append('<button type="submit" name="btn" class="btn btn-secondary btn-default" value="BTN_CANCEL">%s</button> '%(self.getZMILangStr('BTN_CANCEL')))
		html.append('</div>')
		html.append('</div><!-- .form-group -->')
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