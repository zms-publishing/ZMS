## Script (Python) "ZMSLib.uploadMedia"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=zmscontext=None
##title=py: Upload: Media
##
# --// BO uploadMedia //--
from Products.zms import pilutil

result = {}
temp_folder = context.temp_folder
request = context.REQUEST
base_url = request.get('SERVER_URL')
form_id = request.get('form_id')
file = request.get('file')

def resize_image(context, orig, maxdims):
  width = orig.getWidth()
  height = orig.getHeight()
  while width > maxdims or height > maxdims:
    if width > maxdims:
      height = int(height * maxdims / width)
      width = maxdims
    elif height > maxdims:
      width = int(width * maxdims / height)
      height = maxdims
  size = (width,height)
  blob = pilutil.resize( orig, size)
  return blob

def create_blob(container, blob):
  filename = blob.getFilename()
  data = blob.getData()
  id = form_id + '_' + filename
  if id in container.objectIds():
    container.manage_delObjects(ids=[id])
  if blob.getContentType().startswith('image'):
    container.manage_addImage( id=id, title=filename, file=data)
  else:
    container.manage_addFile( id=id, title=filename, file=data)
  ob = getattr(container,id)
  d = {}
  d['content_type'] = blob.getContentType()
  d['filename'] = blob.getFilename()
  d['absolute_url'] = ob.absolute_url()[len(base_url):]
  return d

if file and file.filename:
  blobs = {}
  blob = context.FileFromData(file,file.filename)
  content_type = blob.getContentType()
  if content_type.startswith('image'):
    image = context.ImageFromData(file,file.filename)
    maxdims = int(context.getConfProperty('InstalledProducts.pil.thumbnail.max'))
    if image.getWidth() > maxdims:
      result['imghires'] = create_blob(temp_folder,image)
      result['image'] = create_blob(temp_folder,resize_image(context, image, maxdims))
    else:
      result['image'] = create_blob(temp_folder,image)
  else:
    result['file'] = create_blob(temp_folder,blob)

result['message'] = context.getZMILangStr( 'MSG_UPLOADED')
return context.str_json(result)

# --// EO uploadMedia //--
