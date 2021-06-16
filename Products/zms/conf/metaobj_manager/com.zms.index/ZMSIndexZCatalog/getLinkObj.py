## Script (Python) "ZMSIndexZCatalog.getLinkObj"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=zmscontext=None,options=None
##title=py: Hook: Get link object
##
# --// ZMSIndexZCatalog.getLinkObj //--

request = zmscontext.REQUEST
zmsroot = zmscontext.getRootElement()
url = options['url']
try: return zmsroot.fetchReqBuff(options['url'],request)
except: pass

ob = None
if url.startswith('{$') and url.endswith('}'):
  url = url[2:-1]
  # Strip suffixes
  i = max(url.find('#'),url.find(','))
  if i > 0:
    url = url[:i]
  if url.find('id:') >= 0:
    q = zmscontext.zcatalog_index({'get_uid':url})
    for r in q:
      zmspath  = '%s/'%r['getPath']
      l = zmspath[1:-1].split('/')
      ob = zmscontext
      try:
        for id in [x for x in l if x]:
          ob = getattr(ob,id,None)
        break
      except:
        pass
  elif not url.startswith('__'):
    url = url.replace('@','/content/')
    l = url.split('/') 
    ob = zmscontext.getDocumentElement()
    try:
      for id in [x for x in l if x]:
        ob = getattr(ob,id,None)
    except:
      pass
return zmsroot.storeReqBuff(options['url'],ob)

# --// /ZMSIndexZCatalog.getLinkObj //--
