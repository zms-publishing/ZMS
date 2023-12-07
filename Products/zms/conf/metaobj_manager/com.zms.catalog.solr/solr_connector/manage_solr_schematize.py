import json

def manage_solr_schematize( self):
	zmscontext = self

	# Default properties types
	# https://solr.apache.org/guide/8_11/schema-api.html#SchemaAPI-AddaNewField
	# https://solr.apache.org/guide/8_11/defining-fields.html#optional-field-type-override-properties

	add_field = [
		# HINT: The field 'id' is not allowed to be added by the Solr schema API
		# {
		#	'name':'id',
		#	'type':'string',
		#	'multiValued':False,
		#	'required':True
		# },
		{
			'name':'zmsid',
			'type':'string',
			'multiValued':False,
			'required':True
		},
		{
			'name':'uid',
			'type':'string',
			'multiValued':False,
			'indexed':True,
			'required':True
		},
		{
			'name':'loc',
			'type':'string',
			'multiValued':False,
			'required':False
		},
		{
			'name':'index_html',
			'type':'text_general',
			'multiValued':False,
			'required':False
		},
		{
			'name':'meta_id',
			'type':'string',
			'multiValued':False,
			'indexed':True,
			'required':False
		},
		{
			'name':'lang',
			'type':'string',
			'multiValued':False,
			'indexed':True,
			'required':False
		},
		{
			'name':'home_id',
			'type':'string',
			'multiValued':False,
			'indexed':True,
			'required':False
		}
	]

	# SOLR field types
	allowed_types = [
		'string',
		'text_general',
		'text_en',
		'text_de',
		'text_fr',
		'text_it',
		'text_es',
		'text_pt',
		'text_nl',
		'text_da',
		'long'
		'int',
		'float',
		'double',
		'date',
		'datetime',
		'uuid',
		'boolean',
		'binary',
		'short',
		'currency',
		'enum',
	]
	adapter = zmscontext.getCatalogAdapter()
	attrs = adapter.getAttrs()
	for attr_id in adapter._getAttrIds():
		if attr_id not in ['id', 'uid', 'zmsid', 'loc', 'index_html', 'meta_id', 'lang', 'home_id']:
			attr = attrs[attr_id]
			attr_type = attr.get('type')
			if attr_type in allowed_types:
				add_field.append({
					'name':attr_id, 
					'type':attr_type,
					'multiValued':False,
				})
			else:
				add_field.append({
						'name':attr_id, 
						'type':'text_general',
						'multiValued':False,
					})

	schema = json.dumps(dict({'add-field':list(add_field)}), indent=2)
	self.setConfProperty('solr.schema', schema)
	return schema