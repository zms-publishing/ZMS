## Script (Python) "ZMSIndexZCatalog.get_uid"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=zmscontext=None,options=None
##title=py: Extension-Point: get uid
##
# --// get_uid //--

forced = options['forced']
uid = zmscontext.ZMSIndexZCatalog_func_(zmscontext,'get_uid',forced)
return uid

# --// /get_uid //--
