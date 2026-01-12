## Script (Python) "manage_setObjState"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Set object-state...
##
# ---------------------------------
# HANDLE WITH CARE: Set object-state...
# can be used by the administrator 
# to manipulate the workflow state of an object.
# ---------------------------------

from Products.zms import standard
request = container.REQUEST
RESPONSE = request.RESPONSE
zmscontext = context
lang = request['lang']
obj_states = [x.replace('_%s'%lang.upper(), '') for x in zmscontext.getObjStates()]

print('<!DOCTYPE html>')
print('<html lang="en">')
print(zmscontext.zmi_html_head(zmscontext,request))
print('<body class="%s">'%(' '.join(['zmi',request['lang'],'transition',zmscontext.meta_id])))
print(zmscontext.zmi_body_header(zmscontext,request,options=[{'action':'#','label':'Set object-state...'}]))
print('<div id="zmi-tab">')
print(zmscontext.zmi_breadcrumbs(zmscontext,request))
print('<form class="form-horizontal card" action="manage_setObjState" method="post" enctype="multipart/form-data">')
print('<input type="hidden" name="form_id" value="manage_setObjState"/>')
print('<input type="hidden" name="lang" value="%s"/>'%lang)
print('<legend>Current object-state: <code>%s</code></legend>'%(', '.join(obj_states)))
print('<div class="card-body">')

# --- Execute - and return to manage_main.
# ---------------------------------
if request.form.get('btn')=='BTN_SAVE':
	message = []
	new_obj_state = request.form.get('new_obj_state',[])
	# Only reset object states (not workflow states):
	# see VersionItem.resetObjStates()
	zmscontext.resetObjStates(request)
	# Add new object states:
	for obj_state in new_obj_state:
		zmscontext.setObjState(obj_state, lang)
	message.append('%s: %s'%(zmscontext.getZMILangStr('MSG_CHANGED'),', '.join(zmscontext.getObjStates())))
	return request.response.redirect(zmscontext.url_append_params('%s/manage_main'%zmscontext.absolute_url(),{'lang':request['lang'],'manage_tabs_message':'<br/>'.join(message)}))

# --- Display initial insert form.
# ---------------------------------
else:
	print('<div class="alert alert-warning mx-0">Please use with caution: This action changes the object-state and may interfere with the workflow.</div>')
	print('<div class="form-group row align-items-start">')
	print('<label for="new_obj_state" class="col-sm-2 control-label"><span>Change object-state to</span></label>')
	print('<div class="col-sm-10">')
	for obj_state in ['STATE_NEW', 'STATE_MODIFIED', 'STATE_MODIFIED_OBJS', 'STATE_DELETED']:
		print('<div>')
		print('<input name="new_obj_state:list" type="checkbox" value="' + obj_state + '"' + ['','checked="checked"'][obj_state in obj_states] + '> ')
		print('%s: <code>%s</code>'%(zmscontext.getZMILangStr(obj_state), obj_state))
		print('</div>')
	print('</div><!-- .col-sm-10 -->')
	print('</div><!-- .form-group -->')
	print('</div><!-- .form-group -->')
	print('<div class="form-group row">')
	print('<div class="controls save">')
	print('<button type="submit" name="btn" class="btn btn-primary" value="BTN_SAVE">%s</button> '%(zmscontext.getZMILangStr('BTN_SAVE')))
	print('<button type="submit" name="btn" class="btn btn-secondary" value="BTN_CANCEL">%s</button> '%(zmscontext.getZMILangStr('BTN_CANCEL')))
	print('</div><!-- .controls.save -->')
	print('</div><!-- .form-group -->')

# ---------------------------------

print('</div><!-- .card-body -->')
print('</form><!-- .form-horizontal -->')
print('</div><!-- #zmi-tab -->')
print(zmscontext.zmi_body_footer(zmscontext,request))
print('</body>')
print('</html>')

return printed
