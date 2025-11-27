## Script (Python) "manage_cleanup_metaobjs"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Multisite Meta-Object Definitions Removal
##
request = container.REQUEST
RESPONSE =  request.RESPONSE

### Define List of Metaobj-IDs that shall be Removed from Multisite 
remove_ids = [
    'zcatalog_page',
    'zcatalog_connector',
    'com.zms.catalog.zcatalog'
    ]
request.set('ids',remove_ids)

zmsclients = []
log = ['RESULTS:','---']

### Funktion, um Portal-Clients rekursiv zu verarbeiten
def getZMSPortalClients(zmsclient):
  zmsclients.append(zmsclient)
  for portalClient in zmsclient.getPortalClients():
    getZMSPortalClients(portalClient)
  return

### Create Client-List 'zmsclients'
getZMSPortalClients(container)

for zmsclient in zmsclients:
	metaobj_mgr = zmsclient.metaobj_manager
	clientid = zmsclient.getHome().id
	try:
		metaobj_mgr.manage_changeProperties(lang='ger', btn='BTN_DELETE', key='obj', REQUEST=request, RESPONSE=None)
		log.append( 'Client %s : Successfully cleaned: %s'%(clientid, remove_ids) )
	except:
		log.append( 'Client %s : Error occured, not cleaned: %s'%(clientid, remove_ids) )

request.RESPONSE.setHeader('Content-Type','text/plain;; charset=utf-8')
return '\n'.join(log)