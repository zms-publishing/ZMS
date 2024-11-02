## Script (Python) "adwords.get_targets"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=zmscontext=None
##title=Private object function
##
import Products.zms.standard as standard

# Get ZMS targets by adword from REQUEST
## debug: return zmscontext.REQUEST.get('adword')
adword = zmscontext.REQUEST.get('adword').lower().strip()

def get_adwords_of_row(row):
	adwords = []
	adwords.append(row.get('adword').lower())
	synonyms = row.get('synonyms')
	if len(synonyms.split('\n'))==1:
		synonyms = [s.lower().strip() for s in synonyms.split(' ')]
	else:
		synonyms = [s.lower().strip() for s in synonyms.split('\n')]
	adwords.extend(synonyms)
	return adwords

def get_target_nodes(adword):
	rows = zmscontext.attr('records')
	zmsnodes = [
		zmscontext.getLinkObj(row.get('url')) for row in rows \
			if ( adword in list(get_adwords_of_row(row)) ) \
			and not row.get('url').startswith('http')
	]
	return zmsnodes

def get_target_extlinks(adword):
	rows = zmscontext.attr('records')
	extlinks = [
		{
			'index_html':row.get('url'),
			'title':row.get('title'),
			'attr_dc_description':row.get('attr_dc_description')
		} for row in rows \
			if ( adword in list(get_adwords_of_row(row)) ) \
			and row.get('url').startswith('http')
	]
	return extlinks


target_nodes = get_target_nodes(adword)
target_extlinks = get_target_extlinks(adword)

targets_as_dict  = {}
targets = {'adword':adword, 'docs':[] }

if target_nodes:
	# Extract content from target node
	for target_node in target_nodes:
		if target_node.isActive(zmscontext.REQUEST):
			titleimage_url = target_node.attr('titleimage') and target_node.attr('titleimage').getHref(zmscontext.REQUEST) or ''
			if not titleimage_url:
				document_images = target_node.getObjChildren('e',zmscontext.REQUEST,['ZMSGraphic'])
				if document_images:
					titleimage_url = document_images[0].attr('img').getHref(zmscontext.REQUEST)
			target_as_dict  =  {
				'title': target_node.attr('seotitle_tag') or target_node.attr('title'),
				'attr_dc_description': target_node.attr('seometa_tag') or target_node.attr('attr_dc_description') or target_node.attr('text'),
				'index_html': target_node.getHref2IndexHtml(zmscontext.REQUEST),
				'titleimage': titleimage_url
			}
			targets['docs'].append({'doc':target_as_dict})

if target_extlinks:
	# Extract content from adwords dataset
	for target_extlink in target_extlinks:
		target_as_dict = {
			'title': target_extlink['title'],
			'attr_dc_description': target_extlink['attr_dc_description'],
			'index_html': target_extlink['index_html'],
			'titleimage': ''
		}
		targets['docs'].append({'doc':target_as_dict})


return targets
