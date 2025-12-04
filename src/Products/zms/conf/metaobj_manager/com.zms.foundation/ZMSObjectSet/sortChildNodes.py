## Script (Python) "ZMSObjectSet.sortChildNodes"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=zmscontext=None,options=None
##title=py: Sort record-set.
##
# --// sortChildNodes //--

from Products.zms import standard

request = container.REQUEST
records = options.get('records')
prepare = options.get('prepare',True)

qorder = request.get('qorder','')
qorderdir = request.get('qorderdir','')
if not qorder:
  qorderdefault = zmscontext.attr('record_order_default')
  if qorderdefault.find(':')>=0:
    qorder = qorderdefault[:qorderdefault.find(':')]
    qorderdir = qorderdefault[qorderdefault.find(':')+1:]
  qorder = standard.get_session_value(zmscontext,'qorder%s'%zmscontext.id,qorder)
  qorderdir = standard.get_session_value(zmscontext,'qorderdir%s'%zmscontext.id,qorderdir)
if records and qorder and qorderdir:
  if prepare:
    records = [{qorder:x.attr(qorder),'ob':x} for x in records]
  [standard.operator_setitem(x,qorder,'None') for x in records if x.get(qorder) is None]
  records = standard.sort_list(records,qorder,qorderdir)
  if prepare:
    records = [x['ob'] for x in records]
  request.set('qorder',qorder)
  request.set('qorderdir',qorderdir)

return records

# --// /sortChildNodes //--
