## Script (Python) "ZMSTable.onChangeObjEvt"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=zmscontext=None,options=None
##title=py: Event: onChange
##
# --// onChangeObjEvt //--

request = zmscontext.REQUEST
lang = request['lang']
table = zmscontext.attr('table')
ncols = max(map(lambda x: len(x), table))
weights = map(lambda x: 1, range( ncols))
for row in table:
    for cell in row:
        content = cell.get('content','')
        content = zmscontext.validateInlineLinkObj(content)
        cell['content'] = content
zmscontext.setObjProperty('table',table,lang)

# --// /onChangeObjEvt //--
