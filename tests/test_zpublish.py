import inspect
import unittest

from ZPublisher import zpublish_mark
from Products.zms import _deprecatedapi


class ZPublishTest(unittest.TestCase):

    def test_deprecatedapi_not_published(self):
        allowed = set(_deprecatedapi.PUBLISHED_VIA_URL)
        exposed = []
        for name, f in vars(_deprecatedapi.DeprecatedAPI).items():
            if not inspect.isfunction(f) or name.startswith('__'):
                continue
            if name in allowed:
                self.assertIsNot(zpublish_mark(f), False, name)
            elif zpublish_mark(f) is not False:
                exposed.append(name)
        self.assertEqual([], exposed)

    def test_http_import_wrapper_forbidden(self):
        f = _deprecatedapi.DeprecatedAPI.http_import
        self.assertIs(zpublish_mark(f), False)
