## Script (Python) "ontology.getLangStr"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=zmscontext=None,options=None
##title=py: Get Language String
##
# --// getLangStr //--
import Products.zms.standard as standard
request = context.REQUEST
response =  request.response
response.setHeader('content-type','text/html; charset=utf-8')
lang = request.get('lang',context.getPrimaryLanguage())
key = options.get('key','ontology.debug.default')

# Get Py-Script-Object
get_lang_dict = standard.operator_getattr(context.content.metaobj_manager, 'ontology.get_lang_dict')
# Execute Py-Script-Object
lang_dict = get_lang_dict()

return lang_dict.get(key,{'ger':key,'eng':key,'fra':key})[lang]

# --// /getLangStr //--
