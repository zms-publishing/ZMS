# encoding: utf-8

"""
Unit test for the filter state of the ZMSSqlDb record-set view.

The filter of the ZMI list view (manage_main) is kept in the http-session.
It may only be changed by the filter form (buttons BTN_REFRESH and BTN_RESET)
and by the filter inputs in the grid header (grid form submitted by script with
an empty btn and no action). Saving, cancelling or deleting a record is rendered
by the same manage_main request and carries its own btn value (e.g. BTN_SAVE),
row actions of the grid carry an action; such requests must keep the filter
instead of clearing it.

No database is needed: the entity model is stubbed and only the generated
WHERE clause is inspected.
"""

from OFS.Folder import Folder
import unittest

# Product imports.
from Products.zms import _globals
from Products.zms import mock_http
from Products.zms import zms
from Products.zms import zmssqldb


# /ZMS5> python3 -m unittest tests.test_zmssqldb_filter.ZMSSqlDbFilterSessionTest
class ZMSSqlDbFilterSessionTest(unittest.TestCase):

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

  def _request(self, form, btn=None):
    """
    Simulate one manage_main request on the same session and return the
    resulting sql-statement.
    """
    request = self.sql_db.REQUEST
    for key in [x for x in request.keys() if x.startswith(('filter', 'q', 'btn', 'sqlStatement', 'action'))]:
      del request.d[key]
    request.form = dict(form)
    if btn is not None:
      request.form['btn'] = btn
      request.set('btn', btn)
    for key, value in form.items():
      request.set(key, value)
    self.sql_db.recordSet_Init(request)
    self.sql_db.recordSet_Filter(request)
    return ''.join(request.get('sqlStatement'))

  def _search(self, *filters):
    form = {}
    for index, (attr, value) in enumerate(filters):
      form['filterattr%i' % index] = attr
      form['filterop%i' % index] = ''
      form['filtervalue%i' % index] = value
    return self._request(form, btn='BTN_REFRESH')

  def test_search_sets_filter(self):
    sql = self._search(('name', 'Acme'))
    self.assertIn('WHERE', sql)
    self.assertIn('company.name LIKE', sql)
    self.assertIn('Acme%', sql)

  def test_filter_kept_after_save(self):
    self._search(('name', 'Acme'))
    for action in ['insert', 'update']:
      sql = self._request({'action': action, 'name': 'Acme Ltd', 'rowid': '1'}, btn='BTN_SAVE')
      self.assertIn('company.name LIKE', sql, 'filter lost after %s' % action)
      self.assertEqual(self.sql_db.REQUEST.get('filtervalue0'), 'Acme')

  def test_filter_kept_after_cancel_and_delete(self):
    self._search(('name', 'Acme'))
    sql = self._request({'action': 'update', 'rowid': '1'}, btn='BTN_CANCEL')
    self.assertIn('company.name LIKE', sql)
    sql = self._request({'action': 'delete', 'rowid': '1'}, btn='BTN_DELETE')
    self.assertIn('company.name LIKE', sql)

  def test_filter_kept_without_button(self):
    self._search(('name', 'Acme'))
    sql = self._request({'qindex': 20})
    self.assertIn('company.name LIKE', sql)

  def test_grid_header_filter(self):
    # Typing in a filter input of the grid header submits the grid form with
    # an empty btn and no action (zpt/ZMSRecordSet/main_grid.zpt).
    form = {'action': '', 'filterattr10': 'name', 'filterop10': '', 'filtervalue10': 'Acme'}
    sql = self._request(form, btn='')
    self.assertIn('company.name LIKE', sql)
    self.assertIn('Acme%', sql)
    sql = self._request({'action': 'update', 'rowid': '1'}, btn='BTN_SAVE')
    self.assertIn('company.name LIKE', sql)

  def test_filter_kept_after_grid_row_action(self):
    # Row actions of the grid submit the same form with an empty btn, but with
    # an action; the header inputs may be empty then.
    self._search(('name', 'Acme'))
    for action in ['delete', 'move', 'duplicate']:
      form = {'action': action, 'qindex': '0', 'filterattr10': 'name', 'filterop10': '', 'filtervalue10': ''}
      sql = self._request(form, btn='')
      self.assertIn('company.name LIKE', sql, 'filter lost after grid action %s' % action)

  def test_reset_clears_filter(self):
    self._search(('name', 'Acme'))
    sql = self._request({'filterattr0': 'name', 'filterop0': '', 'filtervalue0': 'Acme'}, btn='BTN_RESET')
    self.assertNotIn('WHERE', sql)
    sql = self._request({})
    self.assertNotIn('WHERE', sql)

  def test_search_removes_dropped_filter_row(self):
    sql = self._search(('name', 'Acme'), ('city', 'Hamburg'))
    self.assertIn('company.city LIKE', sql)
    sql = self._search(('name', 'Acme'))
    self.assertIn('company.name LIKE', sql)
    self.assertNotIn('company.city', sql)
    sql = self._request({'action': 'update', 'rowid': '1'}, btn='BTN_SAVE')
    self.assertNotIn('company.city', sql)
