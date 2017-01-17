################################################################################
# ZMSMetacmdProvider.py
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
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PageTemplates import ZopePageTemplate
import copy
import os
import urllib
import zope.interface
# Product Imports.
import _fileutil
import _globals
import _zopeutil
import IZMSMetacmdProvider,IZMSConfigurationProvider,IZMSRepositoryProvider
import ZMSItem


# Example code.
# -------------

dtmlExampleCode = '<!-- @deprecated -->'

pageTemplateExampleCode = \
  '<!DOCTYPE html>\n' + \
  '<html lang="en">\n' + \
  '<tal:block tal:content="structure python:here.zmi_html_head(here,request)">zmi_html_head</tal:block>\n' + \
  '<body class="zmi">\n' + \
  '<tal:block tal:content="structure python:here.zmi_body_header(here,request)">zmi_body_header</tal:block>\n' + \
  '<div id="zmi-tab">\n' + \
  '<tal:block tal:content="structure python:here.zmi_breadcrumbs(here,request)">zmi_breadcrumbs</tal:block>\n' + \
  '<div style="clear:both;">&nbsp;</div>\n' + \
  '</div><!-- #zmi-tab -->\n' + \
  '<script>\n' + \
  '</script>\n' + \
  '<tal:block tal:content="structure python:here.zmi_body_footer(here,request)">zmi_body_footer</tal:block>\n' + \
  '</body>\n' + \
  '</html>\n'

pyScriptExampleCode = \
  '# Example code:\n' + \
  '\n' + \
  '# Import a standard function, and get the HTML request and response objects.\n' + \
  'from Products.PythonScripts.standard import html_quote\n' + \
  'request = container.REQUEST\n' + \
  'RESPONSE =  request.RESPONSE\n' + \
  '\n' + \
  '# Return a string identifying this script.\n' + \
  'print "This is the", script.meta_type, \'"%s"\' % script.getId(),\n' + \
  'if script.title:\n' + \
  '    print "(%s)" % html_quote(script.title),\n' + \
  'print "in", container.absolute_url()\n' + \
  'return printed\n' + \
  ''


