################################################################################
# zmssqldb.py
#
# $Id: zmssqldb.py,v 1.9 2004/11/23 23:04:49 zmsdev Exp $
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
from Globals import HTML, HTMLFile
from Products.ZSQLMethods.SQL import SQLConnectionIDs
import copy
import os
import sys
import urllib
import tempfile
import time
# Product Imports.
from zmsobject import ZMSObject
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
manage_addZMSSqlDbForm = HTMLFile('manage_addzmssqldbform', globals()) 
def manage_addZMSSqlDb(self, lang, _sort_id, REQUEST, RESPONSE):
  """ manage_addZMSSqlDb """
  
  ##### Create ####
  id_prefix = _globals.id_prefix(REQUEST.get('id','e'))
  obj = ZMSSqlDb(self.getNewId(id_prefix),_sort_id+1)
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

    # Properties.
    # -----------
    meta_type = meta_id = "ZMSSqlDb"

    # Management Options.
    # -------------------
    manage_options = ( 
	{'label': 'TAB_EDIT',		'action': 'manage_main'},
	{'label': 'TAB_IMPORTEXPORT',	'action': 'manage_importexport'},
	{'label': 'TAB_CONFIGURATION',	'action': 'manage_properties'},
	)

    # Management Permissions.
    # -----------------------
    __authorPermissions__ = (
		'manage','manage_main','manage_workspace',
		'manage_moveObjUp','manage_moveObjDown','manage_moveObjToPos',
		'manage_cutObjects','manage_copyObjects','manage_pasteObjs',
		'manage_userForm', 'manage_user',
		'manage_importexport', 'manage_import', 'manage_export',
		'manage_ajaxQuery', 'manage_exportexcel',
		)
    __administratorPermissions__ = (
		'manage_properties','manage_changeProperties',
		)
    __ac_permissions__=(
		('ZMS Author', __authorPermissions__),
		('ZMS Administrator', __administratorPermissions__),
		)

    # Management Interface.
    # ---------------------
    actions = HTMLFile('dtml/ZMSSqlDb/actions', globals())
    input_form = HTMLFile('dtml/ZMSSqlDb/input_form', globals())
    input_details = HTMLFile('dtml/ZMSSqlDb/input_details', globals())
    browse_db = HTMLFile('dtml/ZMSSqlDb/browse_db', globals())
    intersection_sql = HTMLFile('dtml/ZMSSqlDb/intersection_sql', globals())
    manage_main = HTMLFile('dtml/ZMSSqlDb/manage_main', globals())
    manage_importexport = HTMLFile('dtml/ZMSSqlDb/manage_importexport', globals())
    manage_properties = HTMLFile('dtml/ZMSSqlDb/manage_properties', globals())
    manage_exportexcel = HTMLFile('dtml/ZMSSqlDb/manage_exportexcel', globals())


    ############################################################################
    ###
    ###   CONSTRUCTOR
    ###
    ############################################################################

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
      model_xml =  getattr(self,'model_xml','<list>\n</list>')
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
        v = record[col['id']]
        if v is not None and type( v) is not int and type( v) is not float:
          try:
            v = unicode(v,charset).encode(encoding)
          except:
            row[col['id']+'_exception'] = _globals.writeException( self, '[record_encode__]: can\'t %s'%col['id'])
        row[col['id']] = v
      return row


    # --------------------------------------------------------------------------
    #  ZMSSqlDb.sql_quote__:
    # --------------------------------------------------------------------------
    def sql_quote__(self, tablename, columnname, v):
      entities = self.getEntities()
      entity = filter(lambda x: x['id'].upper() == tablename.upper(), entities)[0]
      col = filter(lambda x: x['id'].upper() == columnname.upper(), entity['columns'])[0]
      if col['type'] in ['int']:
        try:
          return str(int(str(v)))
        except:
          return "NULL"
      elif col['type'] in ['float']:
        try:
          return str(float(str(v)))
        except:
          return "NULL"
      elif col['type'] in ['date','datetime','time']:
        try:
          d = self.parseLangFmtDate(v)
          if d is None:
            raise 'Exception'
          return "'%s'"%self.getLangFmtDate(d,'eng','%s_FMT'%col['type'].upper())
        except:
          return "NULL"
      else:
        v = unicode(str(v),'utf-8').encode(getattr(self,'charset','utf-8'))
        if v.find("\'") >= 0: v=''.join(v.split("\'"))
        return "'%s'"%v


    # --------------------------------------------------------------------------
    # ZMSSqlDb.commit:
    # --------------------------------------------------------------------------
    def commit(self):
      databaseAdptr = getattr(self,self.connection_id)
      dbc = databaseAdptr._v_database_connection
      conn = dbc.getconn(False)
      conn.commit()


    # --------------------------------------------------------------------------
    # ZMSSqlDb.rollback:
    # --------------------------------------------------------------------------
    def rollback(self):
      databaseAdptr = getattr(self,self.connection_id)
      dbc = databaseAdptr._v_database_connection
      conn = dbc.getconn(False)
      conn.rollback()


    # --------------------------------------------------------------------------
    #  ZMSSqlDb.query:
    # --------------------------------------------------------------------------
    def query(self, qs, max_rows=None):
      from cStringIO import StringIO
      from Shared.DC.ZRDB.Results import Results
      from Shared.DC.ZRDB import RDB
      if max_rows is None:
        max_rows = getattr(self,'max_rows',999)
      _globals.writeBlock( self, '[query]: qs=%s, max_rows=%i'%(qs,max_rows))
      databaseAdptr = getattr(self,self.connection_id)
      dbc = databaseAdptr._v_database_connection
      res = dbc.query(qs,max_rows)
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
          _globals.writeException(self,'[query]: Column ' + colName + ' has unknown type ' + str(colType) + '!')
        column = {}
        column['id'] = colName
        column['key'] = colName
        column['label'] = colLabel
        column['name'] = colLabel
        column['type'] = colType
        column['sort'] = 1
        columns.append(column)
      keys = map(lambda x: x['id'], columns)
      return {'columns':columns,'records':result}


    # --------------------------------------------------------------------------
    #  ZMSSqlDb.manage_ajaxQuery:
    # --------------------------------------------------------------------------
    def manage_ajaxQuery(self, qs, REQUEST):
      """
      ZMSObject.manage_ajaxQuery
      """
      #-- Build xml.
      RESPONSE = REQUEST.RESPONSE
      content_type = 'text/xml; charset=utf-8'
      filename = 'ajaxQuery.xml'
      RESPONSE.setHeader('Content-Type',content_type)
      RESPONSE.setHeader('Content-Disposition','inline;filename=%s'%filename)
      RESPONSE.setHeader('Cache-Control', 'no-cache')
      RESPONSE.setHeader('Pragma', 'no-cache')
      self.f_standard_html_request( self, REQUEST)
      xml = '<?xml version="1.0" encoding="%s"?>'%REQUEST.get('encoding','iso-8859-1')
      xml += '<records>'
      result = self.query( qs, REQUEST.get('max_rows'))
      c = 0
      for record in result['records']:
        c = c + 1
        xml += '<record index="%i">'%c
        for column in result['columns']:
          id = column['id']
          v = record[id]
          if v:
            v = str(v)
            if column['type'] == 'string':
              xml += '<%s><![CDATA[%s]]></%s>'%(id,v,id)
            else:
              xml += '<%s>%s</%s>'%(id,str(v),id)
        xml += '</record>'
      xml += '</records>'
      return xml
      


    # --------------------------------------------------------------------------
    #  ZMSSqlDb.executeQuery:
    # --------------------------------------------------------------------------
    def executeQuery(self, qs):
      from cStringIO import StringIO
      from Shared.DC.ZRDB.Results import Results
      from Shared.DC.ZRDB import RDB
      _globals.writeBlock( self, '[executeQuery]: qs=%s'%qs)
      databaseAdptr = getattr(self,self.connection_id)
      dbc = databaseAdptr._v_database_connection
      res = dbc.query(qs)
      if type(res) is str:
        f=StringIO()
        f.write(res)
        f.seek(0)
        result=RDB.File(f)
      else:
        result=Results(res)
      return len(result)


    # --------------------------------------------------------------------------
    #  ZMSSqlDb.getEntityColumn:
    # --------------------------------------------------------------------------
    def getEntityColumn(self, tableName, columnName):
      columns = self.getEntity( tableName)['columns']
      return filter(lambda x: x['id'].upper() == columnName.upper(), columns)[0]


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
      databaseAdptr = getattr(self,self.connection_id)
      tableBrwsrs = databaseAdptr.tpValues()
      
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
          tableName = tableBrwsr.Name()
          tableType = tableBrwsr.Type().upper()
          if tableType == 'TABLE':
            # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
            # +- COLUMNS
            # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
            cols = []
            for columnBrwsr in tableBrwsr.tpValues():
              colId = columnBrwsr.tpId()
              colDescr = columnBrwsr.Description().upper()
              colType = 'string'
              colSize = None
              if colDescr.find('INT') >= 0:
                colType = 'int'
              elif colDescr.find('DATE') >= 0 or \
                   colDescr.find('TIME') >= 0:
                colType = 'datetime'
              elif colDescr.find('CHAR') >= 0 or \
                   colDescr.find('STRING') >= 0:
                colSize = 50
                i = colDescr.find('(')
                if i >= 0:
                  j = colDescr.find(')')
                  if j >= 0:
                    colSize = int(colDescr[i+1:j])
                if colSize > 50:
                  colType = 'text'
                else:
                  colType = 'string'
              col = {}
              col['key'] = colId
              col['id'] = col['key']
              col['label'] = ' '.join( map( lambda x: x.capitalize(), colId.split('_'))).strip()
              col['name'] = col['label']
              col['mandatory'] = colDescr.find('NOT NULL') > 0 or databaseAdptr.meta_type == 'Z Gadfly Database Connection'
              col['type'] = colType
              col['sort'] = 1
              col['nullable'] = not col['mandatory']
              # Add Column.
              cols.append(col)
            # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
            # +- TABLE
            # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
            if len(cols) > 0:
              entity = {}
              entity['id'] = tableName
              entity['label'] = ' '.join( map( lambda x: x.capitalize(), tableName.split('_'))).strip()
              entity['type'] = 'table'
              entity['columns'] = cols
              # Add Table.
              entities.append(entity)
      
      #-- Custom properties
      model = self.getModel()
      s = []
      for entity in entities:
        tableName = entity['id'].upper()
        tableInterface = entity.get('interface','')
        cols = []
        colNames = []
        for col in entity['columns']:
          colName = col['id'].upper()
          # Set custom column-properties
          for modelTable in filter(lambda x: x['id'].upper() == tableName, model):
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
            col['index'] = col.get('index',len(cols))
            col['type'] = col.get('type','?')
            col['key'] = col.get('key',col.get('id'))
            col['label'] = col.get('label',col.get('id'))
            cols.insert(col['index'], col)
            colNames.append(col['id'].upper())
        entity['interface'] = tableInterface
        entity['columns'] = cols
        # Set custom table-properties
        for modelTable in filter(lambda x: x['id'].upper() ==tableName, model):
          for modelTableProp in filter(lambda x: x not in ['columns'], modelTable.keys()):
            entity[modelTableProp] = modelTable[modelTableProp]
        # Add
        s.append((entity['label'],entity))
      
      #-- Sort entities
      s.sort()
      entities = map(lambda x: x[1], s)
      
      #-- [ReqBuff]: Returns value and stores it in buffer of Http-Request.
      return self.storeReqBuff( reqBuffId, entities, REQUEST)
      


    ############################################################################
    ###
    ###   RecordSet
    ###
    ############################################################################

    # --------------------------------------------------------------------------
    #  ZMSSqlDb.recordSet_Init:
    # --------------------------------------------------------------------------
    def recordSet_Init(self, REQUEST):
      """
      Initializes record-set.
      @param REQUEST: the triggering request
      @type REQUEST: ZPublisher.HTTPRequest
      @rtype: C{None}
      """
      SESSION = REQUEST.SESSION
      tabledefs = self.getEntities()
      tablename = SESSION.get('qentity_%s'%self.id)
      #-- Sanity check.
      SESSION.set('qentity_%s'%self.id,'')
      REQUEST.set('primary_key','')
      REQUEST.set('grid_cols',[])
      sqlStatement = REQUEST.get('sqlStatement',[])
      if len(tabledefs) > 0:
        if tablename not in map( lambda x: x['id'], tabledefs):
          tablename = tabledefs[0]['id']
        tablename = REQUEST.form.get('qentity',tablename)
        tabledef = filter(lambda x: x['id'].upper() == tablename.upper(), tabledefs)[0]
        tablecols = tabledef['columns']
        REQUEST.set('tabledef',tabledef)
        #-- SELECT
        SESSION.set('qentity_%s'%self.id,tablename)
        sqlStatement.append('SELECT * FROM ' + tablename + ' ')
        # Columns
        REQUEST.set('grid_cols',tablecols)
        # Primary Key.
        primary_key = map(lambda x: x['id'], filter(lambda x: x.get('pk',0)==1, tablecols))
        primary_key.append(None)
        REQUEST.set('primary_key',primary_key[0])
      REQUEST.set('sqlStatement',sqlStatement)


    # --------------------------------------------------------------------------
    #  ZMSSqlDb.recordSet_Filter:
    # --------------------------------------------------------------------------
    def recordSet_Filter(self, REQUEST):
      """
      Filter record-set by appending where clause to sql-statement.
      @param REQUEST: the triggering request
      @type REQUEST: ZPublisher.HTTPRequest
      @rtype: C{None}
      """
      SESSION = REQUEST.SESSION
      tablename = SESSION['qentity_%s'%self.id]
      tabledefs = self.getEntities()
      #-- Sanity check.
      SESSION.set('qfilters_%s'%self.id,REQUEST.form.get('qfilters',SESSION.get('qfilters_%s'%self.id,1)))
      if len(tabledefs) > 0:
        tabledef = filter(lambda x: x['id'].upper() == tablename.upper(), tabledefs)[0]
        tablecols = tabledef['columns']
        tablefilter = self.dt_html(tabledef.get('filter',''),REQUEST)
        #-- WHERE
        q = 'WHERE '
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
          for col in tablecols:
            columnname = col['id']
            v = SESSION.get(sessionvalue,'')
            op = SESSION.get(sessionop,'=')
            if SESSION.get(sessionattr,'') == columnname:
              sqlStatement = REQUEST.get('sqlStatement',[])
              if op in [ 'NULL', 'NOT NULL']:
                sqlStatement.append(q + columnname + ' IS ' + op + ' ')
              elif v != '':
                sqlStatement.append(q + columnname + ' ' + op + ' ' + self.sql_quote__(tablename, columnname, v) + ' ')
              REQUEST.set('sqlStatement',sqlStatement)
              q = 'AND '
        if len(tablefilter) > 0:
          sqlStatement = REQUEST.get('sqlStatement',[])
          sqlStatement.append(q + '(' + tablefilter + ') ')
          REQUEST.set('sqlStatement',sqlStatement)
          q = 'AND '


    # --------------------------------------------------------------------------
    #  ZMSSqlDb.recordSet_Sort:
    # --------------------------------------------------------------------------
    def recordSet_Sort(self, REQUEST):
      """
      Sort record-set by appending order-by clause to sql-statement.
      @param REQUEST: the triggering request
      @type REQUEST: ZPublisher.HTTPRequest
      @rtype: C{None}
      """
      SESSION = REQUEST.SESSION
      tablename = SESSION['qentity_%s'%self.id]
      tabledefs = self.getEntities()
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
              qorder = col['id']
              if col.get('type','') in ['date','datetime','time']:
                qorderdir = 'desc'
              break
        sqlStatement.append('ORDER BY ' + qorder + ' ' + qorderdir + ' ')
      REQUEST.set('sqlStatement',sqlStatement)
      REQUEST.set('qorder',qorder)
      REQUEST.set('qorderdir',qorderdir)


    ############################################################################
    ###
    ###   Actions
    ###
    ############################################################################

    # --------------------------------------------------------------------------
    #  ZMSSqlDb.recordSet_Insert
    # --------------------------------------------------------------------------
    def recordSet_Insert(self, tablename, values={}):
      """
      Insert row into record-set.
      @param tablename: Name of the SQL-Table.
      @type tablename: C{string}
      @param values: Columns (id/value) to be inserted.
      @type values: C{dict}
      @return: ID of the row that was inserted.
      @rtype: C{any}
      """
      REQUEST = self.REQUEST
      auth_user = REQUEST.get('AUTHENTICATED_USER')
      lang = REQUEST['lang']
      if tablename is None:
        raise "[recordSet_Insert]: tablename must not be None!"
      tabledefs = self.getEntities()
      tabledef = filter(lambda x: x['id'].upper() == tablename.upper(), tabledefs)[0]
      tablecols = tabledef['columns']
      primary_key = (map(lambda x: x['id'], filter(lambda x: x.get('pk',0)==1, tablecols))+[tablecols[0]['id']])[0]
      # Get columns to insert
      c = []
      for tablecol in tablecols:
        id = tablecol['id']
        if tablecol.get('auto'):
          if tablecol.get('auto') in ['insert','update']:
            if tablecol.get('type') in ['date','datetime']:
              c.append({'id':id,'value':self.sql_quote__(tablename,id,self.getLangFmtDate(time.time(),lang,'%s_FMT'%tablecol['type'].upper()))})
            elif tablecol.get('type') in ['int']:
              rs = self.query('SELECT MAX(%s) AS max_id FROM %s'%(id,tablename))['records']
              new_id = 0
              if len(rs) == 1:
                new_id = int(rs[0]['max_id'])+1
              c.append({'id':id,'value':str(new_id)})
        elif tablecol.get('blob'):
          blob = tablecol.get('blob')
          remote = blob.get('remote',self.absolute_url())
          if values.get('blob_%s'%id,None) is not None and values.get('blob_%s'%id).filename:
            data = values.get('blob_%s'%id,None)
            file = self.FileFromData( data, data.filename)
            xml = file.toXml()
            value = self.http_import(self.url_append_params(remote+'/set_blob',{'auth_user':blob.get('auth_user',auth_user.getId()),'tablename':tablename,'id':id,'xml':xml}),method='POST')
            c.append({'id':id,'value':self.sql_quote__(tablename,id,value)})
        elif (not tablecol.get('details')) and \
             (not tablecol.get('multiselect') or tablecol.get('multiselect').get('custom') or tablecol.get('multiselect').get('mysqlset')) and \
             (not tablecol.get('multimultiselect')):
          value = values.get(id,values.get(id.lower(),values.get(id.upper(),'')))
          if value == '' and tablecol['nullable']:
            value = 'NULL'
          else:
            value = self.sql_quote__(tablename,id,value)
          c.append({'id':id,'value':str(value)})
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
        raise _globals.writeException( self, '[recordSet_Insert]: can\'t insert row - sqlStatement=' + sqlStatement)
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
          raise _globals.writeException( self, '[recordSet_Insert]: can\'t get primary-key - sqlStatement=' + sqlStatement)
      return rowid


    # --------------------------------------------------------------------------
    #  ZMSSqlDb.recordSet_Update
    # --------------------------------------------------------------------------
    def recordSet_Update(self, tablename, rowid, values={},old_values={}):
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
      REQUEST = self.REQUEST
      auth_user = REQUEST.get('AUTHENTICATED_USER')
      lang = REQUEST['lang']
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
        raise _globals.writeException( self, '[recordSet_Update]: can\'t get old - sqlStatement=' + sqlStatement)
      # Get columns to update
      c = []
      for tablecol in tablecols:
        id = tablecol['id']
        if tablecol.get('auto'):
          if tablecol.get('auto') in ['update']:
            if tablecol.get('type') in ['date','datetime']:
              c.append({'id':id,'value':self.sql_quote__(tablename,id,self.getLangFmtDate(time.time(),lang,'%s_FMT'%tablecol['type'].upper()))})
        elif tablecol.get('blob'):
          blob = tablecol.get('blob')
          remote = blob.get('remote',self.absolute_url())
          if values.get('delete_blob_%s'%id,None):
            value = self.http_import(self.url_append_params(remote+'/delete_blob',{'auth_user':blob.get('auth_user',auth_user.getId()),'tablename':tablename,'id':id,'rowid':rowid}),method='POST')
            c.append({'id':id,'value':value})
          elif values.get('blob_%s'%id,None) is not None and values.get('blob_%s'%id).filename:
            data = values.get('blob_%s'%id,None)
            file = self.FileFromData( data, data.filename)
            xml = file.toXml()
            value = self.http_import(self.url_append_params(remote+'/set_blob',{'auth_user':blob.get('auth_user',auth_user.getId()),'tablename':tablename,'id':id,'rowid':rowid,'xml':xml}),method='POST')
            c.append({'id':id,'value':self.sql_quote__(tablename,id,value)})
        elif (not tablecol.get('details')) and \
             (not tablecol.get('multiselect') or tablecol.get('multiselect').get('custom') or tablecol.get('multiselect').get('mysqlset')) and \
             (not tablecol.get('multimultiselect')):
          if values.has_key(id) and values.get(id) != old_values.get(id,old[id]):
            value = self.sql_quote__(tablename,id,values.get(id))
            if values.get(id) == '' and tablecol['nullable']:
              value = 'NULL'
            c.append({'id':id,'value':str(value)})
      # Assemble sql-statement
      if len(c) > 0:
        sqlStatement = []
        sqlStatement.append( 'UPDATE %s SET '%tablename)
        sqlStatement.append( ', '.join(map(lambda x: x['id']+'='+x['value'], c)))
        sqlStatement.append( 'WHERE %s=%s '%(primary_key,self.sql_quote__(tablename,primary_key,rowid)))
        sqlStatement = ' '.join(sqlStatement)
        try:
          self.executeQuery( sqlStatement)
        except:
          raise _globals.writeException( self, '[recordSet_Update]: can\'t update row - sqlStatement=' + sqlStatement)
      # Return with row-id.
      return rowid


    # --------------------------------------------------------------------------
    #  ZMSSqlDb.recordSet_Delete
    # --------------------------------------------------------------------------
    def recordSet_Delete(self, tablename, rowid):
      """
      Delete row from table.
      @param tablename: Name of the SQL-Table.
      @type tablename: C{string}
      @param rowid: ID of the row to be deleted.
      @type rowid: C{any}
      @rtype: C{None}
      """
      REQUEST = self.REQUEST
      lang = REQUEST['lang']
      if tablename is None:
        raise "[recordSet_Delete]: tablename must not be None!"
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
        self.executeQuery( sqlStatement)
      except:
        raise _globals.writeException( self, '[recordSet_Delete]: can\'t delete row - sqlStatement=' + sqlStatement)


    ############################################################################
    ###
    ###   Blob (remote)
    ###
    ############################################################################

    # --------------------------------------------------------------------------
    #  ZMSSqlDb.delete_blob:
    # --------------------------------------------------------------------------
    def delete_blob( self, auth_user, tablename, id, rowid, REQUEST=None, RESPONSE=None):
      """ ZMSSqlDb.delete_blob """
      user = self.findUser( auth_user)
      if user is None:
        raise "Invalid user"
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
          if column['nullable']:
            value = 'NULL'
          else:
            value = self.sql_quote__(tablename,id,value)
          return value
      except:
        raise _globals.writeException( self, '[get_blob]: can\'t delete blob - sqlStatement=' + sqlStatement)


    # --------------------------------------------------------------------------
    #  ZMSSqlDb.set_blob:
    # --------------------------------------------------------------------------
    def set_blob( self, auth_user, tablename, id, rowid=None, xml=None, REQUEST=None, RESPONSE=None):
      """ ZMSSqlDb.set_blob """
      user = self.findUser( auth_user)
      if user is None:
        raise "Invalid user"
      tabledefs = self.getEntities()
      tabledef = filter(lambda x: x['id'].upper() == tablename.upper(), tabledefs)[0]
      tablecols = tabledef['columns']
      primary_key = (map(lambda x: x['id'], filter(lambda x: x.get('pk',0)==1, tablecols))+[tablecols[0]['id']])[0]
      column = self.getEntityColumn( tablename, id)
      blob = column['blob']
      path = blob['path']
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
          raise _globals.writeException( self, '[set_blob]: can\'t set blob - sqlStatement=' + sqlStatement)
      # Remove old file from server-fs
      try:
        self.localfs_remove(path+oldfilename)
      except: pass
      # Write new file to server-fs
      self.localfs_write(path+filename,file.getData())
      return filename


    # --------------------------------------------------------------------------
    #  ZMSSqlDb.get_blob:
    # --------------------------------------------------------------------------
    def get_blob( self, tablename, id, rowid, REQUEST, RESPONSE):
      """ ZMSSqlDb.get_blob """
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
      except:
        raise _globals.writeException( self, '[get_blob]: can\'t get_blob - sqlStatement=' + sqlStatement)
      return data


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
            message += _globals.writeException( self, '')
            break
        message += '[%i]'%c
      
      elif REQUEST.get('btn','') not in [ self.getZMILangStr('BTN_CANCEL'), self.getZMILangStr('BTN_BACK')]:
        self.connection_id = REQUEST['connection_id']
        self.max_rows = REQUEST['max_rows']
        self.charset = REQUEST['charset']
        self.setModel(REQUEST['model'])
        message = self.getZMILangStr('MSG_CHANGED')
      
      # Return with message.
      message = urllib.quote(message)
      el_data = urllib.quote(el_data)
      return RESPONSE.redirect('manage_properties?lang=%s&manage_tabs_message=%s&el_data=%s'%(lang,message,el_data))


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
          raise "XML-File not found!"
      
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
      RESPONSE.setHeader('Content-Disposition','inline;filename=%s'%filename)
      return ''.join(export)


    ############################################################################
    #  ZMSSqlDb.pub_export:
    #
    #  Export data from Sql-Database.
    ############################################################################
    def pub_export(self, lang, REQUEST=None, RESPONSE=None): 
      """ Exportable.pub_export """
      return self.manage_export( lang, REQUEST, RESPONSE)

################################################################################
