## Script (Python) "calendar.get_events"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=zmscontext=None,options=None
##title=py: Process Events Data
##
# --// get_events //--
from Products.zms import standard
request = container.REQUEST
RESPONSE =  request.RESPONSE

fieldnames = ['col_id','start_time','end_time','title','description','location','url']
events=[]
res = zmscontext.events.attr('records')
for e in res:
    d={}
    for k in fieldnames:
        if "time" in k:
            d[k] = zmscontext.getLangFmtDate(e[k], lang='eng', fmt_str='%Y-%m-%d %H:%M')
        else:
            d[k] = e[k]
    events.append(d)

return events

# --// /get_events //--
