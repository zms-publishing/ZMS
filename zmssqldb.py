################################################################################
# zmssqldb.py
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
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from types import StringTypes
import Globals
import copy
import os
import sys
import urllib
import tempfile
import time
import zExceptions
# Product Imports.
from zmsobject import ZMSObject
import _confmanager
import _fileutil
import _globals
import _objattrs
import _xmllib


################################################################################
################################################################################
###
###   Constructor
###
################################################################################
################################################################################
manage_addZMSSqlDbForm = PageTemplateFile('manage_addzmssqldbform', globals()) 
def manage_addZMSSqlDb(self, lang, _sort_id, REQUEST, RESPONSE):
  """ manage_addZMSSqlDb """
  
  ##### Create ####
  id_prefix = _globals.id_prefix(REQUEST.get('id_prefix','e'))
  new_id = self.getNewId(id_prefix)
  obj = ZMSSqlDb(new_id,_sort_id+1)
  self._setObject(obj.id, obj)
  
  obj = getattr(self,obj.id)
  ##### Object State ####
  obj.setObjStateNew(REQUEST)
  ##### Init Properties ####
  obj.manage_changeProperties(lang,REQUEST,RESPONSE)
  ##### VersionManager ####
  obj.onChangeObj(REQUEST)
  
  ##### Normalize Sort-IDs ####
  self.normalizeSortIds(id_prefix)
  
  # Return with message.
  if REQUEST.RESPONSE:
    message = self.getZMILangStr('MSG_INSERTED')%obj.display_type(REQUEST)
    REQUEST.RESPONSE.redirect('%s/%s/manage_main?lang=%s&manage_tabs_message=%s'%(self.absolute_url(),obj.id,lang,urllib.quote(message)))


################################################################################
################################################################################
###   
###   Class
###   
################################################################################
################################################################################

