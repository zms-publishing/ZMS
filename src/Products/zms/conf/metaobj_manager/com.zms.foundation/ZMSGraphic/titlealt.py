## Script (Python) "ZMSGraphic.titlealt"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=zmscontext=None
##title=py: DC.Title.Alt
##
# --// BO titlealt //--

from Products.zms import standard
try:
    titlealt = standard.string_maxlen(zmscontext.attr('text'),24)
    img = zmscontext.attr('img')
    if titlealt:
        if len(titlealt) < 24:
            return titlealt
        else:
            return '%s...'%titlealt
    else:
        return img.getFilename() 
except:
    return zmscontext.display_type()

# --// EO titlealt //--
