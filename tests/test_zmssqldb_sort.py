# encoding: utf-8

"""
Unit test for the sort parameters of the ZMSSqlDb record-set view.

The ZMI list view (manage_main) sorts by the request parameters qorder and
qorderdir and keeps them in the http-session. qorder must name a column of the
table, qorderdir may only be asc or desc. A parameter that is given twice (e.g.
by a hidden field of the filter form and by the url) arrives as list and must
not break the view.

No database is needed: the entity model is stubbed and only the generated
ORDER BY clause is inspected.
"""

from OFS.Folder import Folder
import unittest

# Product imports.
from Products.zms import _globals
from Products.zms import mock_http
from Products.zms import standard
from Products.zms import zms
from Products.zms import zmssqldb


# /ZMS5> python3 -m unittest tests.test_zmssqldb_sort.ZMSSqlDbSortTest
class ZMSSqlDbSortTest(unittest.TestCase):

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
    obj_id = 'sql_db_under_test'
    self.context._setObject(obj_id, zmssqldb.ZMSSqlDb(obj_id, 1))
    self.sql_db = getattr(self.context, obj_id)
    entities = [{
      'id': 'company',
      'columns': [
        {'id': 'id', 'type': 'int', 'pk': 1, 'datatype_key': _globals.DT_INT},
        {'id': 'name', 'type': 'string', 'datatype_key': _globals.DT_STRING},
        {'id': 'city', 'type': 'string', 'datatype_key': _globals.DT_STRING},
      ],
    }]
    self.sql_db.getEntities = lambda: entities
    self.sql_db.recordSet_Select = lambda tablename, select=None, where=None: 'SELECT * FROM %s ' % tablename

  def _request(self, form):
    """
    Simulate one manage_main request on the same session and return the
    ORDER BY part of the resulting sql-statement.
    """
    request = self.sql_db.REQUEST
    for key in [x for x in request.keys() if x.startswith(('filter', 'q', 'btn', 'sqlStatement', 'action'))]:
      del request.d[key]
    request.form = dict(form)
    for key, value in form.items():
      request.set(key, value)
    self.sql_db.recordSet_Init(request)
    self.sql_db.recordSet_Filter(request)
    self.sql_db.recordSet_Sort(request)
    sql = ''.join(request.get('sqlStatement'))
    self.assertEqual(sql.count('ORDER BY'), 1, sql)
    return sql[sql.index('ORDER BY'):].strip()

  def test_sort_by_column(self):
    self.assertEqual(self._request({'qorder': 'name', 'qorderdir': 'desc'}), 'ORDER BY name desc')
    self.assertEqual(self._request({'qorder': 'city', 'qorderdir': 'asc'}), 'ORDER BY city asc')

  def test_sort_kept_in_session(self):
    self._request({'qorder': 'name', 'qorderdir': 'desc'})
    self.assertEqual(self._request({}), 'ORDER BY name desc')

  def test_unknown_column_falls_back_to_first_column(self):
    self.assertEqual(self._request({'qorder': 'nosuchcol', 'qorderdir': 'asc'}), 'ORDER BY company.id asc')

  def test_qorderdir_given_twice(self):
    self.assertEqual(self._request({'qorder': 'name', 'qorderdir': ['asc', 'desc']}), 'ORDER BY name desc')

  def test_qorder_given_twice(self):
    self.assertEqual(self._request({'qorder': ['name', 'city'], 'qorderdir': 'asc'}), 'ORDER BY city asc')

  def test_qorderdir_only_asc_or_desc(self):
    for value in ['asc, (select 1)', 'desc; drop table company', '1', '', 'DESC ', 'Desc']:
      expected = 'desc' if value.strip().lower() == 'desc' else 'asc'
      self.assertEqual(self._request({'qorder': 'name', 'qorderdir': value}), 'ORDER BY name %s' % expected, value)

  def test_session_not_kept_invalid(self):
    self._request({'qorder': 'name', 'qorderdir': 'asc, (select 1)'})
    self.assertEqual(standard.get_session_value(self.sql_db, 'qorderdir_%s' % self.sql_db.id), 'asc')
    self.assertEqual(self._request({}), 'ORDER BY name asc')


if __name__ == '__main__':
  unittest.main()
