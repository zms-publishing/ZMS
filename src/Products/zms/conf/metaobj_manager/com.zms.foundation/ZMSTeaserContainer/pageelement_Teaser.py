## Script (Python) "pageelement_Teaser"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=here=None,request=None
##title=Template: Teaser
##
# --// BO pageelement_Teaser //--

request = container.REQUEST
RESPONSE =  request.RESPONSE

last_borderstyle = None
last_bgcolor_border = None
teaserElmnts = context.getTeaserElements()
if teaserElmnts:
  print('<div class="ZMSTeaserContainer">')
  for teaserElmnt in teaserElmnts:
    if teaserElmnt.meta_id in ['ZMSLinkElement','ZMSFile','ZMSTeaserElement']:
      name = 'pageelement_TeaserElement'
    else:
      name = 'bodyContentZMSCustom_%s'%teaserElmnt.meta_id
    method = getattr(teaserElmnt,name,None)
    if method is not None:
      method_result = method(teaserElmnt,request)
    else:
      method_result = teaserElmnt.getBodyContent(request)
    print(method_result)
  print('</div><!-- .ZMSTeaserContainer -->')

return printed

# --// EO pageelement_Teaser //--
