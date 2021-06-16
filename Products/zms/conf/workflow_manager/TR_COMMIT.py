## Script (Python) "TR_COMMIT"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=zmscontext
##title=Commit
##
request = zmscontext.REQUEST
message = ''

##### Notification ####
# Recipient
name = zmscontext.attr('work_uid')
mto = zmscontext.getRecipientWf(request)
# Subject
msubject = '[ZMS::%s]: Änderungen wurden publiziert.'%zmscontext.getDocumentElement().getTitle(request)
# Body
mbody = []
mbody.append('MANAGE: \t<%s/manage>\n'%(zmscontext.absolute_url()))
mbody.append('PREVIEW: \t<%s/preview_html>\n'%(zmscontext.absolute_url()))
mbody.append('INFO: Änderungen wurden publiziert von:\n')
mbody.append('%s\r\n\n\n'%(str(request['AUTHENTICATED_USER'])))
mbody.append('------------------------------------------------\n')
mbody.append('Diese Nachricht wurde automatisch generiert.\n')
# Send notification via MailHost
zmscontext.sendMail(mto, msubject, ''.join(mbody), request)

##### Commit ####
newcontext = zmscontext.commitObj(request)
message += 'Changes were committed'

##### Purge Cache ####
try:
  request.set('preview','')
  request.set('url',zmscontext.getHref2IndexHtml(request))
  zmscontext.purge_cache()
  # zmscontext.purgecache(zmscontext.getHref2IndexHtml(request))
  request.set('preview','preview')
  message += ', Cache were purged'
except:
  message += ', ERROR: No Cache Purging'

# Return with message
return request.RESPONSE.redirect(zmscontext.url_append_params('%s/manage_wfTransitionFinalize'%newcontext.absolute_url(),{
    'lang':request['lang'],
    'custom': request['custom'],
    'manage_tabs_message':message}))
