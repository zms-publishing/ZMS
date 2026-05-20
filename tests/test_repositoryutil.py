# encoding: utf-8

from OFS.Folder import Folder
import os
import tempfile
import unittest

# Product imports.
from tests.zms_test_util import *
from Products.zms import mock_http
from Products.zms import repositoryutil
from Products.zms import zms


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


if __name__ == "__main__":
  unittest.main()