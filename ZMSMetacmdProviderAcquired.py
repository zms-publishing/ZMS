################################################################################
# ZMSMetacmdProviderAcquired.py
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
import zope.interface
# Product Imports.
import IZMSMetacmdProvider, ZMSMetacmdProvider


################################################################################
################################################################################
###
###   Class
###
################################################################################
################################################################################
class ZMSMetacmdProviderAcquired(
        ZMSMetacmdProvider.ZMSMetacmdProvider):
    zope.interface.implements(
        IZMSMetacmdProvider.IZMSMetacmdProvider)

    # Properties.
    # -----------
    meta_type = 'ZMSMetacmdProviderAcquired'

    ############################################################################
    #  ZMSMetacmdProviderAcquired.__init__: 
    #
    #  Constructor.
    ############################################################################
    def __init__(self, commands=[]):
      self.id = 'metacmd_manager'

    def getMetaCmdDescription(self, id=None, name=None):
       """ getMetaCmdDescription """
       return self.getPortalMaster().getMetaCmdDescription(id,name)

    def getMetaCmdIds(self, sort=True):
       return self.getPortalMaster().getMetaCmdIds(sort)

    def getMetaCmds(self, context=None, stereotype='', sort=True):
      metaCmds = self.getPortalMaster().getMetaCmds(context,stereotype,sort)
      for metaCmd in metaCmds:
        metaCmd['acquired'] = 1
      return metaCmds

################################################################################