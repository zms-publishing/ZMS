# encoding: utf-8

"""
Integration-style test for ZMSSqlDb grid-context row generation.

What this test does:
1. Bootstraps a minimal ZMS context using the lightweight mock HTTP request.
2. Creates an isolated temporary MySQL database from tests/dbtest.sql.
   The fixture SQL is reused, but the database name is replaced with a
   per-test random name to avoid collisions.
3. Loads the entity model from tests/dbtest.xml into the ZMSSqlDb instance
   as an in-memory model for this test fixture.
4. Reads real rows from the company table in MySQL.
5. Calls getEntityRecordHandler(...) and getRecordSetMainGridContext(...)
   to produce the row structures used by data-grid rendering.
6. Asserts that the generated row context contains the expected row keys,
   record values, and parameter wiring (including preserved primary key data).

Environment and reliability notes:
- The test auto-skips if no MySQL driver is installed.
- The test auto-skips if MySQL cannot be reached with the configured
  credentials.
- Connection parameters can be configured through:
  ZMS_TEST_MYSQL_HOST, ZMS_TEST_MYSQL_PORT,
  ZMS_TEST_MYSQL_USER, ZMS_TEST_MYSQL_PASSWORD.
- The temporary test database is dropped in tearDown.

Why some stubs are used:
- The unit-test fixture does not provide full Zope traversal/page-template
  runtime. Therefore, model and pagination/template parts are simplified so
  the test can focus on the Python row/context logic that drives the grid.
"""

from OFS.Folder import Folder
import importlib
import os
import unittest
import uuid

# Product imports.
from Products.zms import mock_http
from Products.zms import standard
from Products.zms import zms
from Products.zms import zmssqldb


