## Script (Python) "ZMSObjectSet.recordSet_Prepare"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=zmscontext=None,options=None
##title=py: Prepare record-set.
##
# --// recordSet_Prepare //--

from Products.zms import standard

request = zmscontext.REQUEST
lang = request['lang']
session = request.SESSION

records = []
attr_ids = [x['id'] for x in zmscontext.attr('record_attrs')]+['change_uid','change_dt']
buff = {}
for childNode in zmscontext.getChildNodes(request):
  meta_id = childNode.meta_id
  if not meta_id in buff:
    buff[meta_id] = {}
    for attr_id in attr_ids:
      objAttr = childNode.getObjAttr(attr_id)
      buff[meta_id][objAttr['id']] = {'id':objAttr['id'],'attr_name':childNode.getObjAttrName(objAttr,lang)}
  obj_version = childNode.getObjVersion(request)
  record = {'__id__':childNode.id}
  objAttrs = buff[meta_id]
  for objAttr in objAttrs.values():
    record[objAttr['id']] = getattr(obj_version,objAttr['attr_name'],None)  
  records.append(record)
res = records
request.set('res',res)

# init filter from request.
self = zmscontext
REQUEST = request
index = 0
for filterIndex in range(100):
    for filterStereotype in ['attr', 'op', 'value']:
          requestkey = 'filter%s%i'%(filterStereotype, filterIndex)
          sessionkey = '%s_%s'%(requestkey, self.id)
          if REQUEST.get('btn') is None:
            # get value from session 
            requestvalue = standard.get_session_value(self, sessionkey, '')
            # set request-value
            REQUEST.set(requestkey, requestvalue)
          else:
            # reset session-value
            standard.set_session_value(self, sessionkey, '')
            # get value from request
            requestvalue = REQUEST.form.get(requestkey, '')
            # reset value
            if REQUEST.get('btn') == 'BTN_RESET':
              requestvalue = ''
            # set request-/session-values for new index
            requestkey = 'filter%s%i'%(filterStereotype, index)
            sessionkey = '%s_%s'%(requestkey, self.id)
            REQUEST.set(requestkey, requestvalue)
            standard.set_session_value(self, sessionkey, requestvalue)
            # increase index
            if filterStereotype == 'value' and requestvalue != '':
              index += 1
request.set('qfilters', index + 1)
standard.set_session_value(zmscontext,'qfilters_%s'%zmscontext.id, index + 1)
# apply filter
for filterIndex in range(100):
  suffix = '%i_%s'%(filterIndex,zmscontext.id)
  sessionattr = standard.get_session_value(zmscontext,'filterattr%s'%suffix,'')
  sessionop = standard.get_session_value(zmscontext,'filterop%s'%suffix,'%')
  sessionvalue = standard.get_session_value(zmscontext,'filtervalue%s'%suffix,'')
  if sessionattr and sessionvalue:
    res = standard.filter_list(res,sessionattr,sessionvalue,sessionop)

# Order
res = zmscontext.evalMetaobjAttr('sortChildNodes',records=res,prepare=False)

request.set('res',res)
return res

# --// /recordSet_Prepare //--
