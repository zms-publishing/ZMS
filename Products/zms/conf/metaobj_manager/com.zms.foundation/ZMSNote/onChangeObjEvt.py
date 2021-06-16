## Script (Python) "ZMSNote.onChangeObjEvt"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=zmscontext
##title=py: Event: onChangeObj
##
# --// BO onChangeObjEvt //--

request = zmscontext.REQUEST
zmscontext.commitObj(request)

# --// EO onChangeObjEvt //--