# /ZMS5> python3 -m unittest tests.test_zmssqldb.ZMSSqlDbMySQLGridContextTest
class ZMSSqlDbMySQLGridContextTest(unittest.TestCase):

  lang = 'eng'

  def setUp(self):
    folder = Folder('myzmsx')
    folder.REQUEST = mock_http.MockHTTPRequest({
      'lang': self.lang,
      'preview': 'preview',
      'theme': 'conf:aquire',
      'minimal_init': 1,
      'content_init': 1,
    })
    self.context = zms.initZMS(
      folder, 'content', 'titlealt', 'title', self.lang, self.lang, folder.REQUEST
    )
    self.context.REQUEST.response = self.context.REQUEST.RESPONSE

    self._mysql_module, self._mysql_driver_name = self._import_mysql_driver()
    if self._mysql_module is None:
      self.skipTest('No MySQL driver available (tried: MySQLdb, pymysql, mysql.connector)')

    self._mysql_cfg = {
      'host': os.environ.get('ZMS_TEST_MYSQL_HOST', '127.0.0.1'),
      'port': int(os.environ.get('ZMS_TEST_MYSQL_PORT', '3306')),
      'user': os.environ.get('ZMS_TEST_MYSQL_USER', 'root'),
      'password': os.environ.get('ZMS_TEST_MYSQL_PASSWORD', ''),
    }

    self.db_name = 'zms_test_%s' % uuid.uuid4().hex[:10]

    try:
      self._execute_sql_fixture(self.db_name)
    except Exception as exc:
      self.skipTest('MySQL setup failed: %s' % exc)

    self.sql_db = self._create_sql_db_object()

  def tearDown(self):
    try:
      if getattr(self, '_mysql_module', None) is not None and getattr(self, 'db_name', None):
        self._drop_database(self.db_name)
    except Exception:
      # Keep teardown resilient for local test environments.
      pass

  def _import_mysql_driver(self):
    for module_name, driver_name in (
      ('MySQLdb', 'MySQLdb'),
      ('pymysql', 'pymysql'),
      ('mysql.connector', 'mysql.connector'),
    ):
      try:
        return importlib.import_module(module_name), driver_name
      except Exception:
        continue
    return None, None

  def _connect_mysql(self, database=None):
    kwargs = {
      'host': self._mysql_cfg['host'],
      'port': self._mysql_cfg['port'],
      'user': self._mysql_cfg['user'],
    }
    if self._mysql_cfg['password'] != '':
      if self._mysql_driver_name in ('MySQLdb', 'pymysql'):
        kwargs['passwd'] = self._mysql_cfg['password']
      else:
        kwargs['password'] = self._mysql_cfg['password']

    if database:
      if self._mysql_driver_name in ('MySQLdb', 'pymysql'):
        kwargs['db'] = database
      else:
        kwargs['database'] = database

    if self._mysql_driver_name == 'mysql.connector':
      kwargs['autocommit'] = True
      return self._mysql_module.connect(**kwargs)

    kwargs['charset'] = 'utf8mb4'
    conn = self._mysql_module.connect(**kwargs)
    try:
      conn.autocommit(True)
    except Exception:
      pass
    return conn

  def _split_sql_statements(self, sql_text):
    lines = []
    for line in sql_text.splitlines():
      if line.strip().startswith('--'):
        continue
      lines.append(line)
    clean_sql = '\n'.join(lines)
    return [s.strip() for s in clean_sql.split(';') if s.strip()]

  def _execute_sql_fixture(self, db_name):
    base = os.path.dirname(__file__)
    sql_path = os.path.join(base, 'dbtest.sql')
    with open(sql_path, 'r', encoding='utf-8') as f:
      sql_text = f.read()

    # Keep fixture semantics but isolate each test run by db name.
    sql_text = sql_text.replace('CREATE DATABASE testdb', 'CREATE DATABASE `%s`' % db_name)
    sql_text = sql_text.replace('USE testdb;', 'USE `%s`;' % db_name)

    conn = self._connect_mysql()
    try:
      cursor = conn.cursor()
      for stmt in self._split_sql_statements(sql_text):
        cursor.execute(stmt)
      try:
        cursor.close()
      except Exception:
        pass
    finally:
      conn.close()

  def _drop_database(self, db_name):
    conn = self._connect_mysql()
    try:
      cursor = conn.cursor()
      cursor.execute('DROP DATABASE IF EXISTS `%s`' % db_name)
      try:
        cursor.close()
      except Exception:
        pass
    finally:
      conn.close()

  def _fetch_records(self, sql, database):
    conn = self._connect_mysql(database=database)
    try:
      cursor = conn.cursor()
      cursor.execute(sql)
      rows = cursor.fetchall()
      col_names = [x[0] for x in cursor.description]
      records = [dict(zip(col_names, row)) for row in rows]
      try:
        cursor.close()
      except Exception:
        pass
      return records
    finally:
      conn.close()

  def _create_sql_db_object(self):
    obj_id = 'sql_db_under_test'
    self.context._setObject(obj_id, zmssqldb.ZMSSqlDb(obj_id, 1))
    sql_db = getattr(self.context, obj_id)
    sql_db.REQUEST.response = sql_db.REQUEST.RESPONSE
    sql_db.zmi_pagination = lambda **kwargs: ''

    model_path = os.path.join(os.path.dirname(__file__), 'dbtest.xml')
    with open(model_path, 'r', encoding='utf-8') as f:
      model_xml = f.read()

    # Keep test setup independent from DTML method creation in lightweight fixtures.
    model = standard.parseXmlString(model_xml)
    sql_db.model_xml = model_xml
    sql_db.model = model
    sql_db.getModel = lambda: model

    # This test validates row/grid context generation based on the fixture model.
    sql_db.getEntities = lambda: model

    return sql_db

  def test_get_recordset_main_grid_context_rows_from_mysql_fixture(self):
    records = self._fetch_records(
      'SELECT company_id, name, location FROM company ORDER BY company_id',
      self.db_name,
    )

    meta_obj_attrs = [
      self.sql_db.getEntityColumn('company', 'company_id'),
      self.sql_db.getEntityColumn('company', 'name'),
      self.sql_db.getEntityColumn('company', 'location'),
    ]
    for attr in meta_obj_attrs:
      attr['name'] = attr.get('label', attr['id'])

    request = mock_http.MockHTTPRequest({
      'URL': self.sql_db.absolute_url() + '/manage_main',
      'lang': self.lang,
      'qsize': 20,
    })
    request.response = request.RESPONSE

    options = {
      'metaObjAttrIds': ['company_id', 'name', 'location'],
      'metaObjAttrs': meta_obj_attrs,
      'records': records,
      'filtered_records': records,
      'url_params': {'qentity': 'company'},
      'record_handler': self.sql_db.getEntityRecordHandler('company', colNames=['name', 'location']),
      'actions': ['insert', 'update', 'delete'],
    }

    ctx = self.sql_db.getRecordSetMainGridContext(options, request)

    self.assertEqual(3, ctx['total'])
    self.assertEqual(3, ctx['size'])
    self.assertEqual(3, len(ctx['rows']))

    expected_row_keys = {'rindex', 'index', 'qindex', 'record', 'value', 'selected', 'params', 'title'}
    self.assertEqual(expected_row_keys, set(ctx['rows'][0].keys()))

    first_row = ctx['rows'][0]
    self.assertEqual(0, first_row['qindex'])
    self.assertEqual(1, first_row['value'])
    self.assertEqual('TechCorp', first_row['record']['name'])

    # Validate branch behavior: PK is preserved even when colNames excludes it.
    self.assertEqual(1, first_row['record']['company_id'])
    self.assertEqual(1, first_row['record']['__id__'])
    self.assertEqual(1, first_row['record']['params']['rowid'])
    self.assertEqual(1, first_row['params']['rowid'])
    self.assertEqual('company', first_row['params']['qentity'])


if __name__ == '__main__':
  unittest.main()
