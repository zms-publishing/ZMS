## Script (Python) "ontology.get_lang_dict"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST=None
##title=py: Get Language Dictionary
##
# --// get_lang_dict //--
request = context.REQUEST
# RESONSE = request.response
# RESONSE.setHeader('content-type','text/html; charset=utf-8')

res = context.content.getChildNodes(request,'ontology')[0].attr('records')
lang_dict = { i['key']:{'ger':i['ger'],'eng':i['eng'],'fra':i['fra']} for i in res }

if REQUEST is not None:
	REQUEST.RESPONSE.setHeader('Cache-Control','public, max-age=3600')
	REQUEST.RESPONSE.setHeader('Content-Type','text/plain; charset=utf-8')
	return context.content.str_json(lang_dict)
else:
	return lang_dict

# --// /get_lang_dict //--
