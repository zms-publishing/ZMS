################################################################################
# ZMSWorkflowProviderAcquired.py
#
# $Id:$
# $Name:$
# $Author:$
# $Revision:$
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
from zope.interface import implements
# Product Imports.
import IZMSWorkflowProvider
import ZMSItem


class ZMSWorkflowProviderAcquired(
        ZMSItem.ZMSItem):
    implements(IZMSWorkflowProvider.IZMSWorkflowProvider)

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Properties
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    meta_type = 'ZMSWorkflowProviderAcquired'
    icon = "misc_/zms/ZMSWorkflowProvider.png"

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Management Options
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    manage_sub_options = (
    )

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    ZMSWorkflowProviderAcquired.__init__: 
    
    Constructor.
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def __init__(self):
      self.id = 'workflow_manager'


    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    ZMSWorkflowProviderAcquired.getAutocommit
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def getAutocommit(self):
      portalMaster = self.getPortalMaster()
      if portalMaster is not None:
        workflow_manager = portalMaster.workflow_manager
        return workflow_manager.getAutocommit()
      return 1


    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    ZMSWorkflowProviderAcquired.getNodes
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def getNodes(self):
      return self.getPortalMaster().workflow_manager.getNodes()


    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    ZMSWorkflowProviderAcquired.writeProtocol
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def writeProtocol(self, entry):
      self.getPortalMaster().workflow_manager.writeProtocol(entry)

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    @see IZMSWorkflowProvider.getActivities()
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def getActivities(self):
      return self.getPortalMaster().workflow_manager.getActivities()

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    @see IZMSWorkflowProvider.getActitiesIds()
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def getActivitiesIds(self):
      return self.getPortalMaster().workflow_manager.getActivitiesIds()
  
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    @see IZMSWorkflowProvider.getActivity()
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def getActivity(self, id):
      return self.getPortalMaster().workflow_manager.getActivity(id)

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    @see IZMSWorkflowProvider.getTransitions()
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def getTransitions(self):
      return self.getPortalMaster().workflow_manager.getTransitions()

################################################################################
