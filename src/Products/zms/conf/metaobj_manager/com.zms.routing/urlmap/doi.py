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
response =  request.RESPONSE
zmscontext = context.content
id = ''
pth = container.content.absolute_url()

if request['traverse_subpath']:
    s = request['traverse_subpath']
    id = '/'.join(s)

try:
    pth = context.url_mapping.get_path_by_id(zmscontext=zmscontext,id=id)
except:
    pass

## REDIRECT TO LATEST ZMS OBJECT PATH
response.redirect(pth, status=301, lock=True)

## TEST: id = 'e66699' | 'uid:cc493590-0e7e-4cb6-ac8e-d6d79958fc3f'
# id = 'uid:cc493590-0e7e-4cb6-ac8e-d6d79958fc3f'
# pth = context.url_mapping.get_path_by_id(zmscontext=zmscontext,id=id)
# return pth

# --// /doi //--
