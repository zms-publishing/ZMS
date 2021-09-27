from Products.ZCatalog import ZCatalog
from traceback import format_exception
import logging
import os
import re
import sys
import time
import uuid

def ZMSIndexZCatalog_func_( self, *args, **kwargs):
  meta_types = list(self.dGlobalAttrs)
  zmsindex = getattr(self,'zmsindex',None)
  zmsindex_index_names = []
  if zmsindex:
    zmsindex_index_names.extend([x for x in getattr(zmsindex,'index_names','').split(',') if x])
  index_names = ['id','meta_id','get_uid'] + ['zcat_%s'%x for x in zmsindex_index_names]
  request = self.REQUEST
  logger = logging.getLogger('event.ZMS')
  loglevels = [logging.DEBUG,logging.INFO,logging.ERROR]
  loglevel = loglevels[loglevels.index({'DEBUG':logging.DEBUG,'INFO':logging.INFO,'ERROR':logging.ERROR}[request.get('loglevel','INFO')]):]

  printed = []
  def write(l,c,s):
    from DateTime import DateTime
    dt = DateTime()
    line = '%s %s@%s %s'%(dt.strftime("%Y-%m-%d %H:%M:%S,%f"),c.getPath(),c.meta_id,str(s))
    logger.log(l,line)
    if l in loglevel:
      printed.append(line)
  def writeDebug(c,s):
    write(logging.DEBUG,c,s)
  def writeInfo(c,s):
    write(logging.INFO,c,s)
  def writeError(c,s):
    write(logging.ERROR,c,s)

  def catalog_object(catalog,node,regenerate_duplicates=False):
    # Prepare object.
    for attr_id in zmsindex_index_names:
      attr_name = 'zcat_%s'%attr_id
      value = node.attr(attr_id)
      setattr(node,attr_name,value)
    path = node.getPath()
    # Sanity check: if uid is already catalogued we have to generate new uid
    q = catalog({'get_uid':node.get_uid()})
    if len(q) > 0:
      if regenerate_duplicates:
        node._uid = str(uuid.uuid4())
      writeError(node,'[ZMSIndexZCatalog_func_] WARNING duplicate uid: %s'%node.get_uid())
    # Catalog object.
    catalog.catalog_object(node, path)
    # Unprepare object.
    for attr_id in zmsindex_index_names:
      attr_name = 'zcat_%s'%attr_id
      delattr(node,attr_name)

  try:
    zmsroot = self.getRootElement()
    home = zmsroot.getHome()
    id = 'zcatalog_index'
    catalog = getattr(home,id,None)
    func_ = None
    if len(args) > 0:
      func_ = args[0]
    else:
      func_ = request.get('ZMSIndexZCatalog_func_')
    writeDebug(self,'ZMSIndexZCatalog.%s:'%(func_))

    ##############################################################################
    # Get uid
    ##############################################################################
    if func_ == 'get_uid':
      forced = args[1]
      if forced or '_uid' not in self.__dict__ or len(getattr(self,'_uid',''))==0 or len(getattr(self,'_uid','').split('-'))<5:
        self._uid = str(uuid.uuid4())
      return 'uid:%s'%self._uid

    ##############################################################################
    # Catalog Object
    ##############################################################################
    elif func_ == 'catalog_object':
      if catalog is not None:
        catalog_object(catalog,self)
      return None

    ##############################################################################
    # Uncatalog Object
    ##############################################################################
    elif func_ == 'uncatalog_object':
      if catalog is not None:
        path = args[1]
        catalog.uncatalog_object(path)
      return None

    ##############################################################################
    # Reindex
    ##############################################################################
    elif func_ == 'reindex':
      regenerate_duplicates = catalog is None

      def recreate_catalog():
        writeInfo(self,'[ZMSIndexZCatalog_func_] ### recreate catalog')
        # Create catalog.
        catalog = getattr(home,id,None)
        if catalog is None:
          catalog = ZCatalog.ZCatalog(id=id, title=self.meta_id, container=home)
          home._setObject(catalog.id, catalog)
          catalog = getattr(home,id,None)
          # Add indices.
          for index_name in index_names:
            catalog.manage_addIndex(index_name,'FieldIndex')
          catalog.manage_addIndex('path','PathIndex')
          # Add columns
          for index_name in index_names + ['getPath']:
            catalog.manage_addColumn(index_name)
        return catalog

      # Visit tree
      def visit(node):
        l = []
        l.append(1)
        if node.meta_id == 'ZMS':
          # Activate implicitly
          meta_id = 'ZMSIndexZCatalog'
          node.setConfProperty('ExtensionPoint.ZMSObject.get_uid','%s.get_uid'%meta_id)
          node.setConfProperty('ExtensionPoint.ZReferableItem.getRefObjPath','%s.getRefObjPath'%meta_id)
          node.setConfProperty('ExtensionPoint.ZReferableItem.getLinkObj','%s.getLinkObj'%meta_id)
          # Clear catalog
          for i in catalog({'path':'/'.join(node.getPhysicalPath())}):
            path = i['getPath']
            writeInfo(self,'[ZMSIndexZCatalog_func_] uncatalog_object %s'%path)
            catalog.uncatalog_object(path)
        writeInfo(self,'[ZMSIndexZCatalog_func_] catalog_object %s %s'%(node.getPath(),str(node.get_uid())))
        catalog_object(catalog,node,regenerate_duplicates)
        for childNode in node.objectValues(meta_types):
          l.extend(visit(childNode))
        return l
      
      urls = [x for x in request['url'].split(',') if x]
      for url in urls:
        if catalog is None or self == home:
          catalog = recreate_catalog()
        writeInfo(self,'[ZMSIndexZCatalog_func_] ### reindex for %s'%url)
        t0 = time.time()
        base = self.getLinkObj(url)
        if base is not None:
          count = visit(base.getDocumentElement())
          writeInfo(self,'[ZMSIndexZCatalog_func_] reindex for %s done: %i in %.2fsecs.'%(url,len(count),time.time()-t0))

    ##############################################################################
    # Test
    ##############################################################################
    elif func_ == 'test':

      # Read catalog
      def read_catalog(node):
        path = '/'.join(node.getPhysicalPath())
        writeInfo(self,'[ZMSIndexZCatalog_func_] ### read_catalog for %s'%path)
        return [(i['getPath'],i['get_uid']) for i in catalog({'path':path}) if i['getPath'].startswith(path)]
      
      # Visit tree
      def visit(node):
        l = [(node.getPath(),str(node.get_uid()))]
        for childNode in node.objectValues(meta_types):
          l.extend(visit(childNode))
        return l
      
      if catalog is not None:
        urls = [x for x in request['url'].split(',') if x]
        for url in urls:
          writeInfo(self,'[ZMSIndexZCatalog_func_] ### test for %s'%url)
          t0 = time.time()
          base = self.getLinkObj(url)
          if base is not None:
            from_catalog = read_catalog(base)
            from_tree = visit(base)
            c = 0
            for i in from_catalog:
              if i not in from_tree:
                if c == 0:
                  writeInfo(self,'[ZMSIndexZCatalog_func_] found in catalog, missing in tree:')
                writeInfo(self,'[ZMSIndexZCatalog_func_] %i.: %s'%(c,str(i)))
                c += 1
            c = 0
            for i in from_tree:
              if i not in from_catalog:
                if c == 0:
                  writeInfo(self,'[ZMSIndexZCatalog_func_] found in tree, missing in catalog:')
                writeInfo(self,'[ZMSIndexZCatalog_func_] %i.: %s'%(c,str(i)))
                c += 1
            writeInfo(self,'[ZMSIndexZCatalog_func_] test for %s done: %i / %i in %.2fsecs.'%(url,len(from_catalog),len(from_tree),time.time()-t0))

    ##############################################################################
    # Resync
    ##############################################################################
    elif func_ == 'resync':
      if catalog is not None:
        domains = {request['SERVER_URL']:''}

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
                  writeDebug(self,'[ZMSIndexZCatalog_func_] find_brain.100 %s->%s'%(data_id,brain['getPath']))
                  brains.append((100,brain))
                elif ids[-1] == 'content' and len(ids)>=2 and brain['getPath'].endswith('/'.join(ids[-2:])):
                  score = len([1 for id in ids if id in brain['getPath'].split('/')])
                  writeDebug(self,'[ZMSIndexZCatalog_func_] find_brain#1 %i->%s'%(score,brain['getPath']))
                  brains.append((score,brain))
                else:
                  score = len([1 for id in ids if id in brain['getPath'].split('/')])
                  writeDebug(self,'[ZMSIndexZCatalog_func_] find_brain#2 %i->%s'%(score,brain['getPath']))
                  brains.append((score,brain))
            if brains:
              brains = sorted(brains,key=lambda x:x[0])
              writeDebug(self,'[ZMSIndexZCatalog_func_] find_brain brains=%s'%str([(x[0],x[1]['getPath']) for x in brains]))
              rtn = brains[-1][1]
          writeDebug(self,'[ZMSIndexZCatalog_func_] find_brain %s->%s'%(data_id,str(rtn is not None)))
          return rtn

        def find_decl_id(base, id):
          for o in base.objectValues(meta_types):
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
          writeDebug(self,'[ZMSIndexZCatalog_func_] find_node ids=%s'%str(ids))
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
          p = '<dtml-var "getLinkUrl\(\'(.*?)\'(,REQUEST)?\)">'
          r = re.compile(p)
          for f in r.findall(v):
            data_id = f[0]
            old = '<dtml-var "getLinkUrl(\'%s\'%s)">'%(data_id,f[1])
            ref = node.getLinkObj(data_id)
            if ref:
              new = ref.absolute_url()
              writeDebug(node,'[ZMSIndexZCatalog_func_] handleInline %s->%s'%(old,new))
              v = v.replace(old,new)
          p = '<a(.*?)>(.*?)<\\/a>'
          r = re.compile(p)
          for f in r.findall(v):
            data_data = ''
            brain = None
            d = dict(re.findall('\\s(.*?)="(.*?)"',f[0]))
            if brain is None and 'data-id' in d:
              data_id = d['data-id']
              writeDebug(node,'[ZMSIndexZCatalog_func_] handleInline data_id=%s'%data_id)
              brain = find_brain(data_id)
              if data_id.find(';') > 0:
                data_data = data_id[data_id.find(';'):-1]
            if brain is None and 'href' in d:
              href = d['href']
              href = re.sub('http://localhost:(\\d)*','',href)
              for domain in domains:
                path = domains[domain]
                href = re.sub(domain,path,href)
              writeDebug(node,'[ZMSIndexZCatalog_func_] handleInline href=%s'%href)
              if href.startswith('.') or href.startswith('/'):
                nf = re.compile('(.*?)\\?op=not_found&url={\\$(.*?)}').findall(href)
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
                writeInfo(node,'[ZMSIndexZCatalog_func_] handleInline %s->%s'%(old,new))
                v = v.replace(old,new)
          return v

        def handleUrl(node,v):
          writeDebug(node,'[ZMSIndexZCatalog_func_] handleUrl %s'%v)
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
                  writeInfo(node,'[ZMSIndexZCatalog_func_] handleUrl %s->%s'%(old,new))
                  v = new
                  ref = getLinkObj('{$%s}'%brain['get_uid'])
                  ref.registerRefObj(node)
              else:
                writeError(node,'[ZMSIndexZCatalog_func_] handleUrl ### MISSING LINKTARGET %s'%(v))
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
          writeInfo(node,'[ZMSIndexZCatalog_func_] resync')
         
          try:
            if node.meta_id!='ZMSLinkElement' and node.getType()=='ZMSRecordSet':
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
            writeError(node,'[ZMSIndexZCatalog_func_] can\'t visit %s'%msg)

          # premature commit
          req_key = 'ZMSIndexZCatalog.resync.transaction_count'
          cfg_key = 'ZMSIndexZCatalog.resync.transaction_size'
          if request.get(req_key,0)>=int(self.getConfProperty(cfg_key,1000000)):
            writeInfo(node,'[ZMSIndexZCatalog_func_] +++ COMMIT +++')
            import transaction
            transaction.commit()
            request.set(req_key,0)
          request.set(req_key,request.get(req_key,0)+1)

          for childNode in node.objectValues(meta_types):
            count.extend(visit(childNode))

          return count

        def init_domains(doc,domains):
          domain = doc.getConfProperty('ASP.ip_or_domain','')
          if domain != '':
            domain = '^http(\\w)?://%s'%domain
            path = '/'.join(doc.getPhysicalPath())
            if domain in domains:
              writeError(doc,'[ZMSIndexZCatalog_func_] ### init_domains DUPLICATE %s=%s'%(domain,path))
            else:
              domains[domain] = path
              writeInfo(doc,'[ZMSIndexZCatalog_func_] init_domains %s=%s'%(domain,path))
          for portalClient in doc.getPortalClients():
            init_domains(portalClient,domains)
        if int(request.get('i',0)) == 0 or request.SESSION.get('ZMSIndexZCatalog_func_domains') is None:
          init_domains(zmsroot,domains)
          request.SESSION.set('ZMSIndexZCatalog_func_domains',domains)
        domains = request.SESSION.get('ZMSIndexZCatalog_func_domains')

        urls = [x for x in request['url'].split(',') if x]
        for url in urls:
          writeInfo(self,'[ZMSIndexZCatalog_func_] ### resync for %s'%url)
          t0 = time.time()
          base = self.getLinkObj(url)
          if base is not None:
            count = visit(base)
            writeInfo(self,'[ZMSIndexZCatalog_func_] resync for %s done: %i in %.2fsecs.'%(url,len(count),time.time()-t0))

  except:
    t,v,tb = sys.exc_info()
    msg = "[%s@%s]"%(self.meta_id,self.absolute_url())+''.join(format_exception(t, v, tb))
    writeError(self,'[ZMSIndexZCatalog_func_] except %s'%msg)

  response = getattr(request,'RESPONSE',None)
  if response is not None:
    response.setHeader('Content-Type','text/plain')
  return '\n'.join(printed)