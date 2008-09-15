"""
Add External Method with the following option:

'Id':       urls.xml
'Title':    Mirror-Manager
'Module':   zms.urls_xml
'Function': manage_getMirrorURLs
"""
#
# Copyright 2008 {xmachina GmbH. All rights reserved.
# xmachina. Use is subject to license terms.
# 

import Products.zms._blobfields
import Products.zms._fileutil
import Products.zms._globals
import urllib

# see _blobfields.py::recurse_downloadRessources
def recurseRessources(self, base_path, REQUEST, incl_embedded, RESPONSE):
    try:
        RESPONSE.write('<!-- DEBUG recurseRessources(self, %s, REQUEST, incl_embedded, RESPONSE) -->\n'%(base_path))
    except:
        RESPONSE.write('<!-- ERROR exception -->\n')
    
    root = getattr( self, '__root__', None)
    if root is not None or self.meta_type == 'ZMSTrashcan':
        return
    ob = self
    if ob.meta_type != 'ZMS':
        base_path += self.id + '/'
    if ob.meta_type == 'ZMSLinkElement' and ob.isEmbedded( REQUEST) and incl_embedded:
        ob = ob.getRefObj()
    if ob is None:
        return
    
    # Attributes.
    keys = ob.getObjAttrs().keys()
    for key in keys:
        #RESPONSE.write('<!-- DEBUG %s -->\n'%(key))
        obj_attr = ob.getObjAttr(key)
        datatype = obj_attr['datatype_key']
        if datatype in Products.zms._globals.DT_BLOBS:
            for lang in ob.getLangIds():
                #RESPONSE.write('<!-- DEBUG Products.zms._globals.DT_BLOBS %s -->\n'%(lang))
                try:
                    if obj_attr['multilang']==1 or lang==ob.getPrimaryLanguage() or (obj_attr['multilang']==0 and lang!=ob.getPrimaryLanguage()):
                        req = {'lang':lang,'preview':'preview'}
                        obj_vers = ob.getObjVersion(req)
                        blob = ob._getObjAttrValue(obj_attr,obj_vers,lang)
                        if blob is not None: 
                            filename = blob.getFilename()
                            filename = Products.zms._blobfields.getLangFilename(ob,filename,lang)
                            filename = '%s%s'%(base_path,filename)
                            filename = Products.zms._fileutil.getOSPath(filename)
                            RESPONSE.write('<url content_type="%s">%s</url>\n'%(blob.getContentType(), filename))
                except:
                    s = Products.zms._globals.writeException(ob,"[recurse_downloadRessources]: Can't export %s"%key)
                    RESPONSE.write('<!-- ERROR %s -->\n'%(s))
        elif datatype == Products.zms._globals.DT_LIST and obj_attr.get('type') in ['image','file']:
            for lang in ob.getLangIds():
                #RESPONSE.write('<!-- DEBUG Products.zms._globals.DT_LIST %s -->\n'%(lang))
                try:
                    if obj_attr['multilang']==1 or lang==ob.getPrimaryLanguage() or (obj_attr['multilang']==0 and lang!=ob.getPrimaryLanguage()):
                        req = {'lang':lang,'preview':'preview'}
                        obj_vers = ob.getObjVersion(req)
                        blobs = ob._getObjAttrValue(obj_attr,obj_vers,lang)
                        i = 0
                        for blob in blobs:
                            filename = blob.getFilename()
                            filename = Products.zms._blobfields.getLangFilename(ob,filename,lang)
                            filename = '%s@%i/%s'%(base_path,i,filename)
                            filename = Products.zms._fileutil.getOSPath(filename)
                            RESPONSE.write('<url content_type="%s">%s</url>\n'%(blob.getContentType(), filename))
                            i += 1
                except:
                    s = Products.zms._globals.writeException(ob,"[recurse_downloadRessources]: Can't export %s"%key)
                    RESPONSE.write('<!-- ERROR %s -->\n'%(s))
    if ob.meta_type == 'ZMSCustom':
        metaObjId = ob.meta_id
        for metaObjAttrId in ob.getMetaobjAttrIds( metaObjId):
            metaObjAttr = ob.getMetaobjAttr( metaObjId, metaObjAttrId)
            if metaObjAttr['type'] == 'resource':
                try:
                    blob = metaObjAttr['custom']
                    filename = blob.getFilename()
                    filename = '%s%s'%(base_path,filename)
                    filename = Products.zms._fileutil.getOSPath(filename)
                    RESPONSE.write('<url content_type="%s">%s</url>\n'%(blob.getContentType(), filename))
                except:
                    Products.zms._globals.writeException( ob, "[recurse_downloadRessources]: Can't export %s.%s"%(metaObjId,metaObjAttrId))
    # Process children.
    for child in ob.getChildNodes():
        # Return list of ressources.
        recurseRessources( child, base_path, REQUEST, incl_embedded, RESPONSE)
    
    return


