id = 'zcatalog_connector'
from Products.zms import standard

def getZCatalog(context, lang):
	cat_id = 'catalog_%s'%lang
	root = context.getRootElement()
	return getattr(root, cat_id, None)

def catalog_object(zcatalog, adapter, node, data):
	attr_ids = adapter._getAttrIds()
	# Prepare object.
	for attr_id in attr_ids:
		# ------------------------------------------------
		# Boosting (workaround): Since ZCatalog has not a 
		# scriptable interface for scoring content here
		# a pseudo-weighting is introduced by simple
		# content repetition. As an example the attribute 
		# content of 'attr_dc_subject' is multiplied by boost 
		# factor. HINT: Apply this only to the attributes that 
		# are not rendered as result content.
		# ------------------------------------------------
		wght = 1
		if attr_id == 'attr_dc_subject':
			wght = int(adapter._attrs.get('attr_dc_subject',{}).get('boost',1))
		attr_name = 'zcat_index_%s'%attr_id
		value = data.get(attr_id)
		if value in ['None', None]:
			value = ''
		elif isinstance(value, str):
			if wght != 1:
				value = (value.strip() + ' ') * wght
			else:
				value = value.strip()
		setattr(node, attr_name, value)
	# (Re-)Catalog object.
	path = node.getPath()
	if zcatalog.getrid(path):
		zcatalog.uncatalog_object(path)
	zcatalog.catalog_object(node, path)
	# Unprepare object.
	for attr_id in attr_ids:
		attr_name = 'zcat_index_%s'%attr_id
		delattr(node, attr_name)
	return 1

def manage_zcatalog_objects_add( self, objects):
	# Function applies to:
	#	ZMSZCatalogConnector.manage_objects_add 
	#	ZMSZCatalogConnector.reindex_page
	request = self.REQUEST
	adapter = self.getCatalogAdapter()
	success, failed = 0, 0
	for (node, data) in objects:
		lang = standard.nvl(data.get('lang',request.get('lang')), self.getPrimaryLanguage())
		if 'ZMS_ENV_ZCATALOG_%s'%lang.upper() not in request:
			request['ZMS_ENV_ZCATALOG_%s'%lang.upper()] = getZCatalog(self, lang)
		zcatalog = request['ZMS_ENV_ZCATALOG_%s'%lang.upper()]
		success += catalog_object(zcatalog, adapter, node, data)
	return success, failed