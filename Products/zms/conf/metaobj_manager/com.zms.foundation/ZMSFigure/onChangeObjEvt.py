## Script (Python) "ZMSFigure.onChangeObjEvt"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=zmscontext=None,options=None
##title=py: Event: onChange
##
# --// onChangeObjEvt //--

from Products.zms import pilutil

if pilutil.enabled():
	request = zmscontext.REQUEST
	lang =  request.get('lang',zmscontext.getPrimaryLanguage())
	hiresKey = 'img_%s'%(lang)
	loresKey = '_img_%s'%(lang)
	maxdim = int(zmscontext.getConfProperty('InstalledProducts.pil.thumbnail.max',480))
	img = zmscontext.attr('img')
	imgwidth = img and int(img.getWidth()) or 0;
	imgheight = img and int(img.getHeight()) or 0;

	# new picture added
	if int(request.get('del_img_%s'%(lang),0))==1:
		zmscontext.attr('_img',None)
	if (imgwidth < maxdim or imgheight < maxdim):
		zmscontext.attr('_img',None)
	if (hiresKey in request.keys()) and (imgwidth > maxdim or imgheight > maxdim):
		from Products.zms import pilutil
		return pilutil.generate_preview(zmscontext, 'img', '_img', maxdim)

return None

# --// /onChangeObjEvt //--
