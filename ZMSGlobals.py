################################################################################
# ZMSGlobals.py
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
from App.Common import package_home
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from types import StringTypes
import Globals
import os
import zExceptions
# Product Imports.
import standard
import _pilutil

__all__= ['ZMSGlobals']

################################################################################
################################################################################
###
###   class ZMSGlobals:
###
################################################################################
################################################################################
class ZMSGlobals:


    """
    Returns util with PIL functions.
    """
    def pilutil( self):
      return _pilutil.pilutil(self)


    """
    Returns util to handle zms3.extensions
    """
    def extutil(self):
      import _extutil
      return _extutil.ZMSExtensions()


    """
    Executes plugin.
    @param path: the plugin path in $ZMS_HOME/plugins/
    @type path: C{string}
    @param options: the options
    @type options: C{dict}
    """
    def getPlugin( self, path, options={}):
      # Check permissions.
      request = self.REQUEST
      authorized = path.find('..') < 0
      if not authorized:
        raise zExceptions.Unauthorized
      # Execute plugin.
      try:
        class StaticPageTemplateFile(PageTemplateFile):
          def setEnv(self,context,options):
            self.context = context
            self.options  = options
          def pt_getContext(self):
            root = self.context.getPhysicalRoot()
            context = self.context
            options = self.options
            c = {'template': self,
                 'here': context,
                 'context': context,
                 'options': options,
                 'root': root,
                 'request': getattr(root, 'REQUEST', None),
                 }
            return c
        filename = os.path.join(package_home(globals()),'plugins',path)
        pt = StaticPageTemplateFile(filename)
        pt.setEnv(self,options)
        rtn = pt.pt_render(extra_context={'here':self,'request':self.REQUEST})
      except:
        rtn = standard.writeError( self, '[getPlugin]')
      return rtn

    """
    Check if feature toggle is set.
    @rtype: C{boolean}
    """ 
    def isFeatureEnabled(self, feature=''):
    
      # get conf from current client
      confprop = self.breadcrumbs_obj_path(False)[0].getConfProperty('ZMS.Features.enabled','')
      features = confprop.replace(',',';').split(';')
      # get conf from top master if there is no feature toggle set at client
      if len(features)==1 and features[0].strip()=='':
        confprop = self.breadcrumbs_obj_path(True)[0].getConfProperty('ZMS.Features.enabled','')
        features = confprop.replace(',',';').split(';')
    
      if len(filter(lambda ob: ob.strip()==feature.strip(), features))>0:
        return True
      else:
        return False
