## Script (Python) "captcha_validate"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Validate Captcha
##
# --// captcha_validate //--
request = container.REQUEST
RESPONSE =  request.RESPONSE
request.RESPONSE.setHeader('Cache-Control', 'public, max-age=0')
request.RESPONSE.setHeader('Content-Type', 'application/json; charset=utf-8')
return context.captcha_func(context, do='validate')
# --// /captcha_validate //--
