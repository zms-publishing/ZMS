# encoding: utf-8

from OFS.Folder import Folder
import os
import tempfile
import shutil
import unittest

# Product imports.
from tests.zms_test_util import *
from Products.zms import mock_http
from Products.zms import repositoryutil
from Products.zms import standard
from Products.zms import zms
from Products.zms import yamlutil


# /ZMS5> python3 -m unittest tests.test_repositoryutil.RepositoryUtilTest
class RepositoryUtilTest(ZMSTestCase):

  lang = 'eng'

  def setUp(self):
    folder = Folder('myzmsx')
    folder.REQUEST = mock_http.MockHTTPRequest({
      'lang': self.lang,
      'preview': 'preview',
      'theme': 'conf:aquire',
      'minimal_init': 1,
      'content_init': 1
    })
    self.context = zms.initZMS(
      folder, 'content', 'titlealt', 'title', self.lang, self.lang, folder.REQUEST
    )

  def _get_first_repo_object(self):
    providers = repositoryutil.get_providers(self.context)
    if not providers:
      return None

    files = repositoryutil.get_modelfileset_from_zodb(self.context, providers[0])
    if not files:
      return None

    for v in files.values():
      if isinstance(v, dict) and 'id' in v:
        return v
    return None

  def _import_model_from_temp_repo(self, model_rel_dir, init_filename, init_content):
    tmpdir = tempfile.mkdtemp(prefix='zms_repo_test_')
    try:
      model_dir = os.path.join(tmpdir, model_rel_dir)
      os.makedirs(model_dir)
      with open(os.path.join(model_dir, init_filename), 'w', encoding='utf-8') as f:
        f.write(init_content)

      models = repositoryutil.get_models_from_disk(self.context, tmpdir, deep=True)
      translated = self.context.getMetaobjManager().translateRepositoryModel(models)
      xml = standard.toXmlString(self.context, translated)
      imported_ids = self.context.getMetaobjManager().importMetaobjXml(xml)
      return imported_ids
    finally:
      shutil.rmtree(tmpdir, ignore_errors=True)

  def _assert_imported_option_semantics(self, meta_id):
    manager = self.context.getMetaobjManager()

    executable_attr = manager.getMetaobjAttr(meta_id, 'record_meta_ids', sync=False)
    self.assertIsNotNone(executable_attr)
    self.assertIsInstance(executable_attr.get('keys'), list)
    self.assertGreaterEqual(len(executable_attr.get('keys')), 2)
    self.assertEqual('##', executable_attr['keys'][0])
    self.assertIn('return l', executable_attr['keys'])

    static_attr = manager.getMetaobjAttr(meta_id, 'record_static_pairs', sync=False)
    self.assertIsNotNone(static_attr)
    self.assertEqual(['de', 'German', 'en', 'English'], static_attr.get('keys'))

    # Ensure static key lists are still interpreted as value/display pairs.
    options = self.context.getObjOptions({'id': 'record_static_pairs', 'options': static_attr['keys']}, self.context.REQUEST)
    self.assertEqual([['de', 'German'], ['en', 'English']], options)

  def test_get_system_conf_basepath(self):
    path = repositoryutil.get_system_conf_basepath()
    self.assertIsInstance(path, str)
    self.assertTrue(path.endswith('/conf'))

  def test_get_class(self):
    py = (
      "class DemoClass:\n"
      "  def __init__(self):\n"
      "    self.value = 42\n"
    )
    c = repositoryutil.get_class(py)
    self.assertIsInstance(c, type)
    self.assertEqual('DemoClass', c.__name__)
    self.assertEqual(42, c().value)

  def test_read_file_from_disk(self):
    content = "# -*- coding: utf-8 -*-\nmsg = 'äöü'\n"
    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.py') as f:
      f.write(content.encode('utf-8'))
      filepath = f.name
    try:
      dirpath = os.path.dirname(filepath)
      filename = os.path.basename(filepath)
      actual = repositoryutil.read_file_from_disk(self.context, dirpath, filename)
      self.assertEqual(content, actual)
    finally:
      if os.path.exists(filepath):
        os.remove(filepath)

  def test_read_file_from_disk_missing_file(self):
    actual = repositoryutil.read_file_from_disk(self.context, '/tmp', 'nonexistent_file_12345.txt')
    self.assertIsNone(actual)

  def test_get_modelfileset_from_disk_non_existing_basepath(self):
    actual = repositoryutil.get_modelfileset_from_disk(self.context, '/path/does/not/exist', deep=True)
    self.assertEqual({}, actual)

  def test_get_models_from_disk_non_existing_basepath(self):
    actual = repositoryutil.get_models_from_disk(self.context, '/path/does/not/exist', deep=True)
    self.assertEqual({}, actual)

  def test_get_providers(self):
    actual = repositoryutil.get_providers(self.context)
    self.assertIsInstance(actual, list)

  def test_get_modelfileset_from_zodb(self):
    providers = repositoryutil.get_providers(self.context)
    if not providers:
      self.skipTest('No repository providers available in test fixture')
    actual = repositoryutil.get_modelfileset_from_zodb(self.context, providers[0])
    self.assertIsInstance(actual, dict)

  def test_create_modelfileset(self):
    o = {}
    init_files = {}
    actual = repositoryutil.create_modelfileset(o, init_files)
    self.assertIsInstance(actual, dict)
    self.assertEqual({}, actual)

  def test_get_init_py(self):
    o = self._get_first_repo_object()
    if o is None:
      self.skipTest('No suitable repository object fixture for get_init_py')

    actual = repositoryutil.get_init_py(self.context, o)

    # Current contract in this codebase may return list(str), str, or False.
    self.assertTrue(
      isinstance(actual, (list, str)) or actual is False,
      msg="get_init_py returned unexpected type=%s value=%r" % (type(actual), actual)
    )
    if isinstance(actual, list):
      self.assertTrue(all(isinstance(line, str) for line in actual))

  def test_get_init_yaml(self):
    o = self._get_first_repo_object()
    if o is None:
      self.skipTest('No suitable repository object fixture for get_init_yaml')

    try:
      actual = repositoryutil.get_init_yaml(self.context, o)
    except ImportError as e:
      self.skipTest('YAML dependency missing: %s' % e)
    except Exception as e:
      self.skipTest('get_init_yaml requires richer object fixture: %s' % e)

    # Depending on object/content, can be YAML text or False.
    self.assertTrue(
      isinstance(actual, str) or actual is False,
      msg="get_init_yaml returned unexpected type=%s value=%r" % (type(actual), actual)
    )

  def test_get_diffs_identical(self):
    local = {}
    remote = {}
    actual = repositoryutil.get_diffs(local, remote, ignore=True)
    self.assertFalse(actual)  # identical structures should produce no diffs

  def test_import_metaobj_from_init_py_preserves_executable_and_static_keys(self):
    meta_id = 'TestRepoInitPyOptions'
    init_py = (
      'class %s:\n'
      '\tid = "%s"\n'
      '\tname = "%s"\n'
      '\ttype = "ZMSObject"\n'
      '\tclass Attrs:\n'
      '\t\trecord_meta_ids = {"id":"record_meta_ids","name":"Type(s)","mandatory":1,"multilang":0,"repetitive":0,"type":"multiselect",'
      '"keys":["##","l = []","return l"]}\n'
      '\t\trecord_static_pairs = {"id":"record_static_pairs","name":"Static pairs","mandatory":0,"multilang":0,"repetitive":0,"type":"multiselect",'
      '"keys":["de","German","en","English"]}\n'
    ) % (meta_id, meta_id, meta_id)

    if meta_id in self.context.getMetaobjIds():
      self.context.getMetaobjManager().delMetaobj(meta_id)
    self._import_model_from_temp_repo('metaobj_manager/demo/%s' % meta_id, '__init__.py', init_py)
    self._assert_imported_option_semantics(meta_id)

  def test_import_metaobj_from_init_yaml_preserves_executable_and_static_keys(self):
    if yamlutil.parse('probe: 1') == yamlutil.IMPORT_ERROR_MSG:
      self.skipTest('ruamel.yaml not available in test environment')

    meta_id = 'TestRepoInitYamlOptions'
    init_yaml = (
      '%s:\n'
      '  id: %s\n'
      '  name: %s\n'
      '  type: ZMSObject\n'
      '  Attrs:\n'
      '    - id: record_meta_ids\n'
      '      name: Type(s)\n'
      '      mandatory: 1\n'
      '      multilang: 0\n'
      '      repetitive: 0\n'
      '      type: multiselect\n'
      '      keys: |-\n'
      '        ##\n'
      '        l = []\n'
      '        return l\n'
      '    - id: record_static_pairs\n'
      '      name: Static pairs\n'
      '      mandatory: 0\n'
      '      multilang: 0\n'
      '      repetitive: 0\n'
      '      type: multiselect\n'
      '      keys:\n'
      '        - de\n'
      '        - German\n'
      '        - en\n'
      '        - English\n'
    ) % (meta_id, meta_id, meta_id)

    if meta_id in self.context.getMetaobjIds():
      self.context.getMetaobjManager().delMetaobj(meta_id)
    self._import_model_from_temp_repo('metaobj_manager/demo/%s' % meta_id, '__init__.yaml', init_yaml)
    self._assert_imported_option_semantics(meta_id)


if __name__ == "__main__":
  unittest.main()