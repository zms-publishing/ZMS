################################################################################
# ZMSIndex.py
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
from Products.ZCatalog import ZCatalog
from Products.PluginIndexes.FieldIndex.FieldIndex import FieldIndex
from Products.PluginIndexes.PathIndex.PathIndex import PathIndex
import re
import sys
import time
# Product Imports.
from Products.zms import standard
from Products.zms import ZMSItem


################################################################################
###
###   Class
###
################################################################################
class ZMSIndex(ZMSItem.ZMSItem):

    # Properties.
    # -----------
    meta_type = 'ZMSIndex'
    zmi_icon = "fas fa-indent"
    icon_clazz = zmi_icon


    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Management Options
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def manage_options(self):
      return (
        {'label': 'ZMSIndex','action': 'manage_main'},
        )


    # Management Interface.
    # ---------------------
    manage_main = PageTemplateFile( 'zpt/ZMSIndex/manage_main', globals())

    # Catalog Id
    catalog_id = 'zcatalog_index'

    ############################################################################
    #  ZMSIndex.__init__: 
    #
    #  Initialise a new instance of ZMSInddex.
    ############################################################################
    def __init__(self):
      self.id = 'zmsindex'

    ############################################################################
    #  Initialize 
    ############################################################################
    def initialize(self):
      catalog = self.get_catalog()

    ##############################################################################
    # Event: Object Imported
    ##############################################################################
    def ObjectImported(self, context):
      request = self.REQUEST
      base = list(self.getRootElement().getPhysicalPath())[:-1]
      url = list(self.getDocumentElement().getPhysicalPath())[len(base):-1]
      request.set('url','{$'+['','/'.join(url)+'@'][len(url)>0]+'}')
      if self.getConfProperty('ZMSIndexZCatalog.ObjectImported.reindex',False) == True:
        self.manage_reindex(regenerate_duplicates=True)
      if self.getConfProperty('ZMSIndexZCatalog.ObjectImported.resync',False) == True:
        self.manage_resync()

    ##############################################################################
    # Event: Object Added
    ##############################################################################
    def ObjectAdded(self, context):
      catalog = self.get_catalog()
      def traverse(node):
         # Create new uid.
        node.get_uid(True)
        # Catalog object.
        self.catalog_object(catalog,node)
        # Traverse.
        for childNode in node.getChildNodes():
          traverse(childNode)
      traverse(context)
      return True


    ##############################################################################
    # Event: Object Moved
    ##############################################################################
    def ObjectMoved(self, context):
      catalog = self.get_catalog()
      def traverse(node):
        # Refresh index: add and remove.
        query = {'get_uid':node.get_uid()}
        row = catalog(query)
        for r in row:
          catalog.uncatalog_object(r['getPath'])
        self.catalog_object(catalog,node)
        # Traverse.
        for childNode in node.getChildNodes():
          traverse(childNode)
      traverse(context)

    ##############################################################################
    # Event: Object Removed
    ##############################################################################
    def ObjectRemoved(self, context):
      catalog = self.get_catalog()
      def traverse(node):
        # Uncatalog object.
        catalog.uncatalog_object(node.getPath())
        # Traverse.
        for childNode in node.getChildNodes():
          traverse(childNode)
      traverse(context)

    ##############################################################################
    # Get Log
    ##############################################################################
    def get_log(self, log, request):
      loglevel = request.get('loglevel','<NONE>')
      return '\n'.join([x for x in log if x.startswith('%s '%loglevel)])

    ##############################################################################
    # Get Catalog
    ##############################################################################
    def get_catalog(self, createIfNotExists=True):
      # Create catalog.
      zmsroot = self.getRootElement()
      home = zmsroot.getHome()
      catalog = getattr(home,self.catalog_id,None)
      if catalog is None:
        catalog = ZCatalog.ZCatalog(id=self.catalog_id, title=self.meta_id, container=home)
        home._setObject(catalog.id, catalog)
        catalog = getattr(home,self.catalog_id,None)
      # Index names.
      index_names = self.get_index_names(True)
      # Add indices.
      for index_name in index_names:
        if index_name not in catalog.indexes():
          index_type = FieldIndex(index_name)
          catalog.manage_addIndex(index_name,index_type)
      index_name = 'path'
      if index_name not in catalog.indexes():
        index_type = PathIndex(index_name)
        catalog.manage_addIndex(index_name,index_type)
      # Add columns
      for index_name in index_names + ['getPath']:
        if index_name not in catalog.schema():
          catalog.manage_addColumn(index_name)
      return catalog

    ##############################################################################
    # Get Index-Names
    ##############################################################################
    def get_index_names(self, complete=True):
      index_names = [x for x in getattr(self,'index_names','').split(',') if x]
      if complete:
        index_names = ['id','meta_id','get_uid'] + ['zcat_%s'%x for x in index_names]
      return index_names

    ##############################################################################
    # Catalog Object
    ##############################################################################
    def catalog_object(self, catalog, node, regenerate_duplicates=False):
      printed = []
      # Index names.
      index_names = self.get_index_names(False)
      # Prepare object.
      for attr_id in index_names:
        attr_name = 'zcat_%s'%attr_id
        value = node.attr(attr_id)
        setattr(node,attr_name,value)
      path = node.getPath()
      # Sanity check: if uid is already catalogued we have to generate new uid
      uid = node.get_uid()
      q = catalog({'get_uid':uid})
      if len(q) > 0:
        if regenerate_duplicates:
          node.get_uid(forced=True)
        printed.append('ERROR %s'%standard.writeError(node,'[ZMSIndex] WARNING duplicate uid: %s->%s'%(uid,node.get_uid())))
      # Catalog object.
      catalog.catalog_object(node, path)
      # Unprepare object.
      for attr_id in index_names:
        attr_name = 'zcat_%s'%attr_id
        delattr(node,attr_name)
      # return printed
      return printed

    ##############################################################################
    # Uncatalog Object
    ##############################################################################
    def uncatalog_object(self, catalog, node):
      printed = []
      # Prepare object.
      path = node.getPath()
      # Uncatalog object.
      catalog.uncatalog_object(node, path)
      # return printed
      return printed

    ##############################################################################
    # Reindex
    ##############################################################################
    def manage_reindex(self, regenerate_duplicates=False):
      """ ZMSIndex.manage_reindex """
      request = self.REQUEST
      response = request.RESPONSE
      log = []

      zmsroot = self.getRootElement()
      home = zmsroot.getHome()
      catalog = getattr(home,self.catalog_id,None)
      regenerate_duplicates = regenerate_duplicates or catalog is None

      # Visit tree
      def visit(node):
        l = []
        l.append(1)
        if node.meta_id == 'ZMS':
          # Clear catalog
          for i in catalog({'path':'/'.join(node.getPhysicalPath())}):
            path = i['getPath']
            log.append('INFO %s'%standard.writeBlock(self,'[ZMSIndex] uncatalog_object %s'%path))
            catalog.uncatalog_object(path)
        log.append('INFO %s'%standard.writeBlock(self,'[ZMSIndex] catalog_object %s %s'%(node.getPath(),str(node.get_uid()))))
        self.catalog_object(catalog,node,regenerate_duplicates)
        for childNode in node.getChildNodes():
          l.extend(visit(childNode))
        return l
      
      urls = [x for x in request['url'].split(',') if x]
      for url in urls:
        catalog = self.get_catalog()
        log.append('INFO %s'%standard.writeBlock(self,'[ZMSIndex] ### reindex for %s'%url))
        t0 = time.time()
        base = self.getLinkObj(url)
        if base is not None:
          count = visit(base.getDocumentElement())
          log.append('INFO %s'%standard.writeBlock(self,'[ZMSIndex] reindex for %s done: %i in %.2fsecs.'%(url,len(count),time.time()-t0)))
      return self.get_log(log,request)

    ##############################################################################
    # Test
    ##############################################################################
    def manage_test(self):
      """ ZMSIndex.manage_test """
      request = self.REQUEST
      response = request.RESPONSE
      log = []

      zmsroot = self.getRootElement()
      home = zmsroot.getHome()
      catalog = getattr(home,self.catalog_id,None)

      # Read catalog
      def read_catalog(node):
        path = '/'.join(node.getPhysicalPath())
        standard.writeBlock(self,'[ZMSIndex] ### read_catalog for %s'%path)
        return [(i['getPath'],i['get_uid']) for i in catalog({'path':path}) if i['getPath'].startswith(path)]
      
      # Visit tree
      def visit(node):
        l = [(node.getPath(),str(node.get_uid()))]
        for childNode in node.getChildNodes():
          l.extend(visit(childNode))
        return l
      
      if catalog is not None:
        urls = [x for x in request['url'].split(',') if x]
        for url in urls:
          log.append('INFO %s'%standard.writeBlock(self,'[ZMSIndex] ### test for %s'%url))
          t0 = time.time()
          base = self.getLinkObj(url)
          if base is not None:
            from_catalog = read_catalog(base)
            from_tree = visit(base)
            c = 0
            for i in from_catalog:
              if i not in from_tree:
                if c == 0:
                  log.append('INFO %s'%standard.writeBlock(self,'[ZMSIndex] found in catalog, missing in tree:'))
                log.append('INFO %s'%standard.writeBlock(self,'[ZMSIndex] %i.: %s'%(c,str(i))))
                c += 1
            c = 0
            for i in from_tree:
              if i not in from_catalog:
                if c == 0:
                  log.append('INFO %s'%standard.writeBlock(self,'[ZMSIndex] found in tree, missing in catalog:'))
                log.append('INFO %s'%standard.writeBlock(self,'[ZMSIndex] %i.: %s'%(c,str(i))))
                c += 1
            log.append('INFO %s'%standard.writeBlock(self,'[ZMSIndex] test for %s done: %i / %i in %.2fsecs.'%(url,len(from_catalog),len(from_tree),time.time()-t0)))
      return self.get_log(log,request)

    ##############################################################################
    # Resync
    ##############################################################################
    def manage_resync(self):
      """ ZMSIndex.manage_resync """
      request = self.REQUEST
      response = request.RESPONSE
      session = request.SESSION
      log = []

      domains = {request['SERVER_URL']:''}

      zmsroot = self.getRootElement()
      home = zmsroot.getHome()
      catalog = getattr(home,self.catalog_id,None)

      def query(k,v):
        return catalog({k:v})

      def getLinkObj(data_id):
        if data_id.startswith('{$') and data_id.find('id:')>0 and data_id.endswith('}'):
          if data_id.startswith('{$') and data_id.endswith('}'):
            data_id = data_id[2:-1]
          for brain in query('get_uid',data_id):
            ids = [x for x in brain['getPath'].split('/') if x]
            ob = zmsroot
            for id in [x for x in ids if x]:
              ob = getattr(ob,id,None)
              if ob is None:
                break
            return ob
        return None

      def find_brain(data_id):
        rtn = None
        if data_id.startswith('{$') and data_id.find('id:')>0 and data_id.endswith('}'):
          if data_id.startswith('{$') and data_id.endswith('}'):
            data_id = data_id[2:-1]
            if data_id.find(';') > 0:
              data_id = data_id[:data_id.find(';')]
          for brain in query('get_uid',data_id):
            rtn = brain
            break
        else:
          if data_id.startswith('{$') and data_id.endswith('}'):
            data_id = data_id[2:-1].replace('@','/content/')
            if data_id.find(';') > 0:
              data_id = data_id[:data_id.find(';')]
          ids = [x for x in data_id.split('/') if x]
          brains = []
          if ids:
            for brain in query('id',ids[-1]):
              if brain['getPath'].endswith(data_id):
                log.append('INFO %s'%standard.writeBlock(self,'[ZMSIndex] find_brain.100 %s->%s'%(data_id,brain['getPath'])))
                brains.append((100,brain))
              elif ids[-1] == 'content' and len(ids)>=2 and brain['getPath'].endswith('/'.join(ids[-2:])):
                score = len([1 for id in ids if id in brain['getPath'].split('/')])
                log.append('INFO %s'%standard.writeBlock(self,'[ZMSIndex] find_brain#1 %i->%s'%(score,brain['getPath'])))
                brains.append((score,brain))
              else:
                score = len([1 for id in ids if id in brain['getPath'].split('/')])
                log.append('INFO %s'%standard.writeBlock(self,'[ZMSIndex] find_brain#2 %i->%s'%(score,brain['getPath'])))
                brains.append((score,brain))
          if brains:
            brains = sorted(brains,key=lambda x:x[0])
            log.append('INFO %s'%standard.writeBlock(self,'[ZMSIndex] find_brain brains=%s'%str([(x[0],x[1]['getPath']) for x in brains])))
            rtn = brains[-1][1]
        log.append('INFO %s'%standard.writeBlock(self,'[ZMSIndex] find_brain %s->%s'%(data_id,str(rtn is not None))))
        return rtn

      def find_decl_id(base, id):
        for o in base.getChildNodes():
          for l in o.getLanguages():
            r = {'lang':l}
            decl_id = o.getDeclId(r)
            if decl_id == id:
              return o
        return None

      def find_node(base, path):
        ref = base
        if path.find('?')>0:
          if path.find('#')>path.find('?'):
            path = path[:path.find('?')]+path[path.find('#'):]
          else:
            path = path[:path.find('?')]
        ids = []
        for id in path.split('/'):
          ids.extend(id.split('#'))
        ids = [x for x in ids if x not in ['','.','..'] and not (x.startswith('index_') and x.endswith('.html'))]
        log.append('INFO %s'%standard.writeBlock(self,'[ZMSIndex] find_node ids=%s'%str(ids)))
        if len(ids)==0 or len([x for x in ids if x.startswith('manage')]) > 0:
          return None
        # find id in catalog
        brain = find_brain('/'.join(ids))
        if brain is not None:
          return brain
        # find declarative id
        while ref is not None:
          o = find_decl_id(ref,ids[0])
          if o is not None:
            for id in ids[1:]:
              o = find_decl_id(o,id)
              if o is None:
                return None
            return find_brain(o.get_uid())
          ref = ref.getParentNode()
        return ref

      def handleInline(node,v):
        p = r'<dtml-var "getLinkUrl\(\'(.*?)\'(,REQUEST)?\)">'
        r = re.compile(p)
        for f in r.findall(v):
          data_id = f[0]
          old = '<dtml-var "getLinkUrl(\'%s\'%s)">'%(data_id,f[1])
          ref = node.getLinkObj(data_id)
          if ref:
            new = ref.absolute_url()
            log.append('INFO %s'%standard.writeBlock(node,'[ZMSIndex] handleInline %s->%s'%(old,new)))
            v = v.replace(old,new)
        p = r'<a(.*?)>(.*?)<\\/a>'
        r = re.compile(p)
        for f in r.findall(v):
          data_data = ''
          brain = None
          d = dict(re.findall(r'\s(.*?)="(.*?)"',f[0]))
          if brain is None and 'data-id' in d:
            data_id = d['data-id']
            log.append('INFO %s'%standard.writeBlock(node,'[ZMSIndex] handleInline data_id=%s'%data_id))
            brain = find_brain(data_id)
            if data_id.find(';') > 0:
              data_data = data_id[data_id.find(';'):-1]
          if brain is None and 'href' in d:
            href = d['href']
            href = re.sub(r'http://localhost:(\d)*','',href)
            for domain in domains:
              path = domains[domain]
              href = re.sub(domain,path,href)
            log.append('INFO %s'%standard.writeBlock(node,'[ZMSIndex] handleInline href=%s'%href))
            if href.startswith('.') or href.startswith('/'):
              nf = re.compile(r'(.*?)\?op=not_found&url={\$(.*?)}').findall(href)
              if nf:
                url = nf[0][1]
              else:
                url = href
              brain = find_node(node,url)
          old_data_id = d.get('data_id')
          old_url = d.get('href')
          data_id = None
          if brain is not None:
            data_id = '{$%s%s}'%(brain['get_uid'],data_data)
            d['data-id'] = data_id
            old = (p.replace('\\','').replace('(.*?)','%s'))%tuple(f)
            title = f[1]
            new = '<a %s>%s</a>'%(' '.join(['%s="%s"'%(x,d[x]) for x in d]),title)
            if old != new:
              ref = getLinkObj('{$%s}'%brain['get_uid'])
              ref.registerRefObj(node)
              log.append('INFO %s'%standard.writeBlock(node,'[ZMSIndex] handleInline %s->%s'%(old,new)))
              v = v.replace(old,new)
        return v

      def handleUrl(node,v):
        standard.writeLog(node,'[ZMSIndex] handleUrl %s'%v)
        if v.startswith('{$') and v.endswith('}'):
          old = v
          if not (v.startswith('{$__') and v.endswith('__}')) \
              and not (v.startswith('{$') and v.find('id:')>0 and v.endswith('}')):
            data_data = ''
            brain = find_brain(v)
            if brain is not None:
              if v.find(';') > 0:
                data_data = v[v.find(';'):-1]
              data_id = '{$%s%s}'%(brain['get_uid'],data_data)
              new = data_id
              if old != new:
                standard.writeBlock(node,'[ZMSIndex] handleUrl %s->%s'%(old,new))
                v = new
                ref = getLinkObj('{$%s}'%brain['get_uid'])
                ref.registerRefObj(node)
            else:
              log.append('ERROR %s'%standard.writeBlock(node,'[ZMSIndex] handleUrl ### MISSING LINKTARGET %s'%(v)))
              v = '{$__%s__}'%v[2:-1]
        return v

      def handleItem(node,v):
        if type(v) is list:
          v = handleList(node,v)
        elif type(v) is dict:
          v = handleDict(node,v)
        elif type(v) is str or type(v) is bytes:
          v = handleInline(node,v)
        return v

      def handleDict(node,v):
        nd = {}
        for i in v:
          nd[i] = handleItem(node,v[i])
        return nd

      def handleList(node,v):
        nl = []
        for i in v:
          nl.append(handleItem(node,i))
        return nl

      objAttrCache = {}
      def getObjAttrsFast(node):
        if node.meta_id not in objAttrCache:
          objAttrs = []
          for key in [x for x in node.getObjAttrs() if not x.startswith('manage')]:
            objAttr = node.getObjAttr(key)
            datatype = objAttr['datatype']
            if datatype in ['richtext','string','text','list','dict','url']:
              objAttrs.append(objAttr)
          objAttrCache[node.meta_id] = objAttrs
        return objAttrCache[node.meta_id]

      def visit(node):
        count = []
        count.append(1)
        log.append('INFO %s'%standard.writeBlock(node,'[ZMSIndex] resync'))
        
        try:
          if node.meta_id!='ZMSLinkElement' and node.getType() == 'ZMSRecordSet':
            objAttrs = node.getMetaobjAttrs(node.meta_id)
            key = [x for x in objAttrs if x['type']=='list'][0]['id']
            for obj_vers in node.getObjVersions():
              l = self.operator_getattr(obj_vers,key,[])
              for r in l:
                for objAttr in objAttrs:
                  datatype = objAttr['type']
                  if datatype in ['richtext','string','text','url']:
                    v = r.get(objAttr['id'],None)
                    if v is not None and type(v) is str:
                      o = v
                      if datatype in ['richtext','string','text'] in [bytes,str]:
                        v = handleInline(node,v)
                      elif datatype in ['url'] and type(v) in [bytes,str]:
                        v = handleUrl(node,v)
                      if o != v:
                        r[objAttr['id']] = v
              self.operator_setattr(obj_vers,key,l)
          else:
            for objAttr in getObjAttrsFast(node):
              key = objAttr['id']
              datatype = objAttr['datatype']
              lang_suffixes = ['']
              if objAttr['multilang']:
                lang_suffixes = ['_%s'%x for x in node.getLangIds()]
              for lang_suffix in lang_suffixes:
                for obj_vers in node.getObjVersions():
                  v = self.operator_getattr(obj_vers,'%s%s'%(key,lang_suffix),None)
                  if v is not None:
                    o = v
                    if datatype=='url':
                      if type(v) in [bytes,str]:
                        v = handleUrl(node,v)
                    else:
                      if type(v) in [bytes,dict,list,str]:
                        v = handleItem(node,v)
                    if o != v:
                      self.operator_setattr(obj_vers,'%s%s'%(key,lang_suffix),v)
        except:
          t,v,tb = sys.exc_info()
          msg = ''.join(format_exception(t, v, tb))
          log.append('ERROR %s'%standard.writeBlock(node,'[ZMSIndex] can\'t visit %s'%msg))

        # premature commit
        req_key = 'ZMSIndexZCatalog.resync.transaction_count'
        cfg_key = 'ZMSIndexZCatalog.resync.transaction_size'
        if request.get(req_key,0)>=int(self.getConfProperty(cfg_key,1000000)):
          log.append('INFO %s'%standard.writeBlock(node,'[ZMSIndex] +++ COMMIT +++'))
          import transaction
          transaction.commit()
          request.set(req_key,0)
        request.set(req_key,request.get(req_key,0)+1)

        for childNode in node.getChildNodes():
          count.extend(visit(childNode))

        return count

      def init_domains(doc,domains):
        domain = doc.getConfProperty('ASP.ip_or_domain','')
        if domain != '':
          domain = '^http(\\w)?://%s'%domain
          path = '/'.join(doc.getPhysicalPath())
          if domain in domains:
            log.append('ERROR %s'%standard.writeBlock(doc,'[ZMSIndex] ### init_domains DUPLICATE %s=%s'%(domain,path)))
          else:
            domains[domain] = path
            log.append('INFO %s'%standard.writeBlock(doc,'[ZMSIndex] init_domains %s=%s'%(domain,path)))
        for portalClient in doc.getPortalClients():
          init_domains(portalClient,domains)
      if int(request.get('i',0)) == 0 or session is None or session.get('ZMSIndex_domains') is None:
        init_domains(zmsroot,domains)
        if session is not None:
          session.set('ZMSIndex_domains',domains)
      if session is not None:
        domains = session.get('ZMSIndex_domains')

      urls = [x for x in request['url'].split(',') if x]
      for url in urls:
        log.append('INFO %s'%standard.writeBlock(self,'[ZMSIndex] ### resync for %s'%url))
        t0 = time.time()
        base = self.getLinkObj(url)
        if base is not None:
          count = visit(base)
          log.append('INFO %s'%standard.writeBlock(self,'[ZMSIndex] resync for %s done: %i in %.2fsecs.'%(url,len(count),time.time()-t0)))
      return self.get_log(log,request)

    # README: To use redirecting short urls like /doi/10.1109/5.771073 or /doi/faq 
    # based on ZMSIndex, please add a meta-attribute 'attr_dc_identifier_doi' to the 
    # document nodes definition (ZMSFolder, ZMSDocument) and add this meta-attribute-
    # name to the ZMSIndex 'Attributes' list. You can fill the new attribute implicitly
    # with any other (existing) attribute value by declaring it's type as Py-Script 
    # and using following code snippet:
    # ---------------------
    #  from Products.zms import standard
    #  return standard.id_quote(zmscontext.attr('titlealt'))
    # ---------------------
    # After REINDEXING the ZMSIndex contains a new field index 'zcat_attr_dc_identifier_doi'. 
    # Based on this additional index any indexed string can be resolved as redirect to 
    # the path oft its containing document.
    def doi(self):
      request = self.REQUEST
      RESPONSE =  request.RESPONSE
      zmscontext = self.getDocumentElement()
      path_ = 'index_html'

      if request['traverse_subpath']:
        path_ = standard.id_quote('_'.join(request['traverse_subpath']))

      catalog = self.get_catalog()
      query = {'zcat_attr_dc_identifier_doi':path_}
      rows = catalog(query)

      for x in rows:
        # ### test ####
        # print x['get_uid']
        # print zmscontext.getLinkObj('{$%s}'%x['get_uid'])
        # print zmscontext.getLinkObj('{$%s}'%x['get_uid']).absolute_url()
        # return printed
        # #############
        ob = zmscontext.getLinkObj('{$%s}'%x['get_uid'])
        RESPONSE.redirect(ob.absolute_url())
        return standard.FileFromData(zmscontext,ob.absolute_url())

      # Return a string identifying this script.
      return standard.FileFromData(zmscontext,"'%s' not found!"%path_)

################################################################################
