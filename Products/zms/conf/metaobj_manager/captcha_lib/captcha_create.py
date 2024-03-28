## Script (Python) "captcha_create"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=content_type='json'
##title=Create Captcha
##
# --// captcha_create //--
request = container.REQUEST
RESPONSE =  request.RESPONSE
request.RESPONSE.setHeader('Cache-Control', 'public, max-age=0')
request.RESPONSE.setHeader('Content-Type', 'application/json; charset=utf-8')
return context.captcha_func(context,do='create')
# --// /captcha_create //--