class ZMSSqlDb(ZMSObject):

    # Create a SecurityInfo for this class. We will use this
    # in the rest of our class definition to make security
    # assertions.
    security = ClassSecurityInfo()


    # Properties.
    # -----------
    meta_type = meta_id = "ZMSSqlDb"

    # Management Options.
    # -------------------
    manage_options = ( 
    {'label': 'TAB_EDIT',          'action': 'manage_main'},
    {'label': 'TAB_IMPORTEXPORT',  'action': 'manage_importexport'},
    {'label': 'TAB_PROPERTIES',    'action': 'manage_properties'},
    {'label': 'TAB_CONFIGURATION', 'action': 'manage_configuration'},
    {'label': 'SQL',               'action': 'manage_sql'},
    )

    # Management Permissions.
    # -----------------------
    __authorPermissions__ = (
        'manage','manage_main','manage_main_iframe','manage_workspace',
        'manage_moveObjUp','manage_moveObjDown','manage_moveObjToPos',
        'manage_cutObjects','manage_copyObjects','manage_pasteObjs',
        'manage_userForm', 'manage_user',
        'manage_importexport', 'manage_import', 'manage_export',
        'manage_zmi_input_form', 
        'manage_zmi_details_grid', 'manage_zmi_details_form',
        'manage_zmi_intersection_form',
        'manage_zmi_lazy_select_form',
        )
    __administratorPermissions__ = (
        'manage_properties','manage_changeProperties','manage_changeTempBlobjProperty',
        'manage_configuration', 'manage_changeConfiguration',
        'manage_sql', 
        )
    __ac_permissions__=(
        ('ZMS Author', __authorPermissions__),
        ('ZMS Administrator', __administratorPermissions__),
        )

    # Management Interface.
    # ---------------------
    manage_zmi_input_form = PageTemplateFile('zpt/ZMSSqlDb/input_form', globals())
    manage_zmi_details_grid = PageTemplateFile('zpt/ZMSSqlDb/zmi_details_grid', globals())
    manage_zmi_details_form = PageTemplateFile('zpt/ZMSSqlDb/zmi_details_form', globals())
    manage_zmi_intersection_form = PageTemplateFile('zpt/ZMSSqlDb/zmi_intersection_form', globals())
    manage_zmi_lazy_select_form = PageTemplateFile('zpt/ZMSSqlDb/zmi_lazy_select_form', globals())
    manage_main = PageTemplateFile('zpt/ZMSSqlDb/manage_main', globals())
    manage_importexport = PageTemplateFile('zpt/ZMSSqlDb/manage_importexport', globals())
    manage_properties = PageTemplateFile('zpt/ZMSSqlDb/manage_properties', globals())
    manage_sql = PageTemplateFile('zpt/ZMSSqlDb/manage_sql', globals())
    manage_configuration = PageTemplateFile('zpt/ZMSSqlDb/manage_configuration', globals())

    # Valid Types.
    # ------------
    valid_types = {
      'blob':{},
      'date':1,
      'datetime':1,
      'details':{},
      'fk':{},
      'html':1,
      'multiselect':{},
      'multimultiselect':{},
      'pk':1,
      'checkbox':1,
      'password':1,
      'richtext':1,
      'text':1,
      'time':1,
      'url':1,
    }


    ############################################################################
    ###
    ###   CONSTRUCTOR
    ###
    ############################################################################

    # --------------------------------------------------------------------------
    #  ZMSSqlDb.filteredChildNodes:
    # --------------------------------------------------------------------------
    def filteredChildNodes(self, REQUEST={}, meta_types=None): 
      return []


    # --------------------------------------------------------------------------
    #  ZMSSqlDb.getModelContainer:
    # --------------------------------------------------------------------------
    def getModelContainer( self):
      id = 'sqlmodel.xml'
      if id not in self.objectIds(['DTML Method']):
        model_xml =  getattr(self,'model_xml','<list>\n</list>')
        self.manage_addDTMLMethod( id, 'SQL-Model (XML)', model_xml)
      return getattr( self, id)


    # --------------------------------------------------------------------------
    #  ZMSSqlDb.getModel:
    # --------------------------------------------------------------------------
    def getModel(self):
      container = self.getModelContainer()
      container_xml = container.raw
      model_xml =  getattr(self,'model_xml',None)
      if model_xml is None:
        model_xml = '<list>\n</list>'
        self.model_xml = model_xml
        self.model = []
      if container_xml != model_xml:
        self.model_xml = container_xml
        self.model = self.parseXmlString(self.model_xml)
      return self.model


    # --------------------------------------------------------------------------
    #  ZMSSqlDb.setModel:
    # --------------------------------------------------------------------------
    def setModel(self, newModel):
      container = self.getModelContainer()
      container.manage_edit( title=container.title, data=newModel)


    # --------------------------------------------------------------------------
    #  ZMSSqlDb.record_encode__:
    # --------------------------------------------------------------------------
    def record_encode__(self, cols, record, encoding='utf-8'):
      charset = getattr(self,'charset','utf-8')
      row = {}
      for col in cols:
        k = col['id']
        v = record[k]
        if self.getConfProperty('ZMSSqlDb.record_encode__.k.lower'):
          k = k.lower()
        if v is not None and (type(v) is str or type(v) is unicode):
          try:
            v = unicode(v,charset).encode(encoding)
          except:
            row[k+'_exception'] = _globals.writeError( self, '[record_encode__]: can\'t %s'%k)
        row[k] = v
      return row


    # --------------------------------------------------------------------------
    #  ZMSSqlDb.getDA:
    #
    #  Return Database Adapter (DA).
    # --------------------------------------------------------------------------
    def getDA(self):
      da = None
      conn_id = getattr( self, "connection_id", None)
      if conn_id is not None:
        da = getattr(self,conn_id)
        if da.meta_type == 'Z MySQL Database Connection':
          # Try to re-connect if not connected.
          try: 
            dbc = da._v_database_connection 
          except AttributeError: 
            da.connect(da.connection_string) 
            dbc = da._v_database_connection
          # Try to set character-set to utf-8.
          try:
            dbc.query('SET NAMES utf8') 
            dbc.query('SET CHARACTER SET utf8')
          except:
            pass
      return da


    # --------------------------------------------------------------------------
    #  ZMSSqlDb.sql_quote__:
    # --------------------------------------------------------------------------
    def sql_quote__(self, tablename, columnname, v):
      da = self.getDA()
      gadfly = da.meta_type == 'Z Gadfly Database Connection'
      entities = self.getEntities()
      entity = filter(lambda x: x['id'].upper() == tablename.upper(), entities)[0]
      col = (filter(lambda x: x['id'].upper() == columnname.upper(), entity['columns'])+[{'type':'string'}])[0]
      if col.get('nullable') and v in ['',None]:
        if gadfly:
          return "''"
        else:
          return "NULL"
      elif col['type'] in ['int']:
        try:
          return str(int(str(v)))
        except:
          if gadfly:
            return "''"
          else:
            return "NULL"
      elif col['type'] in ['float']:
        try:
          return str(float(str(v)))
        except:
          if da.meta_type == 'Z Gadfly Database Connection':
            return "''"
          else:
            return "NULL"
      elif col['type'] in ['date','datetime','time']:
        try:
          d = self.parseLangFmtDate(v)
          if d is None:
            raise zExceptions.InternalError
          return "'%s'"%self.getLangFmtDate(d,'eng','%s_FMT'%col['type'].upper())
        except:
          if da.meta_type == 'Z Gadfly Database Connection':
            return "''"
          else:
            return "NULL"
      else:
        v = unicode(str(v),'utf-8').encode(getattr(self,'charset','utf-8'))
        if v.find("\'") >= 0: 
          v=''.join(v.split("\'"))
        return "'%s'"%v


    """
    Makes all changes made since the previous commit/rollback permanent and 
    releases any database locks currently held by the Connection object.
    """
    def commit(self):
      da = self.getDA()
      dbc = da._v_database_connection
      conn = dbc.getconn(False)
      conn.commit()


    """
    Undoes all changes made in the current transaction and releases any database
    locks currently held by this Connection object.
    """
    def rollback(self):
      da = self.getDA()
      dbc = da._v_database_connection
      conn = dbc.getconn(False)
      conn.rollback()


    """
    Execute sql-statement.
    Supports parameter-markers of mxODBCZopeDA.
    @param sql: The sql-statement
    @type sql: C{str}
    @param params: The values for the parameters.
    @type params: C{tuple}
    @param max_rows: The maximum number of rows (default: None, unlimited)
    @type max_rows: C{str}
    """
    def execute(self, sql, params=(), max_rows=None, encoding=None):
      da = self.getDA()
      dbc = da._v_database_connection
      result = dbc.execute(sql,params,max_rows)
      if encoding:
        result = self.assemble_query_result(result,encoding)
      return result


    """
    Assemble query-result.
    @return: Dictionary: columns C{list}, records C{list}.
    @rtype: C{dict}
    """
    def assemble_query_result(self, res, encoding=None):
      from cStringIO import StringIO
      from Shared.DC.ZRDB.Results import Results
      from Shared.DC.ZRDB import RDB
      if type(res) is str:
        f=StringIO()
        f.write(res)
        f.seek(0)
        result = RDB.File(f)
      else:
        result = Results(res)
      columns = []
      for result_column in result._searchable_result_columns():
        colName = result_column['name']
        colLabel = ''
        for s in colName.split('_'):
          colLabel += s.capitalize()
        try:
          colType = {'i':'int','n':'float','t':'string','s':'string','d':'datetime','l':'string'}[result_column['type']]
        except:
          colType = result_column.get('type',None)
          _globals.writeError(self,'[query]: Column ' + colName + ' has unknown type ' + str(colType) + '!')
        column = {}
        column['id'] = colName
        column['key'] = colName
        column['label'] = colLabel
        column['name'] = colLabel
        column['type'] = colType
        column['sort'] = 1
        columns.append(column)
      if encoding:
        result = map(lambda x: self.record_encode__(columns,x,encoding), result)
      return {'columns':columns,'records':result}


    """
    Execute select-statement.
    @param sql: The select-statement
    @type sql: C{str}
    @param max_rows: The maximum number of rows (default: None, unlimited)
    @type max_rows: C{str}
    @return: Dictionary: columns C{list}, records C{list}.
    @rtype: C{dict}
    """
    def query(self, sql, max_rows=None, encoding=None):
      if max_rows is None:
        max_rows = getattr(self,'max_rows',999)
      _globals.writeBlock( self, '[query]: sql=%s, max_rows=%i'%(sql,max_rows))
      da = self.getDA()
      dbc = da._v_database_connection
      if da.meta_type == 'Z SQLite Database Connection': sql = str(sql)
      return self.assemble_query_result(dbc.query(sql,max_rows),encoding)


    """
    Execute modify-statement.
    @param sql: The modify-statement
    @type sql: C{str}
    @return: Number of affected rows.
    @rtype: C{int}
    """
    def executeQuery(self, sql):
      from cStringIO import StringIO
      from Shared.DC.ZRDB.Results import Results
      from Shared.DC.ZRDB import RDB
      _globals.writeBlock( self, '[executeQuery]: sql=%s'%sql)
      da = self.getDA()
      dbc = da._v_database_connection
      res = dbc.query(sql)
      if type(res) is str:
        f=StringIO()
        f.write(res)
        f.seek(0)
        result=RDB.File(f)
      else:
        result=Results(res)
      return len(result)


    # --------------------------------------------------------------------------
    #  ZMSSqlDb.getEntityPK:
    #
    #  Returns primary key.
    # --------------------------------------------------------------------------
    def getEntityPK(self, tableName):
      columns = self.getEntity( tableName)['columns']
      # @todo
      pk = columns[0]['id']
      return pk


    # --------------------------------------------------------------------------
    #  ZMSSqlDb.getEntityRecordHandler
    # --------------------------------------------------------------------------
    def getEntityRecordHandler(self, tableName):
      class EntityRecordHandler:
        def __init__(self, parent, tableName):
          self.parent = parent 
          self.tableName = tableName
        __call____roles__ = None
        def __call__(self, r):
          d = {}
          for k in r.keys():
            column = self.parent.getEntityColumn(self.tableName,k,r)
            d[k] =  column.get('value',r[k])
          return d
      return EntityRecordHandler(self,tableName)


    # --------------------------------------------------------------------------
    #  ZMSSqlDb.getEntityColumn:
    # --------------------------------------------------------------------------
    def getEntityColumn(self, tableName, columnName, row=None):
      request = self.REQUEST
      lang = request.get('lang',self.getPrimaryLanguage())
      encoding = getattr(self,'charset','utf-8')
      qcharset = self.REQUEST.get('qcharset','utf-8')
      columns = self.getEntity( tableName)['columns']
      column = copy.deepcopy(filter(lambda x: x['id'].upper() == columnName.upper(), columns)[0])
      column['id'] = column['id'].lower()
      column['label'] = self.getLangStr(column['label'],lang)
      # Checkbox
      stereotype = column.get('checkbox')
      if stereotype not in ['',None]:
        column['type'] = 'boolean'
      # Blob
      stereotype = column.get('blob')
      if stereotype not in ['',None]:
        value = None
        column['type'] = stereotype['type']
        if row is not None:
          primary_key = self.getEntityPK(tableName)
          rowid = self.sql_quote__(tableName,primary_key,self.operator_getitem(row,primary_key,ignorecase=True))
          class BlobWrapper:
            def __init__(self, tableName, columnName, rowid, blob):
              self.tableName = tableName
              self.columnName = columnName
              self.rowid = rowid
              self.blob = blob
            getHref__roles__=None
            def getHref(self,request):
              return 'get_blob?tablename=%s&id=%s&rowid=%s'%(self.tableName,self.columnName,rowid)
            getContentType__roles__=None
            def getContentType(self):
              return self.blob.getContentType()
            getFilename__roles__ = None
            def getFilename(self):
              return self.blob.filename
            getWidth__roles__ = None
            def getWidth(self):
              return self.blob.getWidth()
            getHeight__roles__ = None
            def getHeight(self):
              return self.blob.getHeight()
            get_size__roles__ = None
            def get_size(self):
              return self.blob.get_size()
          blob = self._get_blob(tableName,columnName,rowid)
          if blob is not None:
            value = BlobWrapper(tableName,columnName,rowid,blob)
        column['value'] = value
      # Text
      stereotype = column.get('text')
      if stereotype not in ['',None]:
        column['type'] = 'text'
      # Richtext
      stereotype = column.get('richtext')
      if stereotype not in ['',None]:
        column['type'] = 'richtext'
      # Select
      stereotype = column.get('fk')
      if stereotype not in ['',None]:
        options = []
        # Select.MySQLSet
        if stereotype.has_key('mysqlset'):
          for r in self.query( 'DESCRIBE %s %s'%(tableName,columnName))['records']:
            rtype = r['type']
            for i in rtype[rtype.find('(')+1:rtype.rfind(')')].replace('\'','').split(','):
              options.append([i,i])
        # Select.Options
        elif stereotype.has_key('options'):
          options.extend(stereotype['options'])
        # Select.Fk
        elif stereotype.has_key('tablename'):
          sql = []
          sql.append( 'SELECT ' + stereotype['fieldname'] + ' AS qkey, ' + stereotype['displayfield'] + ' AS qvalue FROM ' + stereotype['tablename'])
          if stereotype.has_key('lazy') and row is not None:
            value = self.operator_getitem(row,columnName,ignorecase=True)
            where = ['1=0']
            if value:
              if type(value) is not list:
                value = [value]
              for i in value:
                where.append( stereotype['fieldname'] + '=' + self.sql_quote__(stereotype['tablename'],stereotype['fieldname'],i))
            sql.append( 'WHERE ' + ' OR '.join(where))
          sql.append( 'ORDER BY ' + str(stereotype.get('sort',2)))
          column['valuesql'] = '\n'.join(sql)
          for r in self.query('\n'.join(sql))['records']:
            qkey = str(r['qkey'])
            qvalue = str(r['qvalue'])
            try:
              qkey =unicode(qkey,qcharset).encode('utf-8')
              qvalue = unicode(qvalue,qcharset).encode('utf-8')
            except:
              pass
            options.append([qkey,qvalue])
        column['options'] = options
      
      # Multiselect
      stereotype = column.get('multiselect')
      if stereotype not in ['',None]:
        value = []
        options = []
        intersection = self.getEntity(stereotype['tablename'])
        intersection_fk = filter(lambda x:x.get('fk') is not None,intersection['columns'])
        src = filter(lambda x:x['fk'].has_key('tablename') and x['fk']['tablename'].upper()==tableName.upper(),intersection_fk)[0]
        dst = None
        if dst is None: dst = (filter(lambda x:x['fk'].has_key('options'),intersection_fk)+[None])[0]
        if dst is None: dst = (filter(lambda x:x['fk'].has_key('tablename') and x['fk']['tablename'].upper()!=tableName.upper(),intersection_fk)+[None])[0]
        # Multiselect.Selected
        if row is not None:
          primary_key = self.getEntityPK(tableName)
          sql = '' \
            + 'SELECT ' + dst['id'] + ' AS dst_id ' \
            + 'FROM ' + intersection['id'] + ' ' \
            + 'WHERE ' + src['id'] + '=' + self.sql_quote__(tableName,primary_key,self.operator_getitem(row,primary_key,ignorecase=True))
          column['valuesql'] = sql
          for r in self.query(sql)['records']:
            value.append(r['dst_id'])
        # Multiselect.MySQLSet
        if dst['fk'].has_key('mysqlset'):
          for r in self.query( 'DESCRIBE %s %s'%(intersection['id'],dst['fk']['id']))['records']:
            rtype = r['type']
            for i in rtype[rtype.find('(')+1:rtype.rfind(')')].replace('\'','').split(','):
              options.append([i,i])
        # Multiselect.Options
        elif dst['fk'].has_key('options'):
          options.extend(dst['fk']['options'])
        # Multiselect.Fk
        elif dst['fk'].has_key('tablename'):
          sql = []
          sql.append('SELECT ' + dst['fk']['fieldname'] + ' AS qkey, ' + dst['fk']['displayfield'] + ' AS qvalue')
          sql.append('FROM ' + dst['fk']['tablename'])
          if stereotype.has_key('lazy') and row is not None:
            where = ['1=0']
            if value:
              if type(value) is not list:
                value = [value]
              for i in value:
                where.append( dst['fk']['fieldname'] + '=' + self.sql_quote__(dst['fk']['tablename'],dst['fk']['fieldname'],i))
            sql.append( 'WHERE ' + ' OR '.join(where))
          column['valuesql'] = '\n'.join(sql)
          for r in self.query('\n'.join(sql))['records']:
            qkey = str(r['qkey'])
            qvalue = str(r['qvalue'])
            try:
              qkey =unicode(qkey,qcharset).encode('utf-8')
              qvalue = unicode(qvalue,qcharset).encode('utf-8')
            except:
              pass
            options.append([qkey,qvalue])
        column['src'] = src
        column['dst'] = dst
        column['value'] = value
        column['options'] = options
      
      # Details
      stereotype = column.get('details')
      if stereotype not in ['',None]:
        details = self.getEntity(stereotype['tablename'])
        # Details.Intersection
        if details['type']=='intersection':
          if row:
            primary_key = self.getEntityPK(tableName)
            dst = filter(lambda x:x.get('fk') is not None and x['fk'].has_key('tablename') and x['fk']['tablename']!=tableName,details['columns'])[0]
            dstentity = self.getEntity(dst['fk']['tablename'])
            sql = '' \
              + 'SELECT a.* ' \
              + 'FROM ' + dstentity['id'] + ' a ' \
              + 'INNER JOIN ' + stereotype['tablename'] + ' b ON a.' + filter(lambda x:x.get('pk'),dstentity['columns'])[0]['id'] + ' = b.' + dst['id'] + ' ' \
              + 'WHERE b.' + stereotype['fk'] + '=' + self.sql_quote__(tableName,primary_key,self.operator_getitem(row,primary_key,ignorecase=True)) 
            column['valuesql'] = sql
            records = self.query(sql,encoding=encoding)['records']
            column['value'] = records
            column['dst'] = dstentity
        # Details.Table
        else:
          if row:
            primary_key = self.getEntityPK(tableName)
            sql = '' \
              + 'SELECT b.* ' \
              + 'FROM ' + stereotype['tablename'] + ' b ' \
              + 'WHERE b.' + stereotype['fk'] + '=' + self.sql_quote__(tableName,primary_key,self.operator_getitem(row,primary_key,ignorecase=True))
            column['valuesql'] = sql
            records = self.query(sql,encoding=encoding)['records']
            column['value'] = records
      
      # Multimultiselect
      stereotype = column.get('multimultiselect')
      if stereotype not in ['',None]:
        items = stereotype.get('tables',[])
        for item in items:
          if item.get('lazy'):
            pass
          else:
            options = []
            sql = '' \
              + 'SELECT ' + item['fieldname'] + ' AS qkey, ' + item['displayfield'] + ' AS qvalue ' \
              + 'FROM ' + item['tablename'] + ' ' \
              + 'ORDER BY ' + item['displayfield']
            for r in self.query(sql)['records']:
              qkey = str(r['qkey'])
              qvalue = str(r['qvalue'])
              try:
                qkey =unicode(qkey,qcharset).encode('utf-8')
                qvalue = unicode(qvalue,qcharset).encode('utf-8')
              except:
                pass
              options.append([qkey,qvalue])
            stereotype['options'] = stereotype.get('options',{})
            stereotype['options'][item['tablename']] = options
        value = []
        if row:
          primary_key = self.getEntityPK(tableName)
          columns  = []
          leftjoins = []
          outerjoins = []
          for item in items:
            i = items.index(item)
            if item['fieldname'].find(item['tablename']+'.') < 0:
              item['fieldname'] = item['tablename']+'.'+item['fieldname'] 
            columns.append(item['fieldname']+' AS fk%i'%i)
            if item['displayfield'].find(item['tablename']+'.') < 0:
              item['displayfield'] = item['tablename']+'.'+item['displayfield'] 
            columns.append(item['displayfield']+' AS displayfield%i'%i)
            join = item['tablename']+' ON '+stereotype['tablename']+'.'+item['fk']+'='+item['fieldname']
            if item.get('nullable'):
              outerjoins.append(join)
            else:
              leftjoins.append(join)
          sql = []
          sql.append('SELECT '+', '.join(columns))
          sql.append(' FROM '+stereotype['tablename'])
          if leftjoins:
            sql.append(' LEFT JOIN '.join(['']+leftjoins))
          if outerjoins:
            sql.append(' LEFT OUTER JOIN '.join(['']+outerjoins))
          sql.append(' WHERE ' + stereotype['tablename'] + '.' + stereotype['fk'] + '=' + self.sql_quote__(tableName,primary_key,self.operator_getitem(row,primary_key,ignorecase=True)))
          column['valuesql'] = '\n'.join(sql)
          for r in self.query('\n'.join(sql))['records']:
            v = []
            l = []
            for item in items:
              i = items.index(item)
              qkey = ''
              qvalue = ''
              if r['fk%i'%i]:
                qkey = str(r['fk%i'%i])
                qvalue = str(r['displayfield%i'%i])
                try:
                  qkey =unicode(qkey,qcharset).encode('utf-8')
                  qvalue = unicode(qvalue,qcharset).encode('utf-8')
                except:
                  pass
              v.append(qkey)
              l.append(qvalue)
            value.append(('|'.join(v),' | '.join(l)))
        column['value']= value
      
      return column


    # --------------------------------------------------------------------------
    #  ZMSSqlDb.getEntity:
    # --------------------------------------------------------------------------
    def getEntity(self, tableName):
      entities = self.getEntities()
      return filter(lambda x: x['id'].upper() == tableName.upper(), entities)[0]


    # --------------------------------------------------------------------------
    #  ZMSSqlDb.getEntities:
    # --------------------------------------------------------------------------
    def getEntities(self):

      #-- [ReqBuff]: Fetch buffered value from Http-Request.
      REQUEST = self.REQUEST
      reqBuffId = 'getEntities'
      try:
        return self.fetchReqBuff( reqBuffId, REQUEST, True)
      except:
        pass
      
      entities = []
      da = self.getDA()
      if da is None: return entities
      
      tableBrwsrs = da.tpValues()
      
      # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
      # +- ENTITES
      # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
      
      #-- for custom entities please refer to $ZMS_HOME/conf/db/getEntities.Oracle.dtml
      method = getattr(self,'getEntities%s'%self.connection_id,None)
      if method is not None:
        entities = method( self, REQUEST)
      
      #-- retrieve entities from table-browsers
      if len( entities) == 0:
        for tableBrwsr in tableBrwsrs:
          tableName = str(getattr(tableBrwsr,'Name',getattr(tableBrwsr,'name',None))())
          tableType = str(getattr(tableBrwsr,'Type',getattr(tableBrwsr,'type',None))())
          if tableType.upper() == 'TABLE':
            # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
            # +- COLUMNS
            # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
            cols = []
            try:
              columnBrwsrs = []
              if da.meta_type == 'Z SQLite Database Connection':
                for columnBrwsr in tableBrwsr.tpValues():
                  desc = getattr(columnBrwsr,'Description',getattr(columnBrwsr,'description',None))().upper()
                  desc = desc[desc.find("(")+1:desc.rfind(")")]
                  for cc in desc.split(","):
                    c = ''
                    for l in cc.split("\n"):
                      if l.find('--') >= 0:
                        l = l[:l.find('--')]
                      l = l.strip()
                      if len(l) > 0:
                        c += l + ' '
                    cl = filter(lambda x: len(x.strip()) > 0, c.split(' '))
                    if len(cl) >= 2:
                      cid = cl[0]
                      if cid.startswith('"') and cid.endswith('"'):
                        cid = cid[1:-1]
                      ucid = cid.upper() 
                      uctype = cl[1].upper()
                      if not ucid in ['CHECK','FOREIGN','PRIMARY'] and not uctype.startswith('KEY') and not uctype.startswith('(') and not ucid.startswith('\''):
                        col = {}
                        col["id"] = cid
                        col["description"] = ' '.join(cl[1:])
                        columnBrwsrs.append(col)
              else:
                for columnBrwsr in tableBrwsr.tpValues():
                  col = {}
                  col["id"] = columnBrwsr.tpId()
                  col["description"] = getattr(columnBrwsr,'Description',getattr(columnBrwsr,'description',None))().upper()
                  columnBrwsrs.append(col)
              for columnBrwsr in columnBrwsrs:
                colId = columnBrwsr["id"]
                colDescr = columnBrwsr["description"]
                colType = 'string'
                colSize = None
                if colDescr.find('INT') >= 0:
                  colType = 'int'
                elif colDescr.find('DATE') >= 0 or \
                     colDescr.find('TIME') >= 0:
                  colType = 'datetime'
                elif colDescr.find('CLOB') >= 0:
                  colType = 'text'
                elif colDescr.find('CHAR') >= 0 or \
                     colDescr.find('STRING') >= 0:
                  colSize = 255
                  i = colDescr.find('(')
                  if i >= 0:
                    j = colDescr.find(')')
                    if j >= 0:
                      colSize = int(colDescr[i+1:j])
                  if colSize > 255:
                    colType = 'text'
                  else:
                    colType = 'string'
                colId = unicode(colId).encode('utf-8')
                col = {}
                col['key'] = colId
                col['description'] = colDescr.strip()
                col['id'] = col['key']
                col['index'] = int(col.get('index',len(cols)))
                col['label'] = ' '.join( map( lambda x: x.capitalize(), colId.split('_'))).strip()
                col['name'] = col['label']
                col['mandatory'] = colDescr.find('NOT NULL') > 0 or da.meta_type == 'Z Gadfly Database Connection'
                col['type'] = colType
                col['sort'] = 1
                col['nullable'] = not col['mandatory']
                # Add Column.
                cols.append(col)
            except:
              _globals.writeError(self,'[getEntities]')
            # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
            # +- TABLE
            # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
            if len(cols) > 0:
              entity = {}
              entity['id'] = tableName
              entity['type'] = 'table'
              entity['label'] = ' '.join( map( lambda x: x.capitalize(), tableName.split('_'))).strip()
              entity['sort_id'] = entity['label'].upper()
              entity['columns'] = self.sort_list(cols,'index')
              # Add Table.
              entities.append(entity)
      
      #-- Custom properties
      model = self.getModel()
      s = []
      for entity in entities:
        tableName = entity['id']
        tableInterface = entity.get('interface','')
        cols = []
        colNames = []
        for col in entity['columns']:
          colName = col['id'].upper()
          # Set custom column-properties
          for modelTable in filter(lambda x: x['id'].upper() == tableName.upper(), model):
            for modelTableCol in filter(lambda x: x['id'].upper() == colName, modelTable.get('columns',[])):
              for modelTableColProp in filter(lambda x: x not in ['id'], modelTableCol.keys()):
                col[modelTableColProp] = modelTableCol[modelTableColProp]
          cols.append(col)
          colNames.append(colName)
        # Add custom columns
        for modelTable in filter(lambda x: x['id'].upper() == tableName.upper(), model):
          tableInterface = modelTable.get('interface',tableInterface)
          for modelTableCol in filter(lambda x: x['id'].upper() not in colNames, modelTable.get('columns',[])):
            col = modelTableCol
            col['id'] = col.get('id','?')
            col['index'] = int(col.get('index',len(cols)))
            col['type'] = col.get('type','?')
            col['key'] = col.get('key',col.get('id'))
            col['label'] = col.get('label',col.get('id'))
            col['stereotypes'] = self.intersection_list( self.valid_types.keys(), col.keys())
            col['not_found'] = col.get('description') is None and len(col.get('stereotypes',[]))==0
            cols.insert(col['index'], col)
            colNames.append(col['id'].upper())
        entity['interface'] = tableInterface
        entity['columns'] = self.sort_list(cols,'index')
        # Set custom table-properties
        for modelTable in filter(lambda x: x['id'].upper() ==tableName.upper(), model):
          for modelTableProp in filter(lambda x: x not in ['columns'], modelTable.keys()):
            entity[modelTableProp] = modelTable[modelTableProp]
            entity['sort_id'] = entity['label'].upper()
        # Add
        s.append((entity['label'],entity))
      
      #-- Custom entities.
      for entity in model:
        tableName = entity['id']
        if entity.has_key('not_found'):
          del entity['not_found']
        if tableName.upper() not in map( lambda x: x['id'].upper(), entities):
          cols = entity.get('columns',[])
          entity['id'] = tableName
          entity['type'] = entity.get('type','table')
          entity['label'] = entity.get('label',' '.join( map( lambda x: x.capitalize(), tableName.split('_'))).strip())
          entity['sort_id'] = entity['label'].upper()
          entity['columns'] = self.sort_list(cols,'index')
          # Add Table.
          entity['not_found'] = 1
          s.append((entity['label'],entity))
      
      #-- Sort entities
      s.sort()
      entities = map(lambda x: x[1], s)
      
      #-- Defaults
      for entity in entities:
        for column in entity['columns']:
          #column['id'] = column['id'].lower()
          column['multilang'] = False
          column['datatype'] = column.get('type','?')
          column['datatype_key'] = _globals.datatype_key(column['datatype'])
      
      #-- [ReqBuff]: Returns value and stores it in buffer of Http-Request.
      return self.storeReqBuff( reqBuffId, entities, REQUEST)


    ############################################################################
    ###
    ###   RecordSet
    ###
    ############################################################################

    """
    @rtype: C{string}
    """
    def recordSet_Select(self, tablename, select=None, where=None):
      da = self.getDA()
      gadfly = da.meta_type == 'Z Gadfly Database Connection'
      tabledef = self.getEntity(tablename)
      tablecols = tabledef['columns']
      selectClause = []
      fromClause = [ tablename]
      whereClause = []
      if where:
        whereClause.append( where)
      if select:
        selectClause.append( select)
      else:
        fk_tablename_counter = {}
        table_AS = self.getConfProperty('ZMSSqlDb.table.AS','AS')
        for tablecol in tablecols:
          if tablecol.get('fk') and tablecol['fk'].get('tablename'):
            fk_tablename = tablecol['fk']['tablename']
            fk_tablename_counter[fk_tablename] = fk_tablename_counter.get(fk_tablename,0)+1
            fk_tablename_alias = '%s%i'%(fk_tablename,fk_tablename_counter[fk_tablename])
            fk_fieldname = tablecol['fk']['fieldname']
            if fk_fieldname.upper().find(fk_tablename.upper()+'.') < 0:
              fk_fieldname = fk_tablename+'.'+fk_fieldname
            fk_fieldname = self.re_sub( fk_tablename+'\.', fk_tablename_alias+'.', fk_fieldname, ignorecase=True)
            fk_displayfield = tablecol['fk']['displayfield']
            if fk_displayfield.upper().find(fk_tablename.upper()+'.') < 0:
              fk_displayfield = fk_tablename+'.'+fk_displayfield
            fk_displayfield = self.re_sub( fk_tablename+'\.', fk_tablename_alias+'.', fk_displayfield, ignorecase=True)
            selectClause.append( '%s AS %s'%(fk_displayfield,tablecol['id']))
            if gadfly:
              fromClause.append( ', %s %s %s'%(fk_tablename,table_AS,fk_tablename_alias))
              whereClause.append( '%s.%s=%s'%(tablename,tablecol['id'],fk_fieldname))
            else:
              fromClause.append( 'LEFT JOIN %s %s %s ON %s.%s=%s'%(fk_tablename,table_AS,fk_tablename_alias,tablename,tablecol['id'],fk_fieldname))
          elif tablecol.get('type','?') != '?':
            selectClause.append( '%s.%s'%(tablename,tablecol['id']))
      sqlStatement = []
      sqlStatement.append( 'SELECT '+' , '.join(selectClause)+' ')
      sqlStatement.append( 'FROM '+' '.join(fromClause)+' ')
      if whereClause:
        sqlStatement.append( 'WHERE '+' AND '.join(whereClause)+' ')
      return ''.join(sqlStatement)


    """
    Initializes record-set.
    @param REQUEST: the triggering request
    @type REQUEST: ZPublisher.HTTPRequest
    @rtype: C{None}
    """
    def recordSet_Init(self, REQUEST, all=True):
      SESSION = REQUEST.SESSION
      tabledefs = filter( lambda x: not x.get('not_found'), self.getEntities())
      tablename = SESSION.get('qentity_%s'%self.id)
      #-- Sanity check.
      SESSION.set('qentity_%s'%self.id,'')
      REQUEST.set('primary_key','')
      REQUEST.set('grid_cols',[])
      sqlStatement = REQUEST.get('sqlStatement',[])
      if type(sqlStatement) is not list:
        sqlStatement = []
      if len(tabledefs) > 0:
        if tablename not in map( lambda x: x['id'], tabledefs):
          tablename = tabledefs[0]['id']
        tablename = REQUEST.form.get('qentity',tablename)
        tabledef = filter(lambda x: x['id'].upper() == tablename.upper(), tabledefs)[0]
        select = None
        if all: 
          select = '*'
        sqlStatement.append( self.recordSet_Select( tablename, select))
        tablecols = tabledef['columns']
        # Primary Key.
        primary_key = map(lambda x: x['id'], filter(lambda x: x.get('pk',0)==1, tablecols))
        primary_key.append(None)
        #-- Set environment.
        SESSION.set('qentity_%s'%self.id,tablename)
        REQUEST.set('qentity',tablename)
        REQUEST.set('tabledef',tabledef)
        REQUEST.set('grid_cols',tablecols)
        REQUEST.set('primary_key',primary_key[0])
      REQUEST.set('sqlStatement',sqlStatement)


    """
    Filter record-set by appending where clause to sql-statement.
    @param REQUEST: the triggering request
    @type REQUEST: ZPublisher.HTTPRequest
    @rtype: C{None}
    """
    def recordSet_Filter(self, REQUEST):
      SESSION = REQUEST.SESSION
      tablename = SESSION['qentity_%s'%self.id]
      tabledefs = filter( lambda x: not x.get('not_found'), self.getEntities())
      #-- Sanity check.
      SESSION.set('qfilters_%s'%self.id,REQUEST.form.get('qfilters',SESSION.get('qfilters_%s'%self.id,1)))
      if len(tabledefs) > 0:
        tabledef = filter(lambda x: x['id'].upper() == tablename.upper(), tabledefs)[0]
        tablecols = tabledef['columns']
        tablefilter = self.dt_exec(tabledef.get('filter',''))
        #-- WHERE
        q = 'WHERE '
        if ''.join(REQUEST.get('sqlStatement',[])).upper().find(q) > 0:
          q = 'AND '
        whereClause = []
        for i in range(SESSION['qfilters_%s'%self.id]):
          filterattr='filterattr%i'%i
          filterop='filterop%i'%i
          filtervalue='filtervalue%i'%i
          sessionattr='%s_%s'%(filterattr,self.id)
          sessionop='%s_%s'%(filterop,self.id)
          sessionvalue='%s_%s'%(filtervalue,self.id)
          if REQUEST.get('action','')=='':
            if REQUEST.get('btn','')==self.getZMILangStr('BTN_RESET'):
              SESSION.set(sessionattr,'')
              SESSION.set(sessionop,'')
              SESSION.set(sessionvalue,'')
            elif REQUEST.get('btn','')==self.getZMILangStr('BTN_REFRESH'):
              SESSION.set(sessionattr,REQUEST.form.get(filterattr,''))
              SESSION.set(sessionop,REQUEST.form.get(filterop,''))
              SESSION.set(sessionvalue,REQUEST.form.get(filtervalue,''))
          fk_tablename_counter = {}
          for tablecol in tablecols:
            if tablecol.get('fk') and tablecol['fk'].get('tablename'):
              fk_tablename = tablecol['fk']['tablename']
              fk_tablename_counter[fk_tablename] = fk_tablename_counter.get(fk_tablename,0)+1
              fk_tablename_alias = '%s%i'%(fk_tablename,fk_tablename_counter[fk_tablename])
              fk_displayfield = tablecol['fk']['displayfield']
              if fk_displayfield.find(fk_tablename+'.') < 0:
                fk_displayfield = fk_tablename+'.'+fk_displayfield
              coltable = fk_tablename
              colname = self.re_sub( fk_tablename+'\.', fk_tablename_alias+'.', fk_displayfield, ignorecase=True)
              qualifiedname = colname
            else:
              coltable = tablename
              colname = tablecol['id']
              qualifiedname = '%s.%s'%(coltable,colname)
            v = SESSION.get(sessionvalue,'')
            op = SESSION.get(sessionop,'=')
            if SESSION.get(sessionattr,'') == tablecol['id']:
              sqlStatement = REQUEST.get('sqlStatement',[])
              if op in [ 'NULL', 'NOT NULL']:
                sqlStatement.append(q + qualifiedname + ' IS ' + op + ' ')
              elif v != '':
                sqlStatement.append(q + qualifiedname + ' ' + op + ' ' + self.sql_quote__(coltable, colname, v) + ' ')
              REQUEST.set('sqlStatement',sqlStatement)
              q = 'AND '
        if len(tablefilter) > 0:
          sqlStatement = REQUEST.get('sqlStatement',[])
          sqlStatement.append(q + '(' + tablefilter + ') ')
          REQUEST.set('sqlStatement',sqlStatement)


    """
    Sort record-set by appending order-by clause to sql-statement.
    @param REQUEST: the triggering request
    @type REQUEST: ZPublisher.HTTPRequest
    @rtype: C{None}
    """
    def recordSet_Sort(self, REQUEST):
      SESSION = REQUEST.SESSION
      tablename = SESSION['qentity_%s'%self.id]
      tabledefs = filter( lambda x: not x.get('not_found'), self.getEntities())
      #-- Sanity check.
      qorder = REQUEST.get('qorder','')
      qorderdir = REQUEST.get('qorderdir','asc')
      sqlStatement = REQUEST.get('sqlStatement',[])
      if len(tabledefs) > 0:
        tabledef = filter(lambda x: x['id'].upper() == tablename.upper(), tabledefs)[0]
        tablecols = tabledef['columns']
        #-- ORDER BY
        if qorder == '' or not qorder in map(lambda x: x['id'], tablecols):
          for col in tablecols:
            if col.get('hide',0) != 1:
              qorder = '%s.%s'%(tablename,col['id'])
              if col.get('type','') in ['date','datetime','time']:
                qorderdir = 'desc'
              break
        if qorder:
          sqlStatement.append('ORDER BY ' + qorder + ' ' + qorderdir + ' ')
      REQUEST.set('sqlStatement',sqlStatement)
      REQUEST.set('qorder',qorder)
      REQUEST.set('qorderdir',qorderdir)


    ############################################################################
    ###
    ###   Actions
    ###
    ############################################################################


    """
    Get reference for foreign-key relation.
    @param tablename: Name of the SQL-Table.
    @type tablename: C{string}
    @return: ID of the row that was inserted.
    @rtype: int
    """
    def getFk(self, tablename, id, name, value, createIfNotExists=1):
      tabledefs = self.getEntities()
      tabledef = filter(lambda x: x['id'].upper() == tablename.upper(), tabledefs)[0]
      tablecols = tabledef['columns']
      primary_key = (map(lambda x: x['id'], filter(lambda x: x.get('pk',0)==1, tablecols))+[tablecols[0]['id']])[0]
      
      # Find existing row-id.
      sqlStatement = []
      sqlStatement.append( 'SELECT %s AS existing_id FROM %s'%(primary_key,tablename))
      sqlStatement.append( 'WHERE %s=%s'%(primary_key,self.sql_quote__(tablename, primary_key, value)))
      sqlStatement.append( 'OR %s=%s'%(name,self.sql_quote__(tablename, name, value)))
      sqlStatement = ' '.join(sqlStatement)
      try:
        rs = self.query(sqlStatement)['records']
        if len(rs) == 1:
          rowid = rs[0]['existing_id']
          return rowid
      except:
        raise zExceptions.InternalError(_globals.writeError( self, '[getFk]: can\'t find existing row - sqlStatement=' + sqlStatement))
      
      rowid = None
      if createIfNotExists:
        # Get columns to insert
        c = []
        tablecol = tablecols[0]
        if tablecol.get('auto'):
          new_id = 0
          try:
            rs = self.query('SELECT MAX(%s) AS max_id FROM %s'%(primary_key,tablename))['records']
            if len(rs) == 1:
              new_id = int(rs[0]['max_id'])+1
          except:
            _globals.writeError( self, '[getFk]: can\'t get max_id')
          c.append({'id':id,'value':str(new_id)})
        c.append({'id':name,'value':self.sql_quote__(tablename,name,value)})
        
        # Assemble sql-statement
        sqlStatement = []
        sqlStatement.append( 'INSERT INTO %s ('%tablename)
        sqlStatement.append( ', '.join(map(lambda x: x['id'], c)))
        sqlStatement.append( ') VALUES (')
        sqlStatement.append( ', '.join(map(lambda x: x['value'], c)))
        sqlStatement.append( ')')
        sqlStatement = ' '.join(sqlStatement)
        try:
          self.executeQuery( sqlStatement)
        except:
          raise zExceptions.InternalError(_globals.writeError( self, '[createFk]: can\'t insert row - sqlStatement=' + sqlStatement))
        
        # Return with row-id.
        rowid = (filter(lambda x: x['id']==primary_key, c)+[{'value':None}])[0]['value']
        if rowid is None:
          sqlStatement = []
          sqlStatement.append( 'SELECT %s AS value FROM %s WHERE '%(primary_key,tablename))
          sqlStatement.append( ' AND '.join(map( lambda x: x['id']+'='+x['value'], filter( lambda x: x['value'].upper()!='NULL', c))))
          sqlStatement = ' '.join(sqlStatement)
          try:
            for r in self.query( sqlStatement)['records']:
              rowid = r['value']
          except:
            raise zExceptions.InternalError(_globals.writeError( self, '[createFk]: can\'t get primary-key - sqlStatement=' + sqlStatement))
      
      return rowid


    """
    Insert row into record-set.
    @param tablename: Name of the SQL-Table.
    @type tablename: C{string}
    @param values: Columns (id/value) to be inserted.
    @type values: C{dict}
    @return: ID of the row that was inserted.
    @rtype: C{any}
    """
    def recordSet_Insert(self, tablename, values={}):
      REQUEST = self.REQUEST
      auth_user = REQUEST.get('AUTHENTICATED_USER')
      lang = REQUEST['lang']
      da = self.getDA()
      if tablename is None:
        raise zExceptions.InternalError("[recordSet_Insert]: tablename must not be None!")
      tabledefs = self.getEntities()
      tabledef = filter(lambda x: x['id'].upper() == tablename.upper(), tabledefs)[0]
      tablecols = tabledef['columns']
      primary_key = (map(lambda x: x['id'], filter(lambda x: x.get('pk',0)==1, tablecols))+[tablecols[0]['id']])[0]
      
      # Get columns to insert
      blobs = {}
      c = []
      for tablecol in tablecols:
        id = tablecol['id']
        if tablecol.get('auto'):
          if tablecol.get('auto') in ['insert','update']:
            if tablecol.get('type') in ['date','datetime']:
              c.append({'id':id,'value':self.getLangFmtDate(time.time(),lang,'%s_FMT'%tablecol['type'].upper())})
            elif tablecol.get('type') in ['int']:
              new_id = 0
              try:
                rs = self.query('SELECT MAX(%s) AS max_id FROM %s'%(id,tablename))['records']
                if len(rs) == 1:
                  new_id = int(rs[0]['max_id'])+1
              except:
                _globals.writeError( self, '[recordSet_Insert]: can\'t get max_id')
              c.append({'id':id,'value':new_id})
        elif tablecol.get('blob'):
          value = None
          blob = tablecol.get('blob')
          if values.get('blob_%s'%id,None) is not None and values.get('blob_%s'%id).filename:
            # Process blobs later...
            blobs['blob_%s'%id] = values['blob_%s'%id]
        elif (not tablecol.get('details')) and \
             (not tablecol.get('multiselect') or tablecol.get('multiselect').get('custom') or tablecol.get('multiselect').get('mysqlset')) and \
             (not tablecol.get('multimultiselect')):
          value = values.get(id,values.get(id.lower(),values.get(id.upper(),'')))
          if type(value) is list:
            value = ','.join(value)
          c.append({'id':id,'value':value})
      # Assemble sql-statement
      c = filter(lambda x: self.sql_quote__(tablename,x['id'],x['value'])!='NULL', c)
      sqlStatement = []
      sqlStatement.append( 'INSERT INTO %s ('%tablename)
      sqlStatement.append( ', '.join(map(lambda x: x['id'], c)))
      sqlStatement.append( ') VALUES (')
      sqlStatement.append( ', '.join(map(lambda x: self.sql_quote__(tablename,x['id'],x['value']), c)))
      sqlStatement.append( ')')
      sqlStatement = ' '.join(sqlStatement)
      try:
        if da.meta_type == 'Z MySQL Database Connection':
          self.executeQuery('SET @auth_user=\'%s\''%auth_user)
      except:
        raise zExceptions.InternalError(_globals.writeError( self, '[recordSet_Insert]: can\'t set auth_user variable'))
      try:
        self.executeQuery( sqlStatement)
      except:
        raise zExceptions.InternalError(_globals.writeError( self, '[recordSet_Insert]: can\'t insert row - sqlStatement=' + sqlStatement))
      # Return with row-id.
      rowid = (filter(lambda x: x['id']==primary_key, c)+[{'value':None}])[0]['value']
      if rowid is None:
        sqlStatement = []
        sqlStatement.append( 'SELECT %s AS value FROM %s WHERE '%(primary_key,tablename))
        sqlStatement.append( ' AND '.join(map( lambda x: x['id']+'='+self.sql_quote__(tablename,x['id'],x['value']), filter( lambda x: self.sql_quote__(tablename,x['id'],x['value']).upper()!='NULL', c))))
        sqlStatement = ' '.join(sqlStatement)
        try:
          for r in self.query( sqlStatement)['records']:
            rowid = r['value']
        except:
          raise zExceptions.InternalError(_globals.writeError( self, '[recordSet_Insert]: can\'t get primary-key - sqlStatement=' + sqlStatement))
      # Update intersections.
      self.recordSet_UpdateIntersections(tablename, rowid, values)
      # Process blobs now.
      if blobs:
        self.recordSet_Update(tablename, rowid, blobs)
      return rowid


    """
    Update row in table.
    @param tablename: Name of the SQL-Table.
    @type tablename: C{string}
    @param rowid: ID of the row to be updated.
    @type rowid: C{any}
    @param values: Columns (id/value) to be updated.
    @type values: C{dict}
    @return: ID of the row that was updated.
    @rtype: C{any}
    """
    def recordSet_Update(self, tablename, rowid, values={}, old_values={}):
      REQUEST = self.REQUEST
      auth_user = REQUEST.get('AUTHENTICATED_USER')
      lang = REQUEST['lang']
      da = self.getDA()
      if tablename is None:
        raise "[recordSet_Update]: tablename must not be None!"
      tabledefs = self.getEntities()
      tabledef = filter(lambda x: x['id'].upper() == tablename.upper(), tabledefs)[0]
      tablecols = tabledef['columns']
      primary_key = (map(lambda x: x['id'], filter(lambda x: x.get('pk',0)==1, tablecols))+[tablecols[0]['id']])[0]
      # Get old.
      sqlStatement = []
      sqlStatement.append( 'SELECT * FROM %s '%tablename)
      sqlStatement.append( 'WHERE %s=%s '%(primary_key,self.sql_quote__(tablename,primary_key,rowid)))
      sqlStatement = ' '.join(sqlStatement)
      try:
        old = self.query( sqlStatement)['records'][0]
      except:
        raise zExceptions.InternalError(_globals.writeError( self, '[recordSet_Update]: can\'t get old - sqlStatement=' + sqlStatement))
      # Get columns to update
      c = []
      for tablecol in tablecols:
        id = tablecol['id']
        consumed = id in REQUEST.get('qexcludeids',[])
        if not consumed and tablecol.get('auto'):
          if tablecol.get('auto') in ['update']:
            if tablecol.get('type') in ['date','datetime']:
              c.append({'id':id,'value':self.getLangFmtDate(time.time(),lang,'%s_FMT'%tablecol['type'].upper())})
          consumed = True
        if not consumed and tablecol.get('blob'):
          blob = tablecol.get('blob')
          remote = blob.get('remote',None)
          if values.get('delete_blob_%s'%id,None):
            if remote is None:
              value = self._delete_blob(tablename=tablename,id=id,rowid=rowid)
            else:
              value = self.http_import(self.url_append_params(remote+'/delete_blob',{'auth_user':blob.get('auth_user',auth_user.getId()),'tablename':tablename,'id':id,'rowid':rowid}),method='POST')
            c.append({'id':id,'value':value})
          elif values.get('blob_%s'%id,None) is not None and values.get('blob_%s'%id).filename:
            data = values.get('blob_%s'%id,None)
            file = self.FileFromData( data, data.filename)
            if remote is None:
              value = self._set_blob(tablename=tablename,id=id,rowid=rowid,file=file)
            else:
              xml = file.toXml()
              value = self.http_import(self.url_append_params(remote+'/set_blob',{'auth_user':blob.get('auth_user',auth_user.getId()),'tablename':tablename,'id':id,'rowid':rowid,'xml':xml}),method='POST')
            c.append({'id':id,'value':value})
          consumed = True
        if not consumed and tablecol.get('fk') and tablecol.get('fk').get('editable'):
          if values.has_key(id):
            fk_tablename = tablecol.get('fk').get('tablename')
            fk_fieldname = tablecol.get('fk').get('fieldname')
            fk_displayfield = tablecol.get('fk').get('displayfield')
            value = values.get(id)
            if value == '' and tablecol.get('nullable'):
              value = None
            else:
              value = self.getFk( fk_tablename, fk_fieldname, fk_displayfield, value)
            if value != old_values.get(id,old[id]):
              c.append({'id':id,'value':value})
          consumed = True
        if not consumed and \
           (not tablecol.get('details')) and \
           (not tablecol.get('multiselect') or tablecol.get('multiselect').get('custom') or tablecol.get('multiselect').get('mysqlset')) and \
           (not tablecol.get('multimultiselect')):
          if values.has_key(id) and values.get(id) != old_values.get(id,old[id]):
            value = values.get(id)
            if value == '' and tablecol.get('nullable'):
              value = None
            elif type(value) is list:
              value = ','.join(value)
            if value != old_values.get(id,old[id]):
              c.append({'id':id,'value':value})
      # Assemble sql-statement
      if len(c) > 0:
        sqlStatement = []
        sqlStatement.append( 'UPDATE %s SET '%tablename)
        sqlStatement.append( ', '.join(map(lambda x: x['id']+'='+self.sql_quote__(tablename,x['id'],x['value']), c)))
        sqlStatement.append( 'WHERE %s=%s '%(primary_key,self.sql_quote__(tablename,primary_key,rowid)))
        sqlStatement = ' '.join(sqlStatement)
        try:
          if da.meta_type == 'Z MySQL Database Connection':
            self.executeQuery('SET @auth_user=\'%s\''%auth_user)
        except:
          raise zExceptions.InternalError(_globals.writeError( self, '[recordSet_Update]: can\'t set auth_user variable'))
        try:
          self.executeQuery( sqlStatement)
        except:
          raise zExceptions.InternalError(_globals.writeError( self, '[recordSet_Update]: can\'t update row - sqlStatement=' + sqlStatement))
      # Update intersections.
      self.recordSet_UpdateIntersections(tablename, rowid, values)
      # Return with row-id.
      return rowid


    """
    Update row-intersections in table.
    @param tablename: Name of the SQL-Table.
    @type tablename: C{string}
    @param rowid: ID of the row to be updated.
    @type rowid: C{any}
    @param values: Columns (id/value) to be updated.
    @type values: C{dict}
    """
    def recordSet_UpdateIntersections(self, tablename, rowid, values={}):
      tabledefs = self.getEntities()
      tabledef = filter(lambda x: x['id'].upper() == tablename.upper(), tabledefs)[0]
      tablecols = tabledef['columns']
      pk = (map(lambda x: x['id'], filter(lambda x: x.get('pk',0)==1, tablecols))+[tablecols[0]['id']])[0]
      for tablecol in tablecols:
        id = tablecol['id']
        column = self.getEntityColumn(tablename,id,row={})
        # Multiselect
        if tablecol.get('multiselect'):
          stereotype = tablecol['multiselect']
          sql = []
          sql.append('DELETE FROM %s'%stereotype['tablename'])
          sql.append('WHERE %s=%s'%(stereotype['fk'],self.sql_quote__(tablename,pk,rowid)))
          self.executeQuery('\n'.join(sql))
          for v in _globals.nvl(values.get(id),[]):
            sql = []
            c = [(column['src']['id'],rowid),(column['dst']['id'],v)]
            sql.append('INSERT INTO %s (%s)'%(stereotype['tablename'],' , '.join(map(lambda x:x[0],c))))
            sql.append('VALUES (%s)'%(' , '.join(map(lambda x:self.sql_quote__(stereotype['tablename'],x[0],x[1]),c))))
            self.executeQuery('\n'.join(sql))
        # Multimultiselect
        elif tablecol.get('multimultiselect'):
          stereotype = tablecol['multimultiselect']
          sql = []
          sql.append('DELETE FROM %s'%stereotype['tablename'])
          sql.append('WHERE %s=%s'%(stereotype['fk'],self.sql_quote__(tablename,pk,rowid)))
          self.executeQuery('\n'.join(sql))
          for v in _globals.nvl(values.get(id),['1|2','4|3']):
            sql = []
            items = stereotype.get('tables',[])
            c = [(stereotype['fk'],rowid)]
            for item in items:
              i = items.index(item)
              c.append((item['fk'],v.split('|')[i]))
            sql.append('INSERT INTO %s (%s)'%(stereotype['tablename'],' , '.join(map(lambda x:x[0],c))))
            sql.append('VALUES (%s)'%(' , '.join(map(lambda x:self.sql_quote__(stereotype['tablename'],x[0],x[1]),c))))
            self.executeQuery('\n'.join(sql))


    """
    Delete row from table.
    @param tablename: Name of the SQL-Table.
    @type tablename: C{string}
    @param rowid: ID of the row to be deleted.
    @type rowid: C{any}
    @rtype: C{None}
    """
    def recordSet_Delete(self, tablename, rowid):
      REQUEST = self.REQUEST
      auth_user = REQUEST.get('AUTHENTICATED_USER')      
      lang = REQUEST['lang']
      da = self.getDA()
      if tablename is None:
        raise zExceptions.InternalError("[recordSet_Delete]: tablename must not be None!")
      tabledefs = self.getEntities()
      tabledef = filter(lambda x: x['id'].upper() == tablename.upper(), tabledefs)[0]
      tablecols = tabledef['columns']
      primary_key = (map(lambda x: x['id'], filter(lambda x: x.get('pk',0)==1, tablecols))+[tablecols[0]['id']])[0]
      # Assemble sql-statement
      sqlStatement = []
      sqlStatement.append( 'DELETE FROM %s '%tablename)
      sqlStatement.append( 'WHERE %s=%s '%(primary_key,self.sql_quote__(tablename,primary_key,rowid)))
      sqlStatement = ' '.join(sqlStatement)
      try:
        if da.meta_type == 'Z MySQL Database Connection':
          self.executeQuery('SET @auth_user=\'%s\''%auth_user)
      except:
        raise zExceptions.InternalError(_globals.writeError( self, '[recordSet_Update]: can\'t set auth_user variable'))      
      try:
        self.executeQuery( sqlStatement)
      except:
        raise zExceptions.InternalError(_globals.writeError( self, '[recordSet_Delete]: can\'t delete row - sqlStatement=' + sqlStatement))


    ############################################################################
    ###
    ###   Blob (remote)
    ###
    ############################################################################

    # --------------------------------------------------------------------------
    #  ZMSSqlDb.delete_blob:
    # --------------------------------------------------------------------------
    def _delete_blob( self, tablename, id, rowid):
      tabledefs = self.getEntities()
      tabledef = filter(lambda x: x['id'].upper() == tablename.upper(), tabledefs)[0]
      tablecols = tabledef['columns']
      primary_key = (map(lambda x: x['id'], filter(lambda x: x.get('pk',0)==1, tablecols))+[tablecols[0]['id']])[0]
      column = self.getEntityColumn( tablename, id)
      blob = column['blob']
      path = blob['path']
      # Assemble sql-statement
      sqlStatement = []
      sqlStatement.append( 'SELECT '+id+' AS v FROM %s '%tablename)
      sqlStatement.append( 'WHERE %s=%s '%(primary_key,self.sql_quote__(tablename,primary_key,rowid)))
      sqlStatement = ' '.join(sqlStatement)
      try:
        for r in self.query( sqlStatement)['records']:
          filename = r['v']
          try:
            self.localfs_remove(path+filename)
          except: pass
          value = ''
          if column.get('nullable'):
            value = None
          else:
            value = self.sql_quote__(tablename,id,value)
          return value
      except:
        raise zExceptions.InternalError(_globals.writeError( self, '[get_blob]: can\'t delete blob - sqlStatement=' + sqlStatement))

    def delete_blob( self, auth_user, tablename, id, rowid, REQUEST=None, RESPONSE=None):
      """ ZMSSqlDb.delete_blob """
      user = self.findUser( auth_user)
      if user is None:
        raise zExceptions.Unauthorized
      return self._delete_blob( tablename=tablename, id=id, rowid=rowid)


    # --------------------------------------------------------------------------
    #  ZMSSqlDb._set_blob:
    # --------------------------------------------------------------------------
    def _set_blob( self, tablename, id, rowid=None, file=None, xml=None):
      print "ZMSSqlDb._set_blob",tablename,id
      tabledefs = self.getEntities()
      tabledef = filter(lambda x: x['id'].upper() == tablename.upper(), tabledefs)[0]
      tablecols = tabledef['columns']
      primary_key = (map(lambda x: x['id'], filter(lambda x: x.get('pk',0)==1, tablecols))+[tablecols[0]['id']])[0]
      column = self.getEntityColumn( tablename, id)
      blob = column['blob']
      path = blob['path']
      if file is None and xml is not None:
        file = self.parseXmlString( xml)
      # Normalize filename (crop path in local-fs)
      filename = file.filename
      i = max( filename.rfind('/'), filename.rfind('\\'))
      if i > 0:
        filename = filename[i+1:]
      fileext = ''
      i = filename.rfind( '.')
      if i > 0:
        fileext = filename[ i:]
        filename = filename[ :i]
      filename = filename + '_' + str( rowid) + fileext
      # Update
      oldfilename = 'None'
      if rowid is not None:
        # Assemble sql-statement
        sqlStatement = []
        sqlStatement.append( 'SELECT '+id+' AS v FROM %s '%tablename)
        sqlStatement.append( 'WHERE %s=%s '%(primary_key,self.sql_quote__(tablename,primary_key,rowid)))
        sqlStatement = ' '.join(sqlStatement)
        try:
          for r in self.query( sqlStatement)['records']:
            oldfilename = r['v']
        except:
          raise zExceptions.InternalError(_globals.writeError( self, '[set_blob]: can\'t set blob - sqlStatement=' + sqlStatement))
      # Remove old file from server-fs
      try:
        self.localfs_remove(path+oldfilename)
      except: pass
      # Write new file to server-fs
      self.localfs_write(path+filename,file.getData())
      return filename

    security.declareProtected('View', 'set_blob')
    def set_blob( self, auth_user, tablename, id, rowid=None, xml=None, REQUEST=None, RESPONSE=None):
      """ ZMSSqlDb.set_blob """
      user = self.findUser( auth_user)
      if user is None:
        raise zExceptions.Unauthorized
      return self._set_blob( tablename=tablename, id=id, rowid=rowid, xml=xml)


    # --------------------------------------------------------------------------
    #  ZMSSqlDb._get_blob:
    # --------------------------------------------------------------------------
    def _get_blob( self, tablename, id, rowid, REQUEST=None):
      data = ''
      tabledefs = self.getEntities()
      tabledef = filter(lambda x: x['id'].upper() == tablename.upper(), tabledefs)[0]
      tablecols = tabledef['columns']
      primary_key = (map(lambda x: x['id'], filter(lambda x: x.get('pk',0)==1, tablecols))+[tablecols[0]['id']])[0]
      column = self.getEntityColumn( tablename, id)
      blob = column['blob']
      path = blob['path']
      # Assemble sql-statement
      sqlStatement = []
      sqlStatement.append( 'SELECT '+id+' AS v FROM %s '%tablename)
      sqlStatement.append( 'WHERE %s=%s '%(primary_key,self.sql_quote__(tablename,primary_key,rowid)))
      sqlStatement = ' '.join(sqlStatement)
      try:
        for r in self.query( sqlStatement)['records']:
          filename = r['v']
          data = self.localfs_read( path+filename, REQUEST=REQUEST)
          if blob['type'] == 'image':
            return self.ImageFromData(data,filename)
          else:
            return self.FileFromData(data,filename)
      except:
        _globals.writeError( self, '[get_blob]: can\'t get_blob - sqlStatement=' + sqlStatement)
      return None


    # --------------------------------------------------------------------------
    #  ZMSSqlDb.get_blob:
    # --------------------------------------------------------------------------
    security.declareProtected('View', 'get_blob')
    def get_blob( self, tablename, id, rowid, REQUEST=None, RESPONSE=None):
      """ ZMSSqlDb.get_blob """
      blob = self._get_blob( tablename, id, rowid, REQUEST)
      return blob.getData()


    ############################################################################
    ###
    ###   Properties
    ###
    ############################################################################

    ############################################################################
    #  ZMSSqlDb.manage_changeProperties: 
    #
    #  Change Sql-Database properties.
    ############################################################################
    def manage_changeProperties(self, lang, REQUEST=None, RESPONSE=None): 
      """ ZMSSqlDb.manage_changeProperties """
      message = ''
      el_data = REQUEST.get('el_data','')
      target = 'manage_properties'
      
      if REQUEST.get('btn','') in [ self.getZMILangStr('BTN_EXECUTE')]:
        c = 0
        for sql in el_data.split(';'):
          try:
            sql = sql.replace( '\n', '')
            sql = sql.replace( '\r', '')
            sql = sql.strip()
            if len(sql) > 0:
              c = c + 1
              self.executeQuery( sql)
          except:
            message += _globals.writeError( self, '')
            break
        message += '[%i]'%c
        target = 'manage_sql'
      
      elif REQUEST.get('btn','') not in [ self.getZMILangStr('BTN_CANCEL'), self.getZMILangStr('BTN_BACK')]:
        self.connection_id = REQUEST['connection_id']
        self.max_rows = REQUEST['max_rows']
        self.charset = REQUEST['charset']
        self.setModel(REQUEST['model'])
        message = self.getZMILangStr('MSG_CHANGED')
      
      # Return with message.
      message = urllib.quote(message)
      el_data = urllib.quote(el_data)
      return RESPONSE.redirect('%s?lang=%s&manage_tabs_message=%s&el_data=%s'%(target,lang,message,el_data))


    ############################################################################
    ###
    ###   Configuration
    ###
    ############################################################################

    # --------------------------------------------------------------------------
    #  ZMSSqlDb.ajaxGetAutocompleteColumns:
    # --------------------------------------------------------------------------
    security.declareProtected('View', 'ajaxGetAutocompleteColumns')
    def ajaxGetAutocompleteColumns(self, tableName, fmt=None, REQUEST=None):
      """ ZMSSqlDb.ajaxGetAutocompleteColumns """
      RESPONSE = REQUEST.RESPONSE
      content_type = 'text/plain; charset=utf-8'
      filename = 'ajaxGetAutocompleteColumns.txt'
      RESPONSE.setHeader('Content-Type',content_type)
      RESPONSE.setHeader('Content-Disposition','inline;filename="%s"'%filename)
      RESPONSE.setHeader('Cache-Control', 'no-cache')
      RESPONSE.setHeader('Pragma', 'no-cache')
      l = map( lambda x: x['id'], filter( lambda x: x['type'] != '?', self.getEntity( tableName)['columns']))
      q = REQUEST.get( 'q', '').upper()
      if q:
        l = filter( lambda x: x.upper().find( q) >= 0, l)
      limit = int(REQUEST.get('limit',self.getConfProperty('ZMS.input.autocomplete.limit',15)))
      if len(l) > limit:
        l = l[:limit]
      if fmt == 'json':
        return self.str_json(l)
      return '\n'.join(l)

    ############################################################################
    #  ZMSSqlDb.manage_changeConfiguration: 
    #
    #  Change Sql-Database configuration.
    ############################################################################
    def manage_changeConfiguration(self, lang, btn='', key='all', REQUEST=None, RESPONSE=None):
      """ ZMSSqlDb.manage_changeConfiguration """
      message = ''
      t0 = time.time()
      id = REQUEST.get('id','')
      target = 'manage_configuration'
      
      # Change.
      # -------
      if btn == self.getZMILangStr('BTN_SAVE'):
        model = self.getModel()
        entities = filter( lambda x: x['id'].upper() == id.upper(), model)
        if entities:
          entity = entities[0]
        else:
          entity = {}
          entity['id'] = id
          entity['type'] = 'table'
          entity['columns'] = []
          model.append( entity)
        entity['label'] = REQUEST.get('label').strip()
        entity['type'] = REQUEST.get('type').strip()
        entity['interface'] = REQUEST.get('interface').strip()
        entity['filter'] = REQUEST.get('filter').strip()
        entity['access'] = {
         'insert': REQUEST.get( 'access_insert', []),
         'update': REQUEST.get( 'access_update', []),
         'delete': REQUEST.get( 'access_delete', []),
         'select': REQUEST.get( 'access_select', []),
        }
        cols = []
        for attr_id in REQUEST.get('attr_ids',[]):
          col = {}
          col['id'] = REQUEST.get( 'attr_id_%s'%attr_id, attr_id).strip()
          col['label'] = REQUEST.get( 'attr_label_%s'%attr_id, '').strip()
          col['index'] = int(REQUEST.get( 'attr_index_%s'%attr_id))
          col['hide'] = int(not REQUEST.get('attr_display_%s'%attr_id,0)==1)
          if REQUEST.has_key( 'attr_auto_%s'%attr_id):
            col['auto'] = REQUEST.get( 'attr_auto_%s'%attr_id)
          if REQUEST.has_key( 'attr_type_%s'%attr_id):
            t = REQUEST.get( 'attr_type_%s'%attr_id)
            if t in self.valid_types.keys():
              d = copy.deepcopy( self.valid_types[ t])
              c = []
              if type( d) is dict:
                xs = 'attr_%s_'%t
                xe = '_%s'%attr_id
                for k in filter( lambda x: x.startswith(xs) and x.endswith(xe), REQUEST.form.keys()):
                  xk = k[len(xs):-len(xe)].split('_')
                  xv = REQUEST[k]
                  if len( xk) == 1:
                    xk = xk[ 0]
                    if xk == 'options':
                      xv2 = []
                      for xi in xv.split('\n'):
                        xi = xi.replace('\r','')
                        if xi.find('->') > 0:
                          xi0 = xi[:xi.find('->')]
                          xi1 = xi[xi.find('->')+len('->'):]
                          if len(xi0) > 0 and len( xi1) > 0:
                            xv2.append( [xi0, xi1])
                        else:
                          if len(xi) > 0:
                            xv2.append( [xi, xi])
                      if len( xv2) > 0:
                        d[ xk] = xv2
                    else:
                      if type( xv) is str:
                        xv = xv.strip()
                        if len( xv) > 0:
                          d[ xk] = xv
                      elif type( xv) is int:
                        if xv != 0:
                          d[ xk] = xv
                  else:
                    if not d.has_key( xk[0]):
                      d[ xk[0]] = {}
                      c.append( xk[0])
                    if not d[ xk[0]].has_key( xk[-1]):
                      d[ xk[0]][ xk[-1]] = {}
                    if type( xv) is str:
                      xv = xv.strip()
                      if len( xv) > 0:
                        d[ xk[0]][ xk[-1]][ xk[1]] = xv
                    elif type( xv) is int:
                      if xv != 0:
                        d[ xk[0]][ xk[-1]][ xk[1]] = xv
              for i in c:
                l = d[i].values()
                l = map( lambda x: (x.get('index',l.index(x)),x), l)
                l.sort()
                l = map( lambda x: x[1], l)
                for x in l:
                  if not x.get('display'):
                    x['hide'] = 1
                  try: del x['display']
                  except: pass
                  try: del x['index']
                  except: pass
                l = filter( lambda x: len(x.keys()) > 0, l)
                d[i] = l
              col[ t] = d
          cols.append( ( col['index'], col))
        cols.sort()
        cols = map( lambda x: x[1], cols)
        # Insert
        attr_id = REQUEST.get('attr_id','').strip()
        attr_label = REQUEST.get('attr_label','').strip()
        attr_type = REQUEST.get('attr_type','').strip()
        if attr_id and attr_label and attr_type:
          newValue = {}
          newValue['id'] = attr_id
          newValue['label'] = attr_label
          newValue['hide'] = int(not REQUEST.get('attr_display',0)==1)
          newValue[attr_type] = {}
          cols.append(newValue)
        entity['columns'] = cols
        f = self.toXmlString( model)
        self.setModel(f)
        message = self.getZMILangStr('MSG_CHANGED')
      
      # Delete.
      # -------
      elif btn == 'delete':
        attr_id = REQUEST['attr_id'].strip()
        model = self.getModel()
        entities = filter( lambda x: x['id'].upper() == id.upper(), model)
        if entities:
          entity = entities[0]
          entity['columns'] = filter( lambda x: x['id'].upper() != attr_id.upper(), entity['columns'])
        f = self.toXmlString( model)
        self.setModel(f)
        message = self.getZMILangStr('MSG_CHANGED')
      
      # Import.
      # -------
      elif btn == self.getZMILangStr('BTN_IMPORT'):
        f = REQUEST['file']
        filename = f.filename
        self.setModel(f)
        message = self.getZMILangStr('MSG_IMPORTED')%('<i>%s</i>'%filename)
      
      # Insert.
      # -------
      elif btn == self.getZMILangStr('BTN_INSERT'):
        attr_id = REQUEST['attr_id'].strip()
        model = self.getModel()
        newValue = {}
        newValue['id'] = attr_id
        newValue['label'] = REQUEST.get('attr_label').strip()
        newValue['hide'] = int(not REQUEST.get('attr_display',0)==1)
        if REQUEST.get('attr_type'):
          newValue[REQUEST.get('attr_type')] = {}
        entities = filter( lambda x: x['id'].upper() == id.upper(), model)
        if entities:
          entity = entities[0]
        else:
          entity = {}
          entity['id'] = id
          entity['type'] = 'table'
          entity['columns'] = []
          model.append( entity)
        entity['columns'].append(newValue)
        f = self.toXmlString( model)
        self.setModel(f)
        message += self.getZMILangStr('MSG_INSERTED')%attr_id
      
      # Move to.
      # --------
      elif key == 'attr' and btn == 'move_to':
        pos = REQUEST['pos']
        attr_id = REQUEST['attr_id']
        model = self.getModel()
        entities = filter( lambda x: x['id'].upper() == id.upper(), model)
        if entities:
          entity = entities[0]
        else:
          entity = {}
          entity['id'] = id
          entity['type'] = 'table'
          entity['columns'] = map( lambda x: {'id':x['id']}, self.getEntity( id)['columns'])
          model.append( entity)
        cols = entity['columns']
        col = filter( lambda x: x['id'].upper() == attr_id.upper(), cols)[0]
        i = cols.index( col)
        cols.remove( col)
        cols.insert( pos, col)
        idx = 0
        for col in cols:
          col['index'] = idx
          idx = idx + 1
        f = self.toXmlString( model)
        self.setModel(f)
        message = self.getZMILangStr('MSG_MOVEDOBJTOPOS')%(("<i>%s</i>"%attr_id),(pos+1))
      
      # Return with message.
      target = self.url_append_params( target, { 'lang':lang, 'id':id, 'attr_id':REQUEST.get('attr_id','')})
      if len( message) > 0:
        message += ' (in '+str(int((time.time()-t0)*100.0)/100.0)+' secs.)'
        target = self.url_append_params( target, { 'manage_tabs_message':message})
      return RESPONSE.redirect( target)


    ############################################################################
    ###
    ###   Im/Export
    ###
    ############################################################################

    # --------------------------------------------------------------------------
    #  ZMSSqlDb.importFile
    # --------------------------------------------------------------------------
    def importFile(self, file, REQUEST):
      message = ''
      
      # Get filename.
      try: 
        filename = file.name
      except:
        filename = file.filename
      
      # Create temporary folder.
      folder = tempfile.mktemp()
      os.mkdir(folder)
      
      # Save to temporary file.
      filename = _fileutil.getOSPath('%s/%s'%(folder,_fileutil.extractFilename(filename)))
      _fileutil.exportObj(file,filename)
      
      # Find XML-file.
      if _fileutil.extractFileExt(filename) == 'zip':
        _fileutil.extractZipArchive(filename)
        filename = None
        for deep in [0,1]:
          for ext in ['xml', 'htm', 'html' ]:
            if filename is None:
              filename = _fileutil.findExtension(ext, folder, deep)
              break
        if filename is None:
          raise zExceptions.InternalError("XML-File not found!")
      
      # Import Filter.
      if REQUEST.get('filter','') in self.getFilterIds():
        filename = _filtermanager.importFilter(self, filename, REQUEST.get('filter',''), REQUEST)
      
      # Import XML-file.
      f = open(filename, 'r')
      xml = f.read()
      f.close()
      
      # Parse XML-file.
      v = self.parseXmlString(xml)
      for tablename in v.keys():
        for row in v.get(tablename):
          qs = 'INSERT INTO %s '%tablename
          qa = '( '
          qv = '( '
          c = 0
          for col in row.keys():
            val = row.get(col)
            if type(val) is str:
              val = "'" + val + "'"
            if c > 0:
              qa += ', '
              qv += ', '
            qa += str(col) + ' '
            qv += str(val) + ' '
            c += 1
          qs = qs + qa + ') VALUES ' + qv + ')'
          self.executeQuery(qs)
      
      # Remove temporary files.
      _fileutil.remove(folder, deep=1)
      
      # Return with message.
      message += self.getZMILangStr('MSG_IMPORTED')%('<i>%s</i>'%_fileutil.extractFilename(filename))
      return message


    ############################################################################
    #  ZMSSqlDb.manage_import: 
    #
    #  Import data to Sql-Database.
    ############################################################################
    def manage_import(self, lang, REQUEST=None, RESPONSE=None): 
      """ ZMSSqlDb.manage_import """
      message = ''
      
      if REQUEST.get('btn','') not in  [ self.getZMILangStr('BTN_CANCEL'), self.getZMILangStr('BTN_BACK')]:
        message = self.importFile(REQUEST.get('file'),REQUEST)
      
      # Return with message.
      message = urllib.quote(message)
      return RESPONSE.redirect('manage_importexport?lang=%s&manage_tabs_message=%s'%(lang,message))


    ############################################################################
    #  ZMSSqlDb.manage_export: 
    #
    #  Export data from Sql-Database.
    ############################################################################
    def manage_export(self, lang, REQUEST=None, RESPONSE=None): 
      """ ZMSSqlDb.manage_export """
      export = []
      export.append(self.getXmlHeader())
      export.append('<dictionary>\n')
      for id in REQUEST.get('ids',[]):
        export.append('<item key="%s">\n'%id)
        export.append('<list>\n')
        qs = 'SELECT * FROM %s'%id
        rs = self.query(qs)
        for i in rs['records']:
          export.append('<item>\n')
          export.append('<dictionary>\n')
          for c in rs['columns']:
            col = c['id']
            val = i[col]
            t = 'string'
            if type(val) is int:
              t = 'int'
            elif type(val) is float:
              t = 'float'
            export.append('<item key="%s" type="%s">\n'%(col,t))
            export.append(str(_xmllib.toCdata(self,val)))
            export.append('</item>\n')
          export.append('</dictionary>\n')
          export.append('</item>\n')
        export.append('</list>\n')
        export.append('</item>\n')
      export.append('</dictionary>\n')
      # Zip Xml-Export.
      filepath = tempfile.mktemp()
      _fileutil.mkDir(filepath)
      filename = filepath + os.sep + self.connection_id + '.xml'
      f = open(filename,'w')
      f.write(''.join(export))
      f.close()
      export = _fileutil.buildZipArchive(filename)
      _fileutil.remove(filepath,deep=1)
      # Return Zipped Xml-Export.
      content_type = 'application/zip'
      filename = self.connection_id + '.zip'
      RESPONSE.setHeader('Content-Type',content_type)
      RESPONSE.setHeader('Content-Disposition','inline;filename="%s"'%filename)
      return ''.join(export)


# call this to initialize framework classes, which
# does the right thing with the security assertions.
Globals.InitializeClass(ZMSSqlDb)

################################################################################