################################################################################
################################################################################
###
###   Class
###
################################################################################
################################################################################
class ZMSMetacmdProvider(
        ZMSItem.ZMSItem):
    zope.interface.implements(
        IZMSConfigurationProvider.IZMSConfigurationProvider,
        IZMSMetacmdProvider.IZMSMetacmdProvider,
        IZMSRepositoryProvider.IZMSRepositoryProvider)

    # Properties.
    # -----------
    meta_type = 'ZMSMetacmdProvider'
    icon = "++resource++zms_/img/ZMSMetacmdProvider.png"
    icon_clazz = "icon-wrench"

    # Management Options.
    # -------------------
    manage_options_default_action = '../manage_customize'
    def manage_options(self):
      return map( lambda x: self.operator_setitem( x, 'action', '../'+x['action']), copy.deepcopy(self.aq_parent.manage_options()))

    def manage_sub_options(self):
      return (
        {'label': 'TAB_METACMD','action': 'manage_main'},
        )

    # Management Interface.
    # ---------------------
    manage = PageTemplateFile('zpt/ZMSMetacmdProvider/manage_main',globals()) 
    manage_main = PageTemplateFile('zpt/ZMSMetacmdProvider/manage_main',globals()) 
    manage_main_acquire = PageTemplateFile('zpt/ZMSMetacmdProvider/manage_main_acquire',globals()) 

    # Management Permissions.
    # -----------------------
    __administratorPermissions__ = (
		'manage_changeMetacmds', 'manage_main', 'manage_main_acquire'
		)
    __ac_permissions__=(
		('ZMS Administrator', __administratorPermissions__),
		)

    ############################################################################
    #  ZMSMetacmdProvider.__init__: 
    #
    #  Constructor.
    ############################################################################
    def __init__(self, commands=[]):
      self.id = 'metacmd_manager'
      self.commands = copy.deepcopy(commands)


    ############################################################################
    #
    #  CLOUD GET/SET
    #
    ############################################################################

    # --------------------------------------------------------------------------
    #  ZMSMetacmdProvider.cloud_get
    # --------------------------------------------------------------------------
    def cloud_get(self, id, artefacts=False):
      basepath = self.get_conf_basepath(self.id)
      filepath = os.path.join(basepath,id)
      filename = os.path.join(filepath,"__init__.py")
      metaCmd = {}
      if os.path.exists(filename):
        # Read python-representation of content-object
        f = open(filename,"r")
        py = f.read()
        f.close()
        # Analyze python-representation.
        exec(py)
        # Class
        metaCmd = {'id':id}
        d = eval("%s.__dict__"%self.id_quote(id.replace('.','_')))
        for k in filter(lambda x:not x.startswith("__") and not x in ['Attributes'],d.keys()):
          v = d[k]
          metaCmd[k] = v
        # Read artefacts.
        if artefacts:
          filepath = os.path.join(basepath,id)
          fileprefix = attr['id'].split('/')[-1]
          for file in os.listdir(filepath):
            if file.startswith('%s.'%fileprefix):
              filename = os.path.join(filepath,file)
              f = open(filename,"r")
              data = f.read()
              f.close()
              metaCmd['data'] = data
              break
      return metaCmd

    # --------------------------------------------------------------------------
    #  ZMSMetacmdProvider.cloud_sync
    #
    # Sync filesystem to ZODB.
    # --------------------------------------------------------------------------
    def cloud_sync(self, id):
      basepath = self.get_conf_basepath(self.id)
      metaCmd = self.__get_metacmd__(id)
      if metaCmd and not metaCmd.get('acquired',0):
        d = self.cloud_get(id,artefacts=True)
        if d:
          self.delMetaCmd(id)
          self.setMetaCmd(d)
          return id
      return None

    # --------------------------------------------------------------------------
    #  ZMSMetacmdProvider.cloud_import
    # --------------------------------------------------------------------------
    def cloud_import(self, ids):
      success = []
      for id in filter(lambda x:x in ids or len(ids)==0,self.getMetaCmdIds()):
        if self.cloud_sync(id):
          success.append(id)
      return self.getZMILangStr('MSG_IMPORTED')%('<em>%s</em>'%' '.join(success))

    # --------------------------------------------------------------------------
    #  ZMSMetacmdProvider.cloud_export
    # --------------------------------------------------------------------------
    def cloud_export(self, ids):
      basepath = self.get_conf_basepath(self.id)
      _fileutil.mkDir(basepath)
      success = []
      for id in filter(lambda x:x in ids or len(ids)==0,self.getMetaCmdIds()):
        metaCmd = self.getMetaCmd(id)
        if metaCmd and not metaCmd.get('acquired',0):
          # Recreate folder.
          filepath = os.path.join(basepath,id)
          if os.path.exists(filepath):
            _fileutil.remove(filepath)
          _fileutil.mkDir(filepath)
          # Write artefacts.
          fileexts = {'DTML Method':'.dtml', 'DTML Document':'.dtml', 'External Method':'.py', 'Page Template':'.zpt', 'Script (Python)':'.py', 'Z SQL Method':'.zsql'}
          fileprefix = id
          filename = os.path.join(filepath,"%s%s"%(fileprefix,fileexts.get(metaCmd['meta_type'],'')))
          data = metaCmd['data']
          f = open(filename,"w")
          f.write(data)
          f.close()
          # Write python-representation.
          py = []
          py.append('class %s:'%id)
          py.append('\t"""')
          py.append('\tpython-representation of ZMS-action %s'%metaCmd['id'])
          py.append('\t"""')
          py.append('')
          keys = filter(lambda x:x not in ['bobobase_modification_time','data'],metaCmd.keys())
          keys.sort()
          for key in keys:
            if metaCmd[key]:
              py.append('\t# %s'%key.capitalize())
              py.append('\t%s = %s'%(key,self.str_json(metaCmd[key],encoding="utf-8",formatted=True,level=2)))
              py.append('')
          py = '\n'.join(py)
          filename = os.path.join(filepath,"__init__.py")
          f = open(filename,"w")
          f.write(py)
          f.close()
          success.append(id)
      return self.getZMILangStr('MSG_EXPORTED')%('<em>%s</em>'%' '.join(success))


    """
    @see IRepositoryProvider
    """
    def provideRepository(self):
      r = {}
      for id in self.getMetaCmdIds():
        o = self.getMetaCmd(id)
        if o and not o.get('acquired',0):
          d = {}
          for k in o.keys():
            d[k] = o[k]
          r[id] = d
      return r

    """
    @see IRepositoryProvider
    """
    def updateRepository(self, id):
      pass


    ############################################################################
    #
    #  XML IM/EXPORT
    #
    ############################################################################

    # ------------------------------------------------------------------------------
    #  ZMSMetacmdProvider.importXml
    # ------------------------------------------------------------------------------
    def _importXml(self, item, createIfNotExists=1):
      id = item['id']
      if createIfNotExists == 1:
        
        # Delete existing object.
        try: self.delMetacmd(id)
        except: pass
        
        # Initialize attributes of new object.
        newId = id
        newAcquired = 0
        newRevision = item.get('revision','0.0.0')
        newName = item['name']
        newTitle = item.get('title','')
        newMethod = item['meta_type']
        newExec = item.has_key('exec') and item['exec']
        newDescription = item.get('description','')
        newIconClazz = item.get('icon_clazz','')
        newMetaTypes = item['meta_types']
        newRoles = item['roles']
        newNodes = item.get('nodes','{$}')
        newData = item['data']
        
        # Return with new id.
        return self.setMetacmd(None, newId, newAcquired, newRevision, newName, newTitle, newMethod, \
          newData, newExec, newDescription, newIconClazz, newMetaTypes, newRoles, \
          newNodes)

    def importXml(self, xml, createIfNotExists=1):
      v = self.parseXmlString(xml)
      if type(v) is list:
        for item in v:
          id = self._importXml(item,createIfNotExists)
      else:
        id = self._importXml(v,createIfNotExists)


    # ------------------------------------------------------------------------------
    #  ZMSMetacmdProvider.__get_metacmd__
    # ------------------------------------------------------------------------------
    def __get_metacmd__(self, id):
      return (filter(lambda x:x['id']==id,self.commands)+[None])[0]


    # ------------------------------------------------------------------------------
    #  ZMSMetacmdProvider.delMetacmd:
    # 
    #  Delete Action specified by given Id.
    # ------------------------------------------------------------------------------
    def delMetacmd(self, id):
      
      # Catalog.
      obs = self.commands
      old = filter(lambda x: x['id']==id, obs)
      if len(old) > 0:
        obs.remove(old[0])
      self.commands = obs
      self.commands = copy.deepcopy(self.commands) # Make persistent.
      
      # Remove Template.
      container = self.aq_parent
      _zopeutil.removeObject(container,id)
      
      # Return with empty id.
      return ''

    # ------------------------------------------------------------------------------
    #  ZMSMetacmdProvider.setMetacmd:
    #
    #  Set/add Action specified by given Id.
    # ------------------------------------------------------------------------------
    def setMetacmd(self, id, newId, newAcquired, newRevision='0.0.0', newName='', newTitle='', newMethod=None, \
          newData=None, newExec=0, newDescription='', newIconClazz='', newMetaTypes=[], \
          newRoles=['ZMSAdministrator'], newNodes='{$}'):
      
      # Catalog.
      obs = self.commands
      old = filter(lambda x: x['id'] in [id, newId], obs)
      if len(old) > 0:
        obs.remove(old[0])
      
      # Values.
      new = {}
      new['id'] = newId
      new['acquired'] = newAcquired
      new['revision'] = newRevision
      new['name'] = newName
      new['title'] = newTitle
      new['description'] = newDescription
      new['icon_clazz'] = newIconClazz
      new['meta_types'] = newMetaTypes
      new['roles'] = newRoles
      new['nodes'] = newNodes
      new['exec'] = newExec
      obs.append(new)
      self.commands = copy.deepcopy(self.commands) # Make persistent.
      
      # Insert Object.
      container = self.aq_parent
      if newAcquired:
        portalMaster = self.getPortalMaster()
        newMethod = getattr(portalMaster,newId).meta_type
        metaCmd = portalMaster.getMetaCmd(newId)
        newData = metaCmd['data']
      if newMethod is None:
        newMethod = getattr(container,id).meta_type
      newTitle = '*** DO NOT DELETE OR MODIFY ***'
      if id is None and newData is None:
        if newMethod in ['DTML Document','DTML Method']:
          newData = dtmlExampleCode
        elif newMethod == 'Page Template':
          newData = pageTemplateExampleCode 
        elif newMethod == 'Script (Python)':
          newData = pyScriptExampleCode
        elif newMethod == 'External Method':
          newData = ''
          newData += '# Example code:\n'
          newData += '\n'
          newData += 'def ' + newId + '( self):\n'
          newData += '  return "This is the external method ' + newId + '"\n'
      _zopeutil.removeObject(container, id)
      _zopeutil.removeObject(container, newId)
      _zopeutil.addObject(container, newMethod, newId, newTitle, newData)
      
      # Return with new id.
      return newId


    # --------------------------------------------------------------------------
    #  ZMSMetacmdProvider.getMetaCmdDescription
    # --------------------------------------------------------------------------
    def getMetaCmdDescription(self, id):
      """
      Returns description of meta-command specified by ID.
      """
      metaCmd = self.getMetaCmd(id)
      return metaCmd.get('description','')


    # --------------------------------------------------------------------------
    #  ZMSMetacmdProvider.getMetaCmd
    # 
    # Returns action.
    # --------------------------------------------------------------------------
    def getMetaCmd(self, id):
      obs = self.getMetaCmds(sort=False)
      # Filter by id.
      obs = filter(lambda x: x['id']==id, obs)
      # Not found!
      if len(obs) == 0:
        return None
      # Refresh Object.
      metaCmd = obs[0]
      if self.getConfProperty('ZMS.debug',0):
        self.cloud_sync(metaCmd['id'])
      container = self.aq_parent
      src = _zopeutil.getObject(metaCmd['home'],metaCmd['id'])
      newData = _zopeutil.readObject(metaCmd['home'],metaCmd['id'],'')
      data = _zopeutil.readObject(container,metaCmd['id'],'')
      if src is not None and (src.meta_type=='External Method' or newData != data):
        newMethod = src.meta_type
        newId = metaCmd['id']
        newTitle = '*** DO NOT DELETE OR MODIFY ***'
        _zopeutil.removeObject(container, newId, removeFile=False)
        _zopeutil.addObject(container, newMethod, newId, newTitle, newData)
      ob = _zopeutil.getObject(container,metaCmd['id'])
      if ob is not None:
        metaCmd['meta_type'] = ob.meta_type
        metaCmd['data'] = _zopeutil.readObject(container,metaCmd['id'],'')
        metaCmd['bobobase_modification_time'] = ob.bobobase_modification_time().timeTime()
      
      return metaCmd


    # --------------------------------------------------------------------------
    #  ZMSMetacmdProvider.getMetaCmdIds
    #
    #  Returns list of action-ids.
    # --------------------------------------------------------------------------
    def getMetaCmdIds(self, sort=True):
      obs = self.commands
      if sort:
        obs = map(lambda x: self.getMetaCmd(x['id']), obs)
        obs = filter( lambda x: x is not None, obs)
        obs = map(lambda x: (x['name'],x), obs)
        obs.sort()
        obs = map(lambda x: x[1], obs)
      ids = map(lambda x: x['id'], obs)
      return ids


    # --------------------------------------------------------------------------
    #  ZMSMetacmdProvider.getMetaCmds
    #
    #  Returns list of actions.
    # --------------------------------------------------------------------------
    def getMetaCmds(self, context=None, stereotype='', sort=True):
      stereotypes = {'insert':'manage_add','tab':'manage_tab'}
      metaCmds = []
      portalMasterMetaCmds = None
      for metaCmd in filter(lambda x:x['id'].startswith(stereotypes.get(stereotype,'')),self.commands):
        # Acquire from parent.
        if metaCmd.get('acquired',0)==1:
          if portalMasterMetaCmds is None:
            portalMaster = self.getPortalMaster()
            portalMasterMetaCmds = portalMaster.getMetaCmds(stereotype=stereotype)
          l = filter(lambda x: x['id']==metaCmd['id'], portalMasterMetaCmds)
          if len(l) > 0:
            metaCmd = l[0]
            metaCmd['acquired'] = 1
        else:
          metaCmd = metaCmd.copy()
          metaCmd['home'] = self.aq_parent
          metaCmd['stereotype'] = ' '.join(filter(lambda x:metaCmd['id'].startswith(stereotypes[x]),stereotypes.keys()))
        metaCmds.append(metaCmd)
      if context is not None:
        request = context.REQUEST
        auth_user = request['AUTHENTICATED_USER']
        user_roles = context.getUserRoles(auth_user)
        absolute_url = '/'.join(list(context.getPhysicalPath())+[''])
        l = []
        for metaCmd in metaCmds:
          canExecute = True
          if canExecute:
            hasMetaType = context.meta_id in metaCmd['meta_types'] or 'type(%s)'%context.getType() in metaCmd['meta_types']
            canExecute = canExecute and hasMetaType
          if canExecute:
            hasRole = False
            hasRole = hasRole or '*' in metaCmd['roles']
            hasRole = hasRole or len(context.intersection_list(user_roles,metaCmd['roles'])) > 0
            hasRole = hasRole or auth_user.has_role('Manager')
            canExecute = canExecute and hasRole
          if canExecute:
            nodes = context.string_list(metaCmd.get('nodes','{$}'))
            sl = []
            sl.extend(map( lambda x: (context.getHome().id+'/content/'+x[2:-1]+'/').replace('//','/'),filter(lambda x: x.find('@')<0,nodes)))
            sl.extend(map( lambda x: (x[2:-1].replace('@','/content/')+'/').replace('//','/'),filter(lambda x: x.find('@')>0,nodes)))
            hasNode = len( filter( lambda x: absolute_url.find(x)>=0, sl)) > 0
            canExecute = canExecute and hasNode
          if canExecute:
            l.append(metaCmd)
        metaCmds = l
      return metaCmds


    ############################################################################
    #  ZMSMetacmdProvider.manage_changeMetacmds:
    #
    #  Change Meta-Commands.
    ############################################################################
    def manage_changeMetacmds(self, btn, lang, REQUEST, RESPONSE):
        """ ZMSMetacmdProvider.manage_changeMetacmds """
        message = ''
        id = REQUEST.get('id','')
        
        # Acquire.
        # --------
        if btn == self.getZMILangStr('BTN_ACQUIRE'):
          aq_ids = REQUEST.get('aq_ids',[])
          for newId in aq_ids:
            newAcquired = 1
            self.setMetacmd(None, newId, newAcquired)
          message = self.getZMILangStr('MSG_INSERTED')%str(len(aq_ids))
        
        # Change.
        # -------
        elif btn == self.getZMILangStr('BTN_SAVE'):
          id = REQUEST['id']
          newId = REQUEST['el_id']
          newAcquired = 0
          newRevision = REQUEST.get('el_revision','0.0.0').strip()
          newName = REQUEST.get('el_name','').strip()
          newTitle = REQUEST.get('el_title','').strip()
          newMethod = None
          newData = REQUEST.get('el_data','').strip()
          newExec = REQUEST.get('el_exec',0)
          newDescription = REQUEST.get('el_description','').strip()
          newIconClazz = REQUEST.get('el_icon_clazz','')
          newMetaTypes = REQUEST.get('el_meta_types',[])
          newRoles = REQUEST.get('el_roles',[])
          newNodes = REQUEST.get('el_nodes','')
          id = self.setMetacmd(id, newId, newAcquired, newRevision, newName, newTitle, \
            newMethod, newData, newExec, newDescription, newIconClazz, \
            newMetaTypes, newRoles, newNodes)
          message = self.getZMILangStr('MSG_CHANGED')
        
        # Copy.
        # -----
        elif btn == self.getZMILangStr('BTN_COPY'):
          metaOb = self.getMetaCmd(id)
          if metaOb.get('acquired',0) == 1:
            portalMaster = self.getPortalMaster()
            if portalMaster is not None:
              REQUEST.set('ids',[id])
              xml =  portalMaster.manage_changeMetacmds(self.getZMILangStr('BTN_EXPORT'), lang, REQUEST, RESPONSE)
              self.importXml(xml=xml)
              message = self.getZMILangStr('MSG_IMPORTED')%('<i>%s</i>'%id)
        
        # Delete.
        # -------
        elif btn == self.getZMILangStr('BTN_DELETE'):
          if id:
            ids = [id]
          else:
            ids = REQUEST.get('ids',[])
          for id in ids:
            self.delMetacmd(id)
          id = ''
          message = self.getZMILangStr('MSG_DELETED')%len(ids)
        
        # Export.
        # -------
        elif btn == self.getZMILangStr('BTN_EXPORT'):
          revision = '0.0.0'
          value = []
          ids = REQUEST.get('ids',[])
          for id in self.getMetaCmdIds():
            if id in ids or len(ids) == 0:
              metaCmd = self.getMetaCmd(id)
              revision = metaCmd.get('revision','0.0.0')
              el_id = metaCmd['id']
              el_name = metaCmd['name']
              el_title = metaCmd.get('title','')
              el_meta_type = metaCmd['meta_type']
              el_description = metaCmd['description']
              el_icon_clazz = metaCmd.get('icon_clazz','')
              el_meta_types = metaCmd['meta_types']
              el_roles = metaCmd['roles']
              el_exec = metaCmd['exec']
              el_data = _zopeutil.readObject(metaCmd['home'],metaCmd['id'])
              # Value.
              value.append({'id':el_id,'revision':revision,'name':el_name,'title':el_title,'description':el_description,'meta_types':el_meta_types,'roles':el_roles,'exec':el_exec,'icon_clazz':el_icon_clazz,'meta_type':el_meta_type,'data':el_data})
          # XML.
          if len(ids)==1:
            filename = '%s-%s.metacmd.xml'%(ids[0],revision)
          else:
            filename = 'export.metacmd.xml'
          content_type = 'text/xml; charset=utf-8'
          export = self.getXmlHeader() + self.toXmlString(value,1)
          RESPONSE.setHeader('Content-Type',content_type)
          RESPONSE.setHeader('Content-Disposition','attachment;filename="%s"'%filename)
          return export
        
        # Import.
        # -------
        elif btn == self.getZMILangStr('BTN_IMPORT'):
          f = REQUEST['file']
          if f:
            filename = f.filename
            self.importXml(xml=f)
          else:
            filename = REQUEST['init']
            self.importConf(filename, createIfNotExists=1)
          message = self.getZMILangStr('MSG_IMPORTED')%('<i>%s</i>'%f.filename)
        
        # Insert.
        # -------
        elif btn == self.getZMILangStr('BTN_INSERT'):
          newId = REQUEST.get('_id').strip()
          newAcquired = 0
          newRevision = REQUEST.get('_revision','0.0.0').strip()
          newName = REQUEST.get('_name').strip()
          newTitle = REQUEST.get('_title').strip()
          newMethod = REQUEST.get('_type','DTML Method')
          newData = None
          newExec = REQUEST.get('_exec',0)
          newIconClazz = REQUEST.get('_icon_clazz','')
          id = self.setMetacmd(None, newId, newAcquired, newRevision, newName, newTitle, newMethod, newData, newExec, newIconClazz=newIconClazz)
          message = self.getZMILangStr('MSG_INSERTED')%id
        
        # Cloud import.
        # -------------
        elif btn == 'cloud_import':
          ids = REQUEST.get('ids',[])
          message = self.cloud_import(ids)
        
        # Cloud export.
        # -------------
        elif btn == 'cloud_export':
          ids = REQUEST.get('ids',[])
          message = self.cloud_export(ids)
        
        # Return with message.
        message = urllib.quote(message)
        return RESPONSE.redirect('manage_main?lang=%s&manage_tabs_message=%s&id=%s'%(lang,message,id))

################################################################################