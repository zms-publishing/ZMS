## Script (Python) "ZMSRichtext.onChangeObjEvt"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=zmscontext=None
##title=py: Event: onChange-Object
##
# --// BO onChangeObjEvt //--

temp_folder = context.temp_folder
request = context.REQUEST

# Find images/files.
text = zmscontext.attr('text')
l = []
lt = []
for sp in ['src="', 'href="' ]:
  for s in text.split(sp):
    ref = s[:s.find('"')]
    if ref.find('/'+zmscontext.id+'/') >= 0:
      idmedia = ref.split('/')[-1]
      l.append(idmedia)
    elif ref.find('/'+temp_folder.id+'/') >= 0:
      lt.append(ref)

# Remove unused images/files.
ob_ids = zmscontext.objectIds(['File','Image'])
for ref in l:
  id = ref.split('/')[-1]
  if id in ob_ids:
    ob_ids.remove(id)
if len(ob_ids) > 0:
  zmscontext.manage_delObjects(ids=ob_ids)

# Add new images/files from temp_folder.
for ref in lt:
  id = ref.split('/')[-1]
  ob = getattr(temp_folder,id,None)
  if ob is not None:
    new_id = ob.title_or_id()
    new_title = ''
    new_data = ob.data
    if ob.meta_type == 'Image':
      zmscontext.manage_addImage( id=new_id, title=new_title, file=new_data)
    else:
      zmscontext.manage_addFile( id=new_id, title=new_title, file=new_data)
    temp_folder.manage_delObjects(ids=[id])
    text = text.replace('"'+ref+'"','"./'+zmscontext.id+'/'+new_id+'"')
zmscontext.attr('text',text)

# --// EO onChangeObjEvt //--
