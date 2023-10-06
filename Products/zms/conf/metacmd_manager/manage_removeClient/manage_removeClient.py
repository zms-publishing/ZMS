## Script (Python) "manage_removeClient"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Remove ZMS-client...
##
from Products.zms import standard
request = container.REQUEST
RESPONSE =  request.RESPONSE
master = context.getPortalMaster()

print('<!DOCTYPE html>')
print('<html lang="en">')
print(context.zmi_html_head(context,request))
print('<body class="%s">'%(' '.join(['zmi',request['lang'],'transition',context.meta_id])))
print(context.zmi_body_header(context,request,options=[{'action':'#','label':'Remove ZMS-Client...'}]))
print('<div id="zmi-tab">')
print(context.zmi_breadcrumbs(context,request))
print('<form class="form-horizontal card" method="post" enctype="multipart/form-data">')
print('<input type="hidden" name="form_id" value="manage_removeClient"/>')
print('<input type="hidden" name="lang" value="%s"/>'%request['lang'])
print('<legend>Remove ZMS-Client...</legend>')
print('<div class="card-body">')

# --- Execute.
# ---------------------------------
if request.form.get('btn')=='BTN_DELETE':
    # import pdb; pdb.set_trace()
    home = context.getHome()
    home_id = home.id
    home.manage_delObjects(ids=[context.id]) # remove ZMS seperately to force deleting records from ZMSIndex
    master.getHome().manage_delObjects(ids=[home_id])
    # deregister at master
    l = master.getConfProperty('Portal.Clients', [])
    l.remove(home_id)
    master.setConfProperty('Portal.Clients', l)
    # Return with message
    message = []
    message.append(master.getZMILangStr('MSG_DELETED')%1)
    return request.response.redirect(master.url_append_params('%s/manage_main'%master.absolute_url(),{'lang':request['lang'],'manage_tabs_message':'<br/>'.join(message)}))

# --- Display initial insert form.
# ---------------------------------
else:
	print('<div class="alert alert-danger">Do you really want to remove ZMS-Client?</div>')
	print('<div class="form-group row">')
	print('<div class="controls save">')
	print('<button type="submit" name="btn" class="btn btn-primary" value="BTN_DELETE">%s</button> '%(context.getZMILangStr('BTN_DELETE')))
	print('<button type="submit" name="btn" class="btn btn-secondary" value="BTN_CANCEL">%s</button> '%(context.getZMILangStr('BTN_CANCEL')))
	print('</div><!-- .controls.save -->')
	print('</div><!-- .form-group -->')

# ---------------------------------

print('</div><!-- .card-body -->')
print('</form><!-- .form-horizontal -->')
print('</div><!-- #zmi-tab -->')
print(context.zmi_body_footer(context,request))
print('</body>')
print('</html>')

return printed
