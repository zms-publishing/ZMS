################################################################################
# _ziputil.py
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
################################################################################

# Imports.
from cStringIO import StringIO
from types import StringTypes
import zipfile
# Product Imports.
import _globals


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
_ziputil.importZip2Zodb:

Extracts and imports zip-file to zodb.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def importZip2Zodb(root, data):
  if type( data) in StringTypes:
    data = StringIO( data)
  zf = zipfile.ZipFile( data, 'r')
  for name in zf.namelist():
    container = root
    ids = name.split('/')
    if len(ids) > 1:
      for id in ids[:-1]:
        if id not in container.objectIds():
          container.manage_addFolder(id=id)
        container = getattr(container,id)
    id = ids[-1]
    if id:
      file = zf.read( name)
      mt, enc  = _globals.guess_contenttype( id, file)
      if id in container.objectIds():
        container.manage_delObjects( [id])
      if mt.startswith('image'):
        file = container.manage_addImage(id=id,file=file)
      else:
        file = container.manage_addFile(id=id,file=file)

################################################################################