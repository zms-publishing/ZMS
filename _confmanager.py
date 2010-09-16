################################################################################
# _confmanager.py
#
# $Id: _confmanager.py,v 1.9 2004/11/30 20:03:17 zmsdev Exp $
# $Name:$
# $Author: zmsdev $
# $Revision: 1.9 $
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
from __future__ import nested_scopes
from zope.interface import implements
from cStringIO import StringIO
from App.Common import package_home
from App.special_dtml import HTMLFile
from DateTime.DateTime import DateTime
from OFS.CopySupport import absattr
from OFS.Image import Image
from Products.PageTemplates import ZopePageTemplate
from Products.PythonScripts import PythonScript
import os
import stat
import urllib
# Product imports.
import IZMSMetamodelProvider, IZMSFormatProvider, IZMSSvnInterface
import ZMSWorkflowProvider, ZMSWorkflowProviderAcquired
import _globals
import _fileutil
import _filtermanager
import _mediadb
import _metacmdmanager
import _multilangmanager
import _sequence
import zmslog


"""
################################################################################
###
###   Initialization
###
################################################################################
"""

# ------------------------------------------------------------------------------
#  _confmanager.initCSS:
# ------------------------------------------------------------------------------
def initCSS(self):
  stylesheet_css = getattr( self, 'stylesheet.css', None)
  if stylesheet_css is not None:
    container = getattr( self.getHome(), 'common', None)
    folder = getattr( container, 'css', None)
    if folder is not None:
      container = getattr( self.getHome(), 'instance', None)
      if container is None:
        self.getHome().manage_addFolder( id='instance', title='Local Graphics and Assets')
        container = getattr( self.getHome(), 'instance', None)
      folder = getattr( container, 'css', None)
    if folder is None:
      container.manage_addFolder( id='css', title='Cascading Style-Sheets')
      folder = getattr( container, 'css', None)
    ids = self.objectIds(['DTML Method'])
    excl_ids = filter( lambda x: x in ids, [ 'stylesheet.css'] + map( lambda x: 'stylesheet_%s.css'%x, self.getLangIds()))
    move_ids = filter( lambda x: x not in excl_ids and x.find('.css') > 0, ids)
    id = 'style.css'
    title = 'Default CSS'
    data = stylesheet_css.raw
    if data.find( '<dtml-var') >= 0:
      data = '<dtml-with content\n><dtml-call "REQUEST.RESPONSE.setHeader(\'Cache-Control\',\'public, max-age=3600\')"\n><dtml-var f_standard_html_request\n><dtml-var f_css_defaults>\n'+data+'\n</dtml-with>'
    if id not in folder.objectIds():
      folder.manage_addDTMLMethod( id, title, data)
    self.manage_delObjects( ids=excl_ids)
    try:
      cb_copy_data = self.manage_cutObjects(move_ids,self.REQUEST)
      folder.manage_pasteObjects(cb_copy_data=None,REQUEST=self.REQUEST)
    except:
      pass


# ------------------------------------------------------------------------------
#  _confmanager.initConf:
# ------------------------------------------------------------------------------
def initConf(self, profile, REQUEST):
  createIfNotExists = True
  files = self.getConfFiles()
  for filename in files.keys():
    label = files[filename]
    if label.startswith(profile + '.'):
      if filename.find('.zip') > 0:
        self.importConfPackage(filename,REQUEST,createIfNotExists)
      elif filename.find('.xml') > 0:
        self.importConf(filename,REQUEST,createIfNotExists)
      self.synchronizeObjAttrs()


# ------------------------------------------------------------------------------
#  _confmanager.updateConf:
# ------------------------------------------------------------------------------
def updateConf(self, REQUEST):
  createIfNotExists = False
  filenames = self.getConfFiles().keys()
  for filename in filenames:
    self.importConf(filename,REQUEST,createIfNotExists)


