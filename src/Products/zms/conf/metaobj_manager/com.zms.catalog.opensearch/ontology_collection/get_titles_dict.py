## Script (Python) "ontology_collection.get_titles_dict"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=zmscontext=None,options=None
##title=py: Get All Titles (Lang-Dict)
##
# --// get_titles_dict //--
from Products.zms import standard
request = container.REQUEST
RESPONSE =  request.RESPONSE

attropts = zmscontext.get_ontology_attropts()
titles_dict = {}
for attropt in attropts:
    t = attropt[1]
    t = t.split('&rsaquo; ')[-1]
    titles_dict[attropt[0]] = t
return titles_dict

# --// /get_titles_dict //--
