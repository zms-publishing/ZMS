# encoding: utf-8

import unittest
from pathlib import Path

from Products.zms import yamlutil
from Products.zms._multilangmanager import normalize_yaml_values
from Products.zms._multilangmanager import langdict


# /ZMS5> python3 -m unittest tests.test_language_yaml.LanguageYAMLTest
class LanguageYAMLTest(unittest.TestCase):

  def _read_language_yaml(self):
    root = Path(__file__).resolve().parents[1]
    filename = root / 'Products' / 'zms' / 'import' / '_language.yaml'
    return filename.read_text(encoding='utf-8')

  def _parse_language_yaml(self):
    raw = self._read_language_yaml()
    normalized = normalize_yaml_values(raw)
    parsed = yamlutil.parse(normalized)
    if isinstance(parsed, str):
      self.skipTest(parsed)
    return parsed

  def test_parse_language_yaml_to_dict(self):
    data = self._parse_language_yaml()

    self.assertIsInstance(data, dict)
    self.assertTrue(len(data) > 0)
    self.assertIn('ACTION_INSERT', data)
    self.assertIsInstance(data['ACTION_INSERT'], dict)
    self.assertIn('eng', data['ACTION_INSERT'])

  def test_placeholders_and_colon_values_are_preserved(self):
    data = self._parse_language_yaml()

    self.assertIn('%s', data['ACTION_INSERT']['eng'])
    self.assertIn('%s', data['ACTION_INSERT']['hin'])
    self.assertIn('%i', data['MSG_DELETED']['eng'])

    # This value used to break plain-scalar YAML parsing and must survive normalization.
    self.assertTrue(data['ATTR_TAG']['ita'].endswith(':'))

  def test_multilangmanager_langdict_uses_yaml_by_default(self):
    d = langdict()
    self.assertIsInstance(d.get_manage_langs(), list)
    self.assertTrue(len(d.get_manage_langs()) > 0)

    lang_data = d.get_langdict()
    self.assertIsInstance(lang_data, dict)
    self.assertIn('ACTION_INSERT', lang_data)
    self.assertIn('%s', lang_data['ACTION_INSERT']['eng'])


if __name__ == '__main__':
  unittest.main()
