################################################################################
# IZMSRepositoryProvider.py
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
from builtins import map
from builtins import str
from zope.interface import Interface

def increaseVersion(v='0.0.0',d=2):
  try:
    l = [int(x) for x in v.split('.')]
    l[d] = l[d]+1
    return '.'.join([str(x) for x in l])
  except:
    return v

class IZMSRepositoryProvider(Interface):

  pass