import json

def manage_solr_schematize( self):
	zmscontext = self
	add_field = []

	# Force default properties types
	add_field.append({'name':'id', 'type':'string','multiValued':False,'indexed':True,'required':True,'stored':True})
	add_field.append({'name':'uid', 'type':'uuid','multiValued':False,'indexed':True,'required':True,'stored':True})
	add_field.append({'name':'zmsid', 'type':'string','multiValued':False,'indexed':False,'required':True,'stored':True})
	add_field.append({'name':'loc', 'type':'string','multiValued':False,'indexed':False,'required':False,'stored':True})
	add_field.append({'name':'index_html', 'type':'text_general','multiValued':False,'indexed':False,'required':False,'stored':True})
	add_field.append({'name':'meta_id', 'type':'keyword','multiValued':False,'indexed':True,'required':False,'stored':True})
	add_field.append({'name':'lang', 'type':'keyword','multiValued':False,'indexed':True,'required':False,'stored':True})
	add_field.append({'name':'home_id', 'type':'keyword','multiValued':False,'indexed':True,'required':False,'stored':True})

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
		add_field.append({
				'name':attr_id, 
				'type':'text_general',
				'multiValued':False,
				'indexed':False,
				'required':False,
				'stored':True
			})

	schema = json.dumps(dict({'add-field':list(add_field)}), indent=2)
	self.setConfProperty('solr.schema', schema)
	return schema