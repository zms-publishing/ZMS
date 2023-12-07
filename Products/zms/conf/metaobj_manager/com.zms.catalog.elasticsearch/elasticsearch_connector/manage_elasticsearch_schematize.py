import json


def manage_elasticsearch_schematize( self):
	zmscontext = self
	properties = {}
	allowed_property_types = [
		'alias',
		'binary',
		'boolean',
		'completion',
		'date',
		'date_range',
		'double',
		'double_range',
		'float',
		'geo_point',
		'geo_shape',
		'half_float',
		'integer',
		'ip',
		'ip_range',
		'keyword',
		'long',
		'long_range',
		'object',
		'percolator',
		'rank_feature',
		'rank_features',
		'search_as_you_type',
		'text',
		'token_count'
	]
	adapter = zmscontext.getCatalogAdapter()
	attrs = adapter.getAttrs()
	for attr_id in adapter._getAttrIds():
		attr = attrs.get(attr_id,{})
		attr_type = attr.get('type', 'string')
		attr_type = {'string':'text'}.get(attr_type,attr_type)
		attr_type = attr_type == 'select'and 'keyword' or attr_type
		if attr_type not in allowed_property_types:
			attr_type = 'text'
		property = {}
		property['type'] = attr_type
		properties[attr_id] = property

	# Force default properties types
	properties['id'] = {'type':'text'}
	properties['zmsid'] = {'type':'text'}
	properties['uid'] = {'type':'text'}
	properties['loc'] = {'type':'text'}
	properties['index_html'] = {'type':'text'}
	properties['meta_id'] = {'type':'keyword'}
	properties['lang'] = {'type':'keyword'}
	properties['home_id'] = {'type':'keyword'}

	mappings = {'properties':properties}
	dictionary = {'mappings':mappings}
	schema = json.dumps(dictionary, indent=2)
	self.setConfProperty('elasticsearch.schema', schema)
	return schema