# see _exportable.py::recurse_downloadHtmlPages
def recurseHtmlPages(self, obj, path, lang, REQUEST, RESPONSE):
    try:
        RESPONSE.write('<!-- DEBUG recurseHtmlPages(self, obj, %s, %s, REQUEST, RESPONSE) -->\n'%(path, lang))
    except:
        RESPONSE.write('<!-- ERROR exception -->\n')
    
    level = obj.getLevel()
    
    dctOp = {'index':'','sitemap':'sitemap','index_print':'print'}
    for key in dctOp.keys():
        if key == 'index' and \
                level > 0 and \
                self.getConfProperty('ZMS.pathhandler',0) != 0 and \
                self.getConfProperty('ZMS.export.pathhandler',0) == 1:
            filename = '%s/../%s%s'%( path, obj.getDeclId(REQUEST), obj.getPageExt(REQUEST))
        else:
            if key == 'sitemap':
                pageext = '.html'
            else:
                pageext = obj.getPageExt( REQUEST)
            filename = '%s/%s_%s%s'%( path, key, lang, pageext)
        
        RESPONSE.write('<url>%s</url>\n'%(filename))
        
        # Process DTML-methods of meta-objects.
        if self.zms_build >= '131': # >= ZMS-2.11
          for metadictAttrId in self.getMetaobjAttrIds( obj.meta_id):
            try:
              metadictAttr = self.getMetaobjAttr( obj.meta_id, metadictAttrId)
              if metadictAttr is not None and metadictAttr['meta_type'] and metadictAttr['type'] in self.getMetaobjIds( sort=0):
                metaObj = self.getMetaobj( metadictAttr['type'])
                if metaObj['type'] == 'ZMSResource':
                  for metadictObj in obj.getObjChildren( metadictAttr['id'], REQUEST):
                    for metaObjAttr in metaObj['attrs']:
                      if metaObjAttr['type'] in [ 'DTML Document', 'DTML Method']:
                        filename = '%s/%s'%( path, metaObjAttr['id'])
                        RESPONSE.write('<url>%s</url>\n'%(filename))
            except:
                    s = Products.zms._globals.writeException( self, "[recurse_downloadHtmlPages]: Can't process DTML-method '%s' of meta-object"%metadictAttr)
                    RESPONSE.write('<!-- ERROR %s -->\n'%(s))
        else: # < ZMS-2.11
          for metadictAttrId in self.getMetadictAttrs( obj.meta_type):
              try:
                  metadictAttr = self.getMetadictAttr( metadictAttrId)
                  if metadictAttr['type'] in self.getMetaobjIds():
                      metaObj = self.getMetaobj( metadictAttr['type'])
                      if metaObj['type'] == 'ZMSResource':
                          for metadictObj in obj.getObjChildren( metadictAttr['id'], REQUEST):
                              for metaObjAttr in metaObj['attrs']:
                                  if metaObjAttr['type'] in [ 'DTML Document', 'DTML Method']:
                                      filename = '%s/%s'%( path, metaObjAttr['id'])
                                      RESPONSE.write('<url>%s</url>\n'%(filename))
              except:
                  s = Products.zms._globals.writeException( self, "[recurse_downloadHtmlPages]: Can't process DTML-method '%s' of meta-object"%metadictAttr)
                  RESPONSE.write('<!-- ERROR %s -->\n'%(s))
    
    # Process children.
    for child in obj.getChildNodes(REQUEST,self.PAGES):
        recurseHtmlPages(self,child,'%s/%s'%(path,child.getDeclId(REQUEST)),lang, REQUEST, RESPONSE)


# see _exportable.py::exportFolder
def recurseFolder(self, root, path, id, REQUEST, RESPONSE):
    try:
        RESPONSE.write('<!-- DEBUG recurseFolder(%s, %s, %s, %s, REQUEST, RESPONSE) -->\n'%(self, "root", path, id))
    except:
        RESPONSE.write('<!-- ERROR exception -->\n')
    
    if hasattr(root,id):
        folder = getattr(root,id)
        if folder.meta_type == 'Folder':
            for ob in folder.objectValues():
                if ob.meta_type == 'Folder':
                    ob_id = ob.id
                    recurseFolder(self,ob,'%s/%s'%(path,id), ob_id, REQUEST, RESPONSE)
                else:
                    try:
                        ob_id = ob.id()
                    except:
                        ob_id = str(ob.id)
                    #if ob.meta_type in [ 'DTML Document', 'DTML Method']:
                    #    ob = Products.zms._globals.dt_html(self,ob.raw,REQUEST)
                    RESPONSE.write('<url>%s/%s/%s</url>\n'%(path,id,ob_id))


# see _exportable::exportContentRessources
def recurseContentRessources(self, REQUEST, RESPONSE):
    try:
        RESPONSE.write('<!-- DEBUG recurseContentRessources(self, REQUEST, RESPONSE) -->\n')
    except:
        RESPONSE.write('<!-- ERROR exception -->\n')
    
    #-- JavaScript
    # diese müssen als comlib_ger.js usw. exportiert werden(!)
    for js in [ 'comlib', 'formlib', 'datelib', 'formlib', 'zmilib', 'styleswitcher']:
      attr = getattr(self,'%s_js'%(js),None)
      if attr:
        data = attr(self,REQUEST)
        filename = '%s.js'%js
        RESPONSE.write('<url>/%s</url>\n'%(filename))


def manage_getMirrorURLs(self, REQUEST, RESPONSE):
    lang = REQUEST.get('lang',self.getPrimaryLanguage())
    REQUEST.set('lang',lang)
    RESPONSE.write('<?xml version="1.0" encoding="utf-8"?>\n');
    RESPONSE.write('<urls base="%s">\n'%(self.getHome().absolute_url()));
    
    # see _exportable.py::exportRessources, etc.
    folder = '/misc_/zms'
    for obj_id in self.misc_.zms._d.keys():
        RESPONSE.write('<url>%s/%s</url>\n'%(folder, obj_id))
    
    for id in [ 'common', 'instance']:
        recurseFolder( self, self.getHome(), "", id, REQUEST, RESPONSE)
    
    recurseContentRessources( self, REQUEST, RESPONSE)
    
    recurseRessources(self, "/content/", REQUEST, True, RESPONSE)
    recurseHtmlPages(self, self, "/content", lang, REQUEST, RESPONSE)
    
    RESPONSE.write('</urls>\n');
    return 
