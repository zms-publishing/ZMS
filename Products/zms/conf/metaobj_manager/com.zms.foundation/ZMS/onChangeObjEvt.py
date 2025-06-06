## Script (Python) "ZMS.onChangeObjEvt"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=zmscontext
##title=py: Event: onChange
##
# --// ZMS.onChangeObjEvt //--
from Products.zms import standard
request = zmscontext.REQUEST

# permalinks
# permalink_keys = [k for k in request.keys() if k.startswith('permalink_key__')]
# permalink_vals = [k for k in request.keys() if k.startswith('permalink_val__')]
if request.get('form_modified',False):
	prefix = '%s.permalink.'%zmscontext.meta_id
	# Delete all conf-properties
	for k in [x for x in zmscontext.getConfProperties() if x.startswith(prefix)]:
		standard.writeBlock(zmscontext,'DELETE CONF PARAM: %s '%(k) )
		zmscontext.delConfProperty(k)
	# Set new conf-properties
	reqprefix = 'permalink_key_'
	for reqkey in request.form:
		if reqkey.find(reqprefix) >= 0:
			id = reqkey[len(reqprefix):]
			k = request.get('permalink_key_%s'%id)
			v = request.get('permalink_val_%s'%id)
			standard.writeBlock(zmscontext,'ADD CONF PARAM: %s = %s'%(k,v) )
			if k and v:
				zmscontext.setConfProperty(prefix+k,v)

# --// /ZMS.onChangeObjEvt //--
