import importlib
import inspect
import os
import pkgutil
import unittest

from ZPublisher import zpublish_mark
from Products.zms import _deprecatedapi
from Products.zms import _zpublish_guard


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

    def test_guard_default_deny_complete(self):
        """Every public method of every class in Products.zms must carry an
        explicit zpublish mark (True or False) - no docstring fallback."""
        pkg_path = os.path.dirname(_zpublish_guard.__file__)
        unmarked = []
        for modinfo in pkgutil.iter_modules((pkg_path,)):
            module = importlib.import_module(
                'Products.zms.' + modinfo.name)
            for cls in vars(module).values():
                if (not isinstance(cls, type)
                        or cls.__module__ != module.__name__):
                    continue
                for name, func in vars(cls).items():
                    if name.startswith('_') or not inspect.isfunction(func):
                        continue
                    if zpublish_mark(func) is None:
                        unmarked.append(
                            '%s.%s.%s' % (modinfo.name, cls.__name__, name))
        self.assertEqual([], unmarked)

    def test_guard_publishable_list_valid(self):
        """Every entry in PUBLISHABLE must resolve to a real method that is
        actually marked as publishable."""
        for modname, classes in _zpublish_guard.PUBLISHABLE.items():
            module = importlib.import_module('Products.zms.' + modname)
            for clsname, names in classes.items():
                cls = getattr(module, clsname, None)
                self.assertIsNotNone(
                    cls, 'unknown class %s.%s' % (modname, clsname))
                for name in names:
                    func = vars(cls).get(name)
                    self.assertTrue(
                        inspect.isfunction(func),
                        'unknown method %s.%s.%s' % (modname, clsname, name))
                    self.assertIs(
                        zpublish_mark(func), True,
                        'not publishable: %s.%s.%s'
                        % (modname, clsname, name))
