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
adword = zmscontext.REQUEST.get('adword').lower()

def get_target_nodes(adword):
	rows = zmscontext.attr('records')
	zmsnodes = [zmscontext.getLinkObj(row.get('url')) for row in rows if (row.get('adword').lower()==adword or (adword in row.get('synonyms').lower())) ]
	return zmsnodes


# ##########################################################
# TODO: process synonyms and multiple node of same keyword
# ##########################################################
target_nodes = get_target_nodes(adword)
targets_as_dict  = {}
targets = {'adword':adword, 'docs':[] }

if target_nodes:
	# Extract content form target
	for target_node in target_nodes:
		titleimage_url = target_node.attr('titleimage') and target_node.attr('titleimage').getHref(zmscontext.REQUEST) or ''
		if not titleimage_url:
			document_images = target_node.getObjChildren('e',zmscontext.REQUEST,['ZMSGraphic'])
			if document_images:
				titleimage_url = document_images[0].attr('img').getHref(zmscontext.REQUEST)
		
		target_as_dict  =  {
			'title': target_node.attr('title'),
			'attr_dc_description': target_node.attr('attr_dc_description') or target_node.attr('text'),
			'index_html': target_node.getHref2IndexHtml(zmscontext.REQUEST),
			'titleimage': titleimage_url
		}
		targets['docs'].append({'doc':target_as_dict})

return targets
