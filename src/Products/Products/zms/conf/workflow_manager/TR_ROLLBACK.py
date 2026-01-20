## Script (Python) "TR_ROLLBACK"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=zmscontext
##title=Rollback
##
request = zmscontext.REQUEST
message = 'Changes were rolled back. '

##### Notification ####
# Recipient
name = zmscontext.attr('work_uid')
mto = zmscontext.getRecipientWf(request)

# Subject
msubject = '[ZMS::%s]: Änderungen wurden zurück gezogen'%zmscontext.getDocumentElement().getTitle(request)
# Body
mbody = []
mbody.append('MANAGE: \t<%s/manage>\n'%(zmscontext.absolute_url()))
mbody.append('PREVIEW: \t<%s/preview_html>\n'%(zmscontext.absolute_url()))
mbody.append('INFO: Ihre Änderungen wurden rückgängig gemacht von\n\n')
mbody.append('%s\r\n\n\n'%(str(request['AUTHENTICATED_USER'])))
mbody.append('------------------------------------------------\n')
mbody.append('Diese Nachricht wurde automatisch generiert.\n')
# Send notification via MailHost
try:
    zmscontext.sendMail(mto, msubject, ''.join(mbody), request)
except:
    message += 'Info: E-Mail could not be sent.'

##### Rollback ####
zmscontext.rollbackObj(request)
# Return with message
message = 'Changes were rolled back.'
return request.RESPONSE.redirect(zmscontext.url_append_params('manage_wfTransitionFinalize',{
    'lang':request['lang'],
    'custom': request['custom'],
    'manage_tabs_message':message}))
