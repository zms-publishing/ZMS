## Script (Python) "captcha_validate"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=content_type='json'
##title=Validate Captcha
##
# --// captcha_validate //--
request = container.REQUEST
RESPONSE =  request.RESPONSE
captcha_is_valid = context.captcha_func(context, do='validate')
if content_type=='json':
	RESPONSE.setHeader('Cache-Control', 'public, max-age=0')
	RESPONSE.setHeader('Content-Type', 'application/json; charset=utf-8')
	return captcha_is_valid
else:
	if 'true' in str(captcha_is_valid):
		return True
	else:
		return False
# --// /captcha_validate //--
