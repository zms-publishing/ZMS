from Products.zms import standard
import os

def manage_repository_gitconfig(self, request=None):
	printed = []
	request = self.REQUEST
	RESPONSE =  request.RESPONSE
	btn = request.form.get('btn')
	came_from = request.get('came_from',request['HTTP_REFERER'])
	if came_from.find('?') > 0:
		came_from = came_from[:came_from.find('?')]
	base_path = self.get_conf_basepath()
	base_status = ''
	try:
		standard.localfs_readPath(base_path)
	except:
		base_status = standard.writeError(self,'can\'t read base_path') 

	printed.append('<!DOCTYPE html>')
	printed.append('<html lang="en">')
	printed.append(self.zmi_html_head(self,request))
	printed.append('<body class="%s">'%(' '.join(['zmi',request['lang'],self.meta_id])))
	#printed.append(self.zmi_body_header(self,request,options=[{'action':'#','label':'GIT-%s...'%self.getZMILangStr('TAB_CONFIGURATION')}]))
	printed.append(self.zmi_body_header(self,request,options=self.repository_manager.customize_manage_options()))
	printed.append('<div id="zmi-tab">')
	printed.append(self.zmi_breadcrumbs(self,request,extra=[self.manage_sub_options()[0]]))
	printed.append('<div class="card">')
	printed.append('<form class="form-horizontal" method="post" enctype="multipart/form-data">')
	printed.append('<input type="hidden" name="lang" value="%s"/>'%request['lang'])
	printed.append('<input type="hidden" name="came_from" value="%s"/>'%came_from)
	printed.append('<legend>GIT-%s...</legend>'%self.getZMILangStr('TAB_CONFIGURATION'))

	# --- Change.
	# ---------------------------------
	if btn=='BTN_CHANGE':
		message = []
		self.setConfProperty('ZMSRepository.git.server.url',request['url'])
		# self.setConfProperty('ZMSRepository.git.server.userid',request['userid'])
		# if request['password'] != '******':
		# 	self.setConfProperty('ZMSRepository.git.server.password',request['password']) # TODO: encrypt
		message.append(self.getZMILangStr('MSG_CHANGED'))
		request.response.redirect(self.url_append_params('manage_main',{'lang':request['lang'],'manage_tabs_message':'<br/>'.join(message)}))

	# --- Checkout.
	# ---------------------------------
	elif btn=='BTN_CLONE':
		# userid = self.getConfProperty('ZMSRepository.git.server.userid')
		# password = self.getConfProperty('ZMSRepository.git.server.password') # TODO: decrypt
		url = self.getConfProperty('ZMSRepository.git.server.url')
		os.chdir(base_path)
		command = "git clone %s ."%(url)
		result = os.system(command)
		printed.append('<div class="alert alert-info my-3"><code class="d-block">%s [%s]</code></div>'%(command, str(result)))

	# --- Cancel.
	# ---------------------------------
	elif btn=='BTN_CANCEL':
		request.response.redirect(self.url_append_params(came_from,{'lang':request['lang']}))

	# --- Display initial form.
	# -------------------------
	else:
		printed.append('<div class="card-body">')
		printed.append('<div class="alert alert-info m-0 mb-4">IMPORTANT NOTE: Please make sure that a certificate based communication with the GIT server is configured properly on the system</div>')
		printed.append('<div class="form-group row">')
		printed.append('<label for="url" class="col-sm-2 control-label mandatory">Working-copy</label>')
		printed.append('<div class="col-sm-10"><input class="form-control" name="path" type="text" size="25" value="%s" readonly></div>'%base_path)
		printed.append('</div><!-- .form-group -->')
		printed.append('<div class="form-group row">')
		printed.append('<label for="url" class="col-sm-2 control-label mandatory">Server</label>')
		printed.append('<div class="col-sm-10"><input class="form-control" name="url" type="text" size="25" value="%s"></div>'%self.getConfProperty('ZMSRepository.git.server.url','git@github.com:myname/myproject.git'))
		printed.append('</div><!-- .form-group -->')
		# printed.append('<div class="form-group row">')
		# printed.append('<label for="userid" class="col-sm-2 control-label mandatory">User-ID</label>')
		# printed.append('<div class="col-sm-10"><input class="form-control" name="userid" type="text" size="25" value="%s"></div>'%self.getConfProperty('ZMSRepository.git.server.userid','zmsdev'))
		# printed.append('</div><!-- .form-group -->')
		# printed.append('<div class="form-group row">')
		# printed.append('<label for="password" class="col-sm-2 control-label mandatory">Password</label>')
		# printed.append('<div class="col-sm-10"><input class="form-control" name="password" type="password" size="25" value="******"></div>')
		# printed.append('</div><!-- .form-group -->')
		printed.append('<div class="form-group row">')
		printed.append('<div class="controls save">')
		printed.append('<button type="submit" name="btn" class="btn btn-primary" value="BTN_CHANGE">%s</button> '%(self.getZMILangStr('BTN_CHANGE')))
		printed.append('<button type="submit" name="btn" class="btn btn-warning" value="BTN_CLONE">%s</button> '%(self.getZMILangStr('BTN_CLONE')=='BTN_CLONE' and 'Clone' or self.getZMILangStr('BTN_CLONE')))
		printed.append('<button type="submit" name="btn" class="btn btn-secondary" value="BTN_CANCEL">%s</button> '%(self.getZMILangStr('BTN_CANCEL')))
		printed.append('</div>')
		printed.append('</div><!-- .form-group -->')
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