################################################################################
# _metacmdmanager.py
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
import urllib

################################################################################
################################################################################
###
###   Class
###
################################################################################
################################################################################
class MetacmdObject:

    ############################################################################
    #  MetacmdObject.manage_executeMetacmd:
    #
    #  Execute Meta-Command.
    ############################################################################
    def manage_executeMetacmd(self, custom, lang, REQUEST, RESPONSE):
      """ MetacmdObject.manage_executeMetacmd """
      message = ''
      target = self
      
      # Execute.
      # --------
      metaCmd = self.getMetaCmd(name=custom)
      if metaCmd is not None:
        # Execute directly.
        if metaCmd.get('exec',0) == 1:
          ob = getattr(self,metaCmd['id'],None)
          if ob.meta_type in ['DTML Method','DTML Document']:
            value = ob(self,REQUEST,RESPONSE)
          elif ob.meta_type in ['External Method','Page Template','Script (Python)']:
            value = ob()
          if type(value) is str:
            message = value
          elif type(value) is tuple:
            target = value[0]
            message = value[1]
        # Execute redirect.
        else:
          params = {'lang':REQUEST.get('lang'),'id_prefix':REQUEST.get('id_prefix'),'ids':REQUEST.get('ids',[])}
          return RESPONSE.redirect(self.url_append_params(metaCmd['id'],params,sep='&'))
      
      # Return with message.
      message = urllib.quote(message)
      return RESPONSE.redirect('%s/manage_main?lang=%s&manage_tabs_message=%s'%(target.absolute_url(),lang,message))

################################################################################
