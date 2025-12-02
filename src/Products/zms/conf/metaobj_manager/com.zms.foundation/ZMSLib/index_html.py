## Script (Python) "index_html"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Index-Html
##
# --// index_html //--

request = container.REQUEST
RESPONSE =  request.RESPONSE
RESPONSE.redirect(context.objectValues(['ZMS'])[0].getHref2IndexHtml(request,deep=False), status=301)

# --// /index_html //--
