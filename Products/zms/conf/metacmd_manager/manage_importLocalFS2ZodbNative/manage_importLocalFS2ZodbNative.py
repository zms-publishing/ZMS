import os
from Products.zms import _fileutil
from Products.zms import zopeutil

MAX_FILE_SIZE = 1024 * 1024


def manage_importLocalFS2ZodbNative(self):
  request = self.REQUEST
  request.set('lang', request.get('lang', self.getPrimaryLanguage()))

  extension_map = {
    '.dtml': 'DTML Method',
    '.zpt': 'Page Template',
    '.py': 'Script (Python)',
    '.zsql': 'Z SQL Method',
  }
  image_extensions = ['.avif', '.bmp', '.gif', '.ico', '.jpeg', '.jpg', '.png', '.svg', '.tif', '.tiff', '.webp']
  traversable_meta_types = ['Folder', 'ZMS', 'ZMSMetacmdProvider', 'ZMSMetamodelProvider', 'ZMSWorkflowProvider']

  def normalize(path):
    path = path.replace('\\', '/')
    if path != '/':
      path = path.rstrip('/')
    return path or '/'

  def list_files(base_path):
    items = []
    if not base_path or not os.path.isdir(base_path):
      return items
    base_path = normalize(base_path)
    for root, dirs, files in os.walk(base_path):
      dirs.sort()
      files.sort()
      for name in files:
        abs_path = normalize(os.path.join(root, name))
        rel_path = normalize(os.path.relpath(abs_path, base_path))
        items.append({'abs_path': abs_path, 'rel_path': rel_path, 'status': []})
    return items

  def find_node_by_physical_path(node, target_path):
    path = '/'.join(node.getPhysicalPath())
    if path == target_path:
      return node
    if node.meta_type in traversable_meta_types:
      for child in node.objectValues():
        found = find_node_by_physical_path(child, target_path)
        if found is not None:
          return found
    return None

  def infer_meta_type(filename, content_type):
    ext = os.path.splitext(filename)[1].lower()
    meta_type = extension_map.get(ext)
    if meta_type is not None:
      return meta_type
    if ext in image_extensions:
      return 'Image'
    if content_type and content_type.startswith('image/'):
      return 'Image'
    return 'File'

  def get_target_folder(base_obj, rel_dir):
    folder = base_obj
    if not rel_dir or rel_dir == '.':
      return folder
    for part in [x for x in rel_dir.split('/') if x]:
      if part not in folder.objectIds():
        zopeutil.addObject(folder, 'Folder', part, part, '')
      folder = getattr(folder, part)
      if folder.meta_type != 'Folder':
        raise Exception('Target path segment is not a Folder: %s' % part)
    return folder

  def import_file(source_path, source_root, target_root, allow_overwrite=False):
    source_path = normalize(source_path)
    source_root = normalize(source_root)
    rel_path = normalize(os.path.relpath(source_path, source_root))
    rel_dir = normalize(os.path.dirname(rel_path))
    filename = os.path.basename(source_path)

    file_size = os.path.getsize(source_path)
    if file_size > MAX_FILE_SIZE:
      raise Exception('File size exceeds limit (%i bytes > %i bytes): %s' % (file_size, MAX_FILE_SIZE, rel_path))

    data, content_type, encoding, fsize = _fileutil.readFile(source_path, mode='b', threshold=-1)
    meta_type = infer_meta_type(filename, content_type)

    obj_id = filename
    if meta_type in ['DTML Method', 'Page Template', 'Script (Python)', 'Z SQL Method']:
      obj_id = os.path.splitext(filename)[0]

    folder = get_target_folder(target_root, rel_dir)

    if obj_id in folder.objectIds():
      if not allow_overwrite:
        raise Exception('Object already exists and overwrite is disabled: %s/%s' % ('/'.join(folder.getPhysicalPath()), obj_id))
      folder.manage_delObjects(ids=[obj_id])

    zopeutil.addObject(folder, meta_type, obj_id, filename, data)
    return {'rel_path': rel_path, 'meta_type': meta_type, 'target_path': '/'.join(folder.getPhysicalPath()) + '/' + obj_id}

  source_root = request.get('path', self.getINSTANCE_HOME())
  target_path = request.get('zodb_path', '/'.join(self.getHome().getPhysicalPath()))
  execute = request.get('btn') == 'execute'
  allow_overwrite = str(request.get('allow_overwrite', '0')).lower() in ['1', 'true', 'on', 'yes']

  file_items = list_files(source_root)

  if execute:
    statuses = []
    target_root = find_node_by_physical_path(self.getHome(), normalize(target_path))
    if target_root is None:
      return self.str_json(['Error: Target ZODB path not found: %s' % target_path])

    selected = request.get('ids', [])
    for item in file_items:
      if item['abs_path'] in selected:
        try:
          result = import_file(item['abs_path'], source_root, target_root, allow_overwrite=allow_overwrite)
          statuses.append(['<span class="badge badge-success">Done</span> %s (%s) -> %s' % (result['rel_path'], result['meta_type'], result['target_path'])])
        except Exception as e:
          statuses.append(['<span class="badge badge-danger">Error</span> %s -> %s' % (item['rel_path'], str(e))])
    return self.str_json(statuses)

  html = ''
  html += '<!DOCTYPE html>'
  html += '<html lang="en">'
  html += self.zmi_html_head(self, request)
  html += """
<script>
  function btn_execute_click() {
    var allow_overwrite = $("input[name='allow_overwrite']").is(':checked') ? '1' : '0';
    $("input[name='ids:list']:checked").each( function() {
        var v = $(this).attr("value");
        var $td = $("td:last",$(this).parents("tr")[0]);
        var p = {'btn':'execute','ids:list':v,'path':$("input[name=path]").val(),'zodb_path':$("input[name=zodb_path]").val(),'allow_overwrite':allow_overwrite};
        $.ajax({
          url:'manage_importLocalFS2ZodbNative',
          data:p,
          timeout:30000,
          error: function (xhr, ajaxOptions, thrownError) {
              $td.html(''
                + getZMILangStr('CAPTION_ERROR')+'<hr/> '
                + '<code>' + xhr.status + ': ' + thrownError + '</code>');
            },
          success:function(response) {
              var l = eval('('+response+')');
              $td.html(l.join('<br>'));
            }
        });
      });
    return false;
  }
</script>
  """
  html += '<body class="%s">' % (' '.join(['zmi', request['lang'], self.meta_id]))
  html += self.zmi_body_header(self, request, options=[{'action': '#', 'label': 'Import LocalFS to ZODB...'}])
  html += '<div id="zmi-tab">'
  html += self.zmi_breadcrumbs(self, request)
  html += '<form class="form-horizontal" method="post" enctype="multipart/form-data">'
  html += '<div class="card">'
  html += '<legend>Import LocalFS to ZODB</legend>'

  html += '' \
    + '<div class="form-group row card-body">' \
    + '<label class="col-sm-2 control-label mandatory"><span>LocalFS Path</span></label>' \
    + '<div class="col-sm-10">' \
    + '<input class="form-control" id="path" name="path" value="' + request.get('path', self.getINSTANCE_HOME()) + '">' \
    + '</div><!-- .col-sm-10 -->' \
    + '</div><!-- .form-group -->' \
    + '<div class="form-group row card-body">' \
    + '<label class="col-sm-2 control-label mandatory"><span>Target ZODB Path</span></label>' \
    + '<div class="col-sm-10">' \
    + '<input class="form-control" id="zodb_path" name="zodb_path" value="' + request.get('zodb_path', '/'.join(self.getHome().getPhysicalPath())) + '">' \
    + '</div><!-- .col-sm-10 -->' \
    + '</div><!-- .form-group -->' \
    + '<div class="form-group row card-body">' \
    + '<label class="col-sm-2 control-label"><span>Safety</span></label>' \
    + '<div class="col-sm-10">' \
    + '<div class="form-check">' \
    + '<input class="form-check-input" type="checkbox" id="allow_overwrite" name="allow_overwrite" value="1" %s>' % (['', 'checked="checked"'][int(allow_overwrite)]) \
    + '<label class="form-check-label" for="allow_overwrite">Allow overwrite of existing objects</label>' \
    + '</div>' \
    + '<small class="form-text text-muted">Maximum file size per import: %i bytes</small>' % MAX_FILE_SIZE \
    + '</div><!-- .col-sm-10 -->' \
    + '</div><!-- .form-group -->' \
    + '<div class="form-row">' \
    + '<div class="controls save">' \
    + '<button type="submit" name="btn" class="btn btn-secondary" value="%s">%s</button> ' % (self.getZMILangStr('BTN_REFRESH'), self.getZMILangStr('BTN_REFRESH')) \
    + '<button type="button" name="btn" class="btn btn-danger" value="return %s" onclick="btn_execute_click()">%s</button> ' % (self.getZMILangStr('BTN_EXECUTE'), self.getZMILangStr('BTN_EXECUTE')) \
    + '</div><!-- .controls.save -->' \
    + '</div><!-- .form-row -->'

  html += '<table class="table">'
  html += '<tr>'
  html += '''<th class="text-center" style="width: 5rem;">
            <div class="btn-group">
              <span class="btn btn-secondary" title="%s/%s" onclick="zmiToggleSelectionButtonClick(this)"><i class="fas fa-check-square"></i></span>
            </div>
          </th>''' % (self.getZMILangStr('BTN_SLCTALL'), self.getZMILangStr('BTN_SLCTNONE'))
  html += '<th class="align-middle" style="max-width: calc(33% - 15rem);">LocalFS File</th>'
  html += '<th class="align-middle text-center" style="width: 10rem;">Mapped<br/>Type</th>'
  html += '<th class="align-middle" style="max-width: calc(33% - 15rem);">Target</th>'
  html += '<th class="align-middle" style="max-width: calc(33% - 15rem);">Status</th>'
  html += '</tr>'
  html += '\n'.join([
      '''<tr>
            <td class="text-center bg-light"><input type="checkbox" name="ids:list" value="%s" checked="checked"/></td>
            <td><span class="text-truncate" title="%s">%s</span></td>
            <td class="text-center">%s</td>
            <td><span class="text-truncate">%s/%s</span></td>
            <td>%s</td>
        </tr>''' % (
      x['abs_path'],
      x['rel_path'],
      x['rel_path'],
      infer_meta_type(os.path.basename(x['abs_path']), None),
      request.get('zodb_path', '/'.join(self.getHome().getPhysicalPath())),
      os.path.dirname(x['rel_path']),
      '<br>'.join(x['status']),
      ) for x in file_items])
  html += '</table><!-- .table -->'

  html += '</div>'
  html += '</form><!-- .form-horizontal -->'
  html += '</div><!-- #zmi-tab -->'
  html += self.zmi_body_footer(self, request)
  html += '</body>'
  html += '''<style>
    #zmi-tab table.table td {
        max-width: 33vw;
        word-break: break-word;
    }
    #zmi-tab table.table td .text-truncate {
        display: inline-block;
        max-width: 33vw;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        vertical-align: bottom;
    }
    </style>
    '''
  html += '</html>'

  return html