################################################################################
################################################################################
###
###   Class
###
################################################################################
################################################################################
class ConfManager(
    _multilangmanager.MultiLanguageManager,        # Languages
    _metacmdmanager.MetacmdManager,            # Actions
    _filtermanager.FilterManager,            # Filters (XML Im-/Export)
    ):
    implements(
      IZMSMetamodelProvider.IZMSMetamodelProvider,
      IZMSFormatProvider.IZMSFormatProvider,
      IZMSSvnInterface.IZMSSvnInterface)

    # Management Interface.
    # ---------------------
    manage_customize = HTMLFile('dtml/ZMS/manage_customize', globals()) 
    manage_customizeSvnForm = HTMLFile('dtml/ZMS/manage_customizesvnform', globals()) 
    manage_customizeDesignForm = HTMLFile('dtml/ZMS/manage_customizedesignform', globals()) 


    # --------------------------------------------------------------------------
    #  ConfManager.importConfPackage:
    # --------------------------------------------------------------------------
    def importConfPackage(self, file, REQUEST, createIfNotExists=0):
      if type( file) is str:
        if file.startswith('http://'):
          file = StringIO( self.http_import(file))
        else:
          file = open(_fileutil.getOSPath(file),'rb')
      files = _fileutil.getZipArchive( file)
      for f in files:
        if not f.get('isdir'):
          self.importConf(f,REQUEST,createIfNotExists)
      self.synchronizeObjAttrs()


    # --------------------------------------------------------------------------
    #  ConfManager.getConfXmlFile:
    # --------------------------------------------------------------------------
    def getConfXmlFile(self, file):
      if type(file) is dict:
        filename = file['filename']
        xmlfile = StringIO( file['data'])
      elif type(file) is str and file.startswith('http://'):
        filename = _fileutil.extractFilename(file)
        xmlfile = StringIO( self.http_import(file))
      else:
        filename = _fileutil.extractFilename(file)
        xmlfile = open(_fileutil.getOSPath(file),'rb')
      return filename, xmlfile


    # --------------------------------------------------------------------------
    #  ConfManager.importConf:
    # --------------------------------------------------------------------------
    def importConf(self, file, REQUEST, createIfNotExists=0):
      message = ''
      filename, xmlfile = self.getConfXmlFile( file)
      zms_system = 1
      if filename.find('.charfmt.') > 0:
        self.format_manager.importCharformatXml(xmlfile, REQUEST, zms_system, createIfNotExists)
      elif filename.find('.filter.') > 0:
        _filtermanager.importXml(self, xmlfile, REQUEST, zms_system, createIfNotExists)
      elif filename.find('.metadict.') > 0:
        self.metaobj_manager.importMetadictXml(xmlfile, REQUEST, zms_system, createIfNotExists)
      elif filename.find('.metaobj.') > 0:
        self.metaobj_manager.importMetaobjXml(xmlfile, REQUEST, zms_system, createIfNotExists)
      elif filename.find('.metacmd.') > 0:
        _metacmdmanager.importXml(self, xmlfile, REQUEST, zms_system, createIfNotExists)
      elif filename.find('.langdict.') > 0:
        _multilangmanager.importXml(self, xmlfile, REQUEST, zms_system, createIfNotExists)
      elif filename.find('.textfmt.') > 0:
        self.format_manager.importTextformatXml(xmlfile, REQUEST, zms_system, createIfNotExists)
      xmlfile.close()
      return message


    # --------------------------------------------------------------------------
    #  ConfManager.getConfFiles:
    #
    #  Returns configuration-files from $ZMS_HOME/import-Folder
    # --------------------------------------------------------------------------
    def getConfFiles(self, pattern=None, REQUEST=None, RESPONSE=None):
      """
      ConfManager.getConfFiles
      """
      filenames = {}
      filepaths = [
        self.Control_Panel.getINSTANCE_HOME()+'/etc/zms/import/',
        package_home(globals())+'/import/',]
      try:
        conf = open( filepaths[0]+'configure.zcml','r')
        _globals.writeBlock( self, "[getConfFiles]: Read from "+filepaths[0]+"configure.zcml")
      except:
        conf = open( filepaths[1]+'configure.zcml','r')
        _globals.writeBlock( self, "[getConfFiles]: Read from "+filepaths[0]+"configure.zcml")
      conf_xml = self.xmlParse( conf)
      for source in self.xmlNodeSet(conf_xml,'source'):
        location = source['attrs']['location']
        if location.startswith('http://'):
          try:
            remote_conf = self.http_import(location+'configure.zcml')
            remote_conf_xml = self.xmlParse( remote_conf)
            for remote_file in self.xmlNodeSet(remote_conf_xml,'file'):
              filename = remote_file['attrs']['id']
              if filename not in filenames.keys():
                filenames[location+filename] = filename+' ('+remote_file['attrs']['title']+')'
          except:
            _globals.writeError( self, "[getConfFiles]: can't get conf-files from remote URL=%s"%location)
        else:
          for filepath in filepaths:
            if os.path.exists( filepath):
              for filename in os.listdir(filepath+location):
                path = filepath + filename
                mode = os.stat(path)[stat.ST_MODE]
                if not stat.S_ISDIR(mode):
                  if filename not in filenames:
                    filenames[path] = filename
      conf.close()
      # Filter.
      if pattern is not None:
        for k in filenames.keys():
          if k.find(pattern) < 0:
            del filenames[k]
          else:
            v = filenames[k]
            i = v.find(' ')
            if i < 0:
              i = len(v)
            v = v[:v.find(pattern)]+v[i:]
            filenames[k] = v
      # Return.
      if REQUEST is not None and \
         RESPONSE is not None:
        RESPONSE = REQUEST.RESPONSE
        content_type = 'text/xml; charset=utf-8'
        filename = 'getConfFiles.xml'
        RESPONSE.setHeader('Content-Type',content_type)
        RESPONSE.setHeader('Content-Disposition','inline;filename=%s'%filename)
        RESPONSE.setHeader('Cache-Control', 'no-cache')
        RESPONSE.setHeader('Pragma', 'no-cache')
        return self.getXmlHeader() + self.toXmlString( filenames)
      else:
        return filenames


    """
    ############################################################################
    ###
    ###   SVN
    ###
    ############################################################################
    """

    # --------------------------------------------------------------------------
    #  ConfManager.svnCopy:
    # --------------------------------------------------------------------------
    def svnCopy(self, node, path, ids=[], excl_ids=[]):
      l = []
      for ob in node.objectValues(['ZMS']):
        # Add content-object artefacts to exclude-ids.
        for metaObjId in ob.getMetaobjIds():
          for metaObjAttrId in ob.getMetaobjAttrIds( metaObjId):
            metaObjAttr = ob.getMetaobjAttr(metaObjId,metaObjAttrId)
            if metaObjAttr['type'] in ob.metaobj_manager.valid_zopetypes:
              excl_ids.append( metaObjAttrId)
      obs = map( lambda x: (absattr(x.id), x), node.objectValues())
      obs.sort()
      for x in obs:
        id = x[0]
        ob = x[1]
        if id not in excl_ids and not id.startswith('A_'):
          action = None
          filepath = path+'/'+id
          filemtime = None
          mtime = long(ob.bobobase_modification_time().timeTime())
          meta_type = ob.meta_type
          if node.meta_type == 'Folder' and ob.meta_type in ['DTML Method','DTML Document','File','Image','Script (Python)']:
            if ob.meta_type in ['DTML Method','DTML Document']:
              filepath += '.dtml'
            if ob.meta_type in ['Script (Python)']:
              filepath += '.py'
            if os.path.exists( filepath):
              filestat = os.stat(filepath)
              filemtime = long(filestat[stat.ST_MTIME])
              if mtime > filemtime:
                action = 'refresh'
              elif mtime < filemtime:
                action = 'conflict'
            else: 
              action = 'add'
            if action:
              l.append({'action':action,'filepath':filepath,'mtime':mtime,'filemtime':filemtime,'meta_type':meta_type})
              if filepath in ids or '*' in ids:
                _fileutil.exportObj(ob,filepath)
                atime = mtime
                times = (atime,mtime)
                os.utime(filepath,times)
          elif ob.meta_type == 'ZMS':
            l.extend( ob.metaobj_manager.svnCopy( node, path, ids))
          elif ob.meta_type == 'Folder':
            if not os.path.exists( filepath):
              action = 'add'
              l.append({'action':action,'filepath':filepath,'meta_type':meta_type})
              if filepath in ids or '*' in ids:
                _fileutil.mkDir(filepath)
            l.extend( self.svnCopy(ob,filepath,ids))
      return l


    # --------------------------------------------------------------------------
    #  ConfManager.svnUpdate:
    # --------------------------------------------------------------------------
    def svnUpdate(self, node, path, ids=[], excl_ids=[]):
      l = []
      path_ids = []
      for filename in os.listdir(path):
        action = None
        id = filename
        filepath = path+'/'+id
        filestat = os.stat(filepath)
        mode = filestat[stat.ST_MODE]
        filemtime = long(filestat[stat.ST_MTIME])
        if id.endswith('.dtml'):
          id = id[:id.rfind('.')]
        if id.endswith('.py'):
          id = id[:id.rfind('.')]
        path_ids.append( id)
        ob = getattr( node, id, None)
        if stat.S_ISDIR(mode):
          if filename == 'metaobj_manager':
            for ob in node.objectValues(['ZMS']):
              l.extend( ob.metaobj_manager.svnUpdate( node, filepath, ids))
          elif filename != '.svn':
            if ob is None:
              if filepath in ids or '*' in ids:
                node.manage_addFolder( id, 'New Folder')
              ob = getattr( node, id, None)
              meta_type = 'Folder'
              mtime = 0
              action = 'add'
            if action:
              l.append({'action':action,'filepath':filepath,'mtime':mtime,'filemtime':filemtime,'meta_type':meta_type})
            l.extend( self.svnUpdate(ob,filepath,ids))
        else:
          if ob is None:
            if filename.endswith('.dtml'):
              meta_type = 'DTML Method'
              if filepath in ids or '*' in ids:
                node.manage_addDTMLMethod( id=id, title='New DTML Method')
            elif filename.endswith('.py'):
              meta_type = 'Script (Python)'
              if filepath in ids or '*' in ids:
                PythonScript.manage_addPythonScript( node, id)
            elif filename.lower().endswith('.gif') or \
                 filename.lower().endswith('.jpg') or \
                 filename.lower().endswith('.png'):
              meta_type = 'Image'
              if filepath in ids or '*' in ids:
                node.manage_addImage( id=id, file='', title='')
            else:
              meta_type = 'File'
              if filepath in ids or '*' in ids:
                node.manage_addFile( id=id, file='', title='')
            ob = getattr( node, id, None)
            mtime = 0
            action = 'add'
          else:
            meta_type = ob.meta_type
            # modification-time
            mtime = long(ob.bobobase_modification_time().timeTime())
            if mtime < filemtime:
              action = 'refresh'
          if action:
            l.append({'action':action,'filepath':filepath,'mtime':mtime,'filemtime':filemtime,'meta_type':meta_type})
            if filepath in ids or '*' in ids:
              file = open(filepath)
              data = file.read()
              ob.manage_upload(data)
              file.close()
      if node is not None and node.meta_type != 'ZMS':
        for ob in node.objectValues(['ZMS']):
          # Add content-object artefacts to exclude-ids.
          for metaObjId in ob.getMetaobjIds():
            for metaObjAttrId in ob.getMetaobjAttrIds( metaObjId):
              metaObjAttr = ob.getMetaobjAttr(metaObjId,metaObjAttrId)
              if metaObjAttr['type'] in ob.metaobj_manager.valid_zopetypes:
                excl_ids.append( metaObjAttrId)
        for id in filter( lambda x: x not in path_ids and x not in excl_ids and not x.startswith('A_'), node.objectIds(['DTML Method','File','Folder','Image'])):
          ob = getattr( node, id)
          action = 'delete'
          filepath = path+'/'+id
          mtime = long(ob.bobobase_modification_time().timeTime())
          filemtime = 0
          meta_type = ob.meta_type
          l.append({'action':action,'filepath':filepath,'mtime':mtime,'filemtime':filemtime,'meta_type':meta_type})
          if filepath in ids or '*' in ids:
            node.manage_delObjects( ids=[id])
      return l


    """
    ############################################################################
    ###
    ###   Configuration-Properties Getters
    ###
    ############################################################################
    """

    # --------------------------------------------------------------------------
    #  ConfManager.getSequence:
    #
    #  Returns sequence.
    # --------------------------------------------------------------------------
    def getSequence(self):
      id = 'acl_sequence'
      exists = id in self.objectIds(['Sequence'])
      portalMaster = self.getPortalMaster()
      if portalMaster is not None:
        startvalue = 0
        if exists:
          ob = getattr(self,id)
          startvalue = ob.value
          self.manage_delObjects(ids=[id])
        ob = portalMaster.getSequence()
        if ob.value < startvalue:
          ob.value = startvalue
      else:
        if not exists:
          sequence = _sequence.Sequence()
          self._setObject(sequence.id, sequence)
        ob = getattr(self,id)
      return ob

    # --------------------------------------------------------------------------
    #  ConfManager.getMediaDb:
    #
    #  Returns mediadb.
    # --------------------------------------------------------------------------
    def getMediaDb(self):
      for ob in self.getDocumentElement().objectValues(['MediaDb']):
        return ob
      return None

    # --------------------------------------------------------------------------
    #  ConfManager.getStylesheet:
    #
    #  Returns stylesheet.
    # --------------------------------------------------------------------------
    def getStylesheet(self, id=None):
      stylesheets = self.getStylesheets()
      if id is None:
        return stylesheets[0]
      else:
        for css in stylesheets:
          if absattr( css.id) == id:
            return css

    # --------------------------------------------------------------------------
    #  ConfManager.getStylesheets:
    #
    #  Returns list of stylesheets.
    # --------------------------------------------------------------------------
    def getStylesheets(self):
      ids = []
      obs = []
      for id in [ 'instance', 'common']:
        container = getattr( self, id, None)
        if container is not None:
          folder = getattr( container, 'css', None)
          if folder is not None:
            for ob in folder.objectValues(['DTML Method','DTML Document']):
              id = absattr( ob.id)
              if id not in ids:
                ids.append( id)
                if absattr( ob.id) == self.getConfProperty('ZMS.stylesheet','style.css'):
                  obs.insert( 0, ob)
                else:
                  obs.append( ob)
      return obs


    """
    ############################################################################
    ###
    ###   Configuration-Tab Options
    ###
    ############################################################################
    """

    # --------------------------------------------------------------------------
    #  ConfManager.customize_manage_options:
    # --------------------------------------------------------------------------
    def customize_manage_options(self):
      l = []
      l.append({'label':'TAB_SYSTEM','action':'manage_customize'})
      l.append({'label':'TAB_LANGUAGES','action':'manage_customizeLanguagesForm'})
      for ob in self.objectValues(['ZMSMetamodelProvider','ZMSFormatProvider','ZMSWorkflowProvider']):
        for d in ob.manage_sub_options:
          l.append(self.operator_setitem(d.copy(),'action',ob.id+'/'+d['action']))
      l.append({'label':'TAB_METACMD','action':'manage_customizeMetacmdForm'})
      l.append({'label':'TAB_FILTER','action':'manage_customizeFilterForm'})
      l.append({'label':'TAB_DESIGN','action':'manage_customizeDesignForm'})
      return l


    """
    ############################################################################
    ###
    ###   Configuration-Properties
    ###
    ############################################################################
    """

    # --------------------------------------------------------------------------
    #  ConfManager.getConfProperties:
    #
    #  Returns property from configuration.
    # --------------------------------------------------------------------------
    def getConfProperties(self):
      return getattr( self, '__attr_conf_dict__', {})

    # --------------------------------------------------------------------------
    #  ConfManager.getConfProperty:
    #
    #  Removes property from configuration.
    #
    #  @param key    The key.
    # --------------------------------------------------------------------------
    def delConfProperty(self, key):
      self.setConfProperty(key,None)

    # --------------------------------------------------------------------------
    #  ConfManager.getConfProperty:
    #
    #  Returns property from configuration.
    #
    #  @param key    The key.
    #  @param default    The default-value.
    #  @return any
    # --------------------------------------------------------------------------
    def getConfProperty(self, key, default=None):
      return self.getConfProperties().get( key, default)

    # --------------------------------------------------------------------------
    #  ConfManager.setConfProperty:
    #
    #  Sets property into configuration.
    #
    #  @param key    The key.
    #  @param value    The value.
    #  @return void
    # --------------------------------------------------------------------------
    def setConfProperty(self, key, value):
      d = self.getConfProperties()
      if value is None:
        if d.has_key(key):
          del d[key]
      else:
        d[key] = value
      self.__attr_conf_dict__ = d
      self.__attr_conf_dict__ = self.__attr_conf_dict__.copy()


    """
    ############################################################################
    ###
    ###   Configuration-System
    ###
    ############################################################################
    """

    ############################################################################
    #  ConfManager.manage_customizeSystem: 
    #
    #  Customize system properties.
    ############################################################################
    def manage_customizeSystem(self, btn, key, lang, REQUEST, RESPONSE=None):
      """ ConfManager.manage_customizeSystem """
      
      message = ''
      params = []
      
      ##### Import ####
      if key == 'Import':
        if btn == 'Import':
          f = REQUEST['file']
          createIfNotExists = 1
          if f:
            filename = f.filename
            self.importConfPackage( f, REQUEST, createIfNotExists)
          else:
            filename = REQUEST['init']
            self.importConfPackage( filename, REQUEST, createIfNotExists)
          message = self.getZMILangStr('MSG_IMPORTED')%('<i>%s</i>'%filename)
      
      ##### History ####
      elif key == 'History':
        old_active = self.getConfProperty('ZMS.Version.active',0)
        new_active = REQUEST.get('active',0)
        old_nodes = self.getConfProperty('ZMS.Version.nodes',['{$}'])
        new_nodes = self.string_list(REQUEST.get('nodes',''))
        self.setConfProperty('ZMS.Version.active',new_active)
        self.setConfProperty('ZMS.Version.nodes',new_nodes)
        nodes = []
        if old_active == 1 and new_active == 0:
          nodes = old_nodes
        if old_active == 1 and new_active == 1:
          nodes = self.difference_list( old_nodes, self.getConfProperty('ZMS.Version.nodes',['{$}']))
        for node in nodes:
          ob = self.getLinkObj( node)
          if ob is not None:
            message += '[%s: %i]'%(node,ob.packHistory())
        message = self.getZMILangStr('MSG_CHANGED')+message
      
      ##### Clients ####
      elif key == 'Clients':
        if btn == 'Change':
          s = REQUEST.get('portal_master','').strip()
          if s != self.getHome().id:
            self.setConfProperty('Portal.Master',s)
          l = []
          for s in REQUEST.get('portal_clients','').split('\n'):
            s = s.strip()
            if s in self.getHome().objectIds(['Folder']):
              l.append(s)
          self.setConfProperty('Portal.Clients',l)
          message = self.getZMILangStr('MSG_CHANGED')
      
      ##### MediaDb ####
      elif key == 'MediaDb':
        if btn == 'Create':
          location = REQUEST['mediadb_location'].strip()
          _mediadb.manage_addMediaDb(self,location)
          message = self.getZMILangStr('MSG_CHANGED')
        elif btn == 'Pack':
          message = _mediadb.manage_packMediaDb(self)
        elif btn == 'Remove':
          message = _mediadb.manage_delMediaDb(self)
      
      ##### SVN ####
      elif key == 'SVN':
        k = REQUEST.get( 'conf_key')
        v = REQUEST.get( 'conf_value', '')
        self.setConfProperty( k, v)
        if btn == 'Change':
          message = self.getZMILangStr('MSG_CHANGED')
        elif btn == 'Copy to Location':
          execute = REQUEST.get('execute')
          if execute:
            ids = REQUEST.get('ids',[])
            l = self.svnCopy(self.getHome(),self.getConfProperty(k,v)+'/'+self.getHome().id,ids)
            message = self.getZMILangStr('MSG_EXPORTED')%str(len(ids))
          else:
            return RESPONSE.redirect( self.url_append_params( 'manage_customizeSvnForm', { 'lang': lang, 'conf_key': k, 'conf_value': v, 'action': 'outgoing'}))
        elif btn == 'Update from Location':
          execute = REQUEST.get('execute')
          if execute:
            ids = REQUEST.get('ids',[])
            l = self.svnUpdate(self.getHome(),self.getConfProperty(k,v)+'/'+self.getHome().id,ids)
            message = self.getZMILangStr('MSG_INSERTED')%str(len(ids))
          else:
            return RESPONSE.redirect( self.url_append_params( 'manage_customizeSvnForm', { 'lang': lang, 'conf_key': k, 'conf_value': v, 'action': 'incoming'}))
      
      ##### Custom ####
      elif key == 'Custom':
        k = REQUEST.get( 'conf_key', '')
        if btn == 'Change':
          v = REQUEST.get( 'conf_value', '')
          self.setConfProperty( k, v)
          if REQUEST.get('portal_clients'):
            for portalClient in self.getPortalClients():
              portalClient.setConfProperty( k, v)
          params.append('conf_key')
          message = self.getZMILangStr('MSG_CHANGED')
        elif btn == 'Delete':
          self.delConfProperty( k)
          if REQUEST.get('portal_clients'):
            for portalClient in self.getPortalClients():
              portalClient.delConfProperty( k)
          message = self.getZMILangStr('MSG_DELETED')%int(1)
      
      ##### InstalledProducts ####
      elif key == 'InstalledProducts':
        if btn == 'Change':
          self.setConfProperty('InstalledProducts.pil',REQUEST.get('pil',None))
          self.setConfProperty('InstalledProducts.pil.pythonpath',REQUEST.get('pil_pythonpath','python'))
          self.setConfProperty('InstalledProducts.pil.thumbnail.max',REQUEST.get('pil_thumbnail_max',100))
          self.setConfProperty('InstalledProducts.pil.hires.thumbnail.max',REQUEST.get('pil_hires_thumbnail_max',0))
          message = self.getZMILangStr('MSG_CHANGED')
      
      ##### Manager ####
      elif key == 'Manager':
        if btn == 'Add':
          meta_type = REQUEST.get('meta_type','')
          if meta_type == 'ZMSLog':
            obj = zmslog.ZMSLog()
            self._setObject(obj.id, obj)
            message = 'Added '+meta_type
          elif meta_type == 'ZMSWorkflowProvider':
            obj = ZMSWorkflowProvider.ZMSWorkflowProvider()
            self._setObject(obj.id, obj)
            message = 'Added '+meta_type
          elif meta_type == 'ZMSWorkflowProviderAcquired':
            obj = ZMSWorkflowProviderAcquired.ZMSWorkflowProviderAcquired()
            self._setObject(obj.id, obj)
            message = 'Added '+meta_type
        elif btn == 'Remove':
          ids = REQUEST.get('ids',[])
          if ids:
            message = 'Removed '+', '.join(ids)
            self.manage_delObjects(ids=ids)
      
      # Return with message.
      if RESPONSE:
        d = {'lang': lang,'manage_tabs_message': message}
        for param in params:
          d[param] = REQUEST.get( param, '')
        return RESPONSE.redirect( self.url_append_params( 'manage_customize', d) + '#_%s'%key)
      
      return message


    """
    ############################################################################
    ###
    ###   Configuration-Design
    ###
    ############################################################################
    """

    ############################################################################
    #  ConfManager.manage_customizeDesign: 
    #
    #  Customize design properties.
    ############################################################################
    def manage_customizeDesign(self, btn, lang, REQUEST, RESPONSE):
      """ ConfManager.manage_customizeDesign """
      message = ''
      cssId = REQUEST.get('cssId','')
      
      # Insert.
      # -------
      if btn == self.getZMILangStr('BTN_INSERT'):
        #-- Stylesheet.
        if REQUEST.has_key('newCssId'):
          title = 'CSSschema'
          data = '<dtml-with content\n><dtml-call "REQUEST.RESPONSE.setHeader(\'Cache-Control\',\'public, max-age=3600\')"\n><dtml-var f_standard_html_request\n><dtml-var f_css_defaults>\n\n</dtml-with>'
          self.common.css.manage_addDTMLMethod( REQUEST.get('newCssId'), title, data)
          message = self.getZMILangStr('MSG_INSERTED')%REQUEST.get('newCssId')
          cssId = REQUEST.get('newCssId')
      
      # Delete.
      # -------
      if btn == self.getZMILangStr('BTN_DELETE'):
        #-- Stylesheet.
        if REQUEST.has_key('cssId'):
          self.common.css.manage_delObjects(ids=[REQUEST.get('cssId')])
          message = self.getZMILangStr('MSG_DELETED')%int(1)
          cssId = ''
      
      # Ex-/Import.
      # -----------
      if btn in [ self.getZMILangStr('BTN_EXPORT'), self.getZMILangStr('BTN_IMPORT')]:
        #-- Theme.
        home = self.getHome()
        home_id = home.id
        temp_folder = self.temp_folder
        # Init exclude-ids.
        excl_ids = []
        # Add clients-folders to exclude-ids.
        for folder in home.objectValues( ['Folder']):
          if len( folder.objectValues( ['ZMS'])) > 0:
            excl_ids.append( absattr( folder.id))
        # Add content-object artefacts to exclude-ids.
        for metaObjId in self.getMetaobjIds():
          for metaObjAttrId in self.getMetaobjAttrIds( metaObjId):
            metaObjAttr = self.getMetaobjAttr(metaObjId,metaObjAttrId)
            if metaObjAttr['type'] in self.metaobj_manager.valid_zopetypes:
              excl_ids.append( metaObjAttrId)
        # Filter ids.
        ids = filter( lambda x: x not in excl_ids, home.objectIds(self.metaobj_manager.valid_zopetypes))
        if btn == self.getZMILangStr('BTN_EXPORT'):
          if home_id in temp_folder.objectIds():
            temp_folder.manage_delObjects(ids=[home_id])
          temp_folder.manage_addFolder(id=home_id,title=home.title_or_id())
          folder = getattr(temp_folder,home_id)
          home.manage_copyObjects(ids,REQUEST)
          folder.manage_pasteObjects(cb_copy_data=None,REQUEST=REQUEST)
          return RESPONSE.redirect( self.url_append_params('%s/manage_exportObject'%temp_folder.absolute_url(),{'id':home_id,'download:int':1}))
        if btn == self.getZMILangStr('BTN_IMPORT'):
          v = REQUEST['theme']
          temp_filename = _fileutil.extractFilename( v.filename)
          temp_id = temp_filename[:temp_filename.rfind('.')]
          filepath = INSTANCE_HOME+'/import/'+temp_filename
          _fileutil.exportObj( v, filepath)
          if temp_id in temp_folder.objectIds():
            temp_folder.manage_delObjects(ids=[temp_id])
          temp_folder.manage_importObject( temp_filename)
          folder = getattr( temp_folder, temp_id)
          home.manage_delObjects(ids=ids)
          folder.manage_copyObjects(folder.objectIds(),REQUEST)
          home.manage_pasteObjects(cb_copy_data=None,REQUEST=REQUEST)
          _fileutil.remove( filepath)
          temp_folder.manage_delObjects(ids=[temp_id])
      
      # Save.
      # -----
      if btn == self.getZMILangStr('BTN_SAVE'):
        #-- Stylesheet.
        if REQUEST.has_key('cssId'):
          if REQUEST.get('default'):
            self.setConfProperty('ZMS.stylesheet',REQUEST.get('cssId'))
          css = self.getStylesheet( REQUEST.get('cssId'))
          data = REQUEST.get('stylesheet')
          title = css.title
          css.manage_edit(data,title)
          message = self.getZMILangStr('MSG_CHANGED')
        #-- Sitemap.
        if REQUEST.has_key('attr_layoutsitemap'):
          if len(REQUEST['attr_layoutsitemap'])>0:
            self.attr_layoutsitemap = int(REQUEST['attr_layoutsitemap'])
          elif hasattr(self,'attr_layoutsitemap'):
            delattr(self,'attr_layoutsitemap')
          message = self.getZMILangStr('MSG_CHANGED')
      
      # Upload.
      # -------
      elif btn == self.getZMILangStr('BTN_UPLOAD'):
        #-- ZMI Logo.
        self.zmi_logo = Image(id='logo', title='', file='')
        self.zmi_logo.manage_upload(REQUEST['file'],REQUEST)
        message = self.getZMILangStr('MSG_CHANGED')
      
      # Return with message.
      message = urllib.quote(message)
      return RESPONSE.redirect('manage_customizeDesignForm?lang=%s&manage_tabs_message=%s&cssId=%s'%(lang,message,cssId))


    ############################################################################
    ###
    ###   Interface IZMSWorkflowProvider: delegate to workflow_manager
    ###
    ############################################################################

    def getWfActivities(self):
      workflow_manager = getattr(self,'workflow_manager',None)
      if workflow_manager is None:
        return []
      return workflow_manager.getActivities()

    def getWfActivitiesIds(self):
      workflow_manager = getattr(self,'workflow_manager',None)
      if workflow_manager is None:
        return []
      return workflow_manager.getActivitiesIds()

    def getWfActivity(self, id):
      workflow_manager = getattr(self,'workflow_manager',None)
      if workflow_manager is None:
        return None
      return workflow_manager.getActivity(id)

    def getWfTransitions(self):
      workflow_manager = getattr(self,'workflow_manager',None)
      if workflow_manager is None:
        return []
      return workflow_manager.getTransitions()


    ############################################################################
    ###
    ###   Interface IZMSMetamodelProvider: delegate to metaobj_manager
    ###
    ############################################################################

    def getMetaobjId(self, name):
      return self.metaobj_manager.getMetaobjId( name)

    def getMetaobjIds(self, sort=1, excl_ids=[]):
      return self.metaobj_manager.getMetaobjIds( sort, excl_ids)

    def getMetaobj(self, id):
      return self.metaobj_manager.getMetaobj( id)

    def getMetaobjAttrIds(self, meta_id, types=[]):
      return self.metaobj_manager.getMetaobjAttrIds( meta_id, types)

    def getMetaobjAttrs(self, meta_id,  types=[]):
      return self.metaobj_manager.getMetaobjAttrs( meta_id)

    def getMetaobjAttr(self, meta_id, key):
      return self.metaobj_manager.getMetaobjAttr( meta_id, key)

    def getMetaobjAttrIdentifierId(self, meta_id):
      return self.metaobj_manager.getMetaobjAttrIdentifierId( meta_id)

    def notifyMetaobjAttrAboutValue(self, meta_id, key, value):
      return self.metaobj_manager.notifyMetaobjAttrAboutValue( meta_id, key, value)

    ############################################################################
    ###
    ###   Interface IZMSFormatProvider: delegate to format_manager
    ###
    ############################################################################

    def getTextFormatDefault(self):
      return self.format_manager.getTextFormatDefault()

    def getTextFormat(self, id, REQUEST):
      return self.format_manager.getTextFormat(id, REQUEST)

    def getTextFormats(self, REQUEST):
      return self.format_manager.getTextFormats(REQUEST)

    def getCharFormats(self):
      return self.format_manager.getCharFormats()

################################################################################