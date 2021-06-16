## Script (Python) "doi"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=DOI-Redirect
##
# --// doi //--

# README: To use redirecting short urls like /doi/10.1109/5.771073 or /doi/faq 
# based on ZMSIndex, please add a meta-attribute 'attr_dc_identifier_doi' to the 
# document nodes definition (ZMSFolder, ZMSDocument) and add this meta-attribute-
# name to the ZMSIndex 'Attributes' list. You can fill the new attribute implicitly
# with any other (existing) attribute value by declaring it's type as Py-Script 
# and using following code snippet:
# ---------------------
#  from Products.zms import standard
#  return standard.id_quote(zmscontext.attr('titlealt'))
# ---------------------
# After REINDEXING the ZMSIndex contains a new field index 'zcat_attr_dc_identifier_doi'. 
# Based on this additional index any indexed string can be resolved as redirect to 
# the path oft its containing document.

from Products.zms import standard
request = container.REQUEST
RESPONSE =  request.RESPONSE
zmscontext = context.content
path_ = 'index_html'

if request['traverse_subpath']:
  path_ = standard.id_quote('_'.join(request['traverse_subpath']))

catalog = context.zcatalog_index
query = {'zcat_attr_dc_identifier_doi':path_}
rows = catalog(query)

for x in rows:
  # ### test ####
  # print x['get_uid']
  # print context.content.getLinkObj('{$%s}'%x['get_uid'])
  # print context.content.getLinkObj('{$%s}'%x['get_uid']).absolute_url()
  # return printed
  # #############
  ob = zmscontext.getLinkObj('{$%s}'%x['get_uid'])
  RESPONSE.redirect(ob.absolute_url())
  return standard.FileFromData(zmscontext,ob.absolute_url())

# Return a string identifying this script.
return standard.FileFromData(zmscontext,"'%s' not found!"%path_)

# --// /doi //--
