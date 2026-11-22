import importlib
import inspect
import os
import pkgutil
import unittest

import Products.zms
from ZPublisher import zpublish_mark
from Products.zms import _deprecatedapi

_pkg_path = (os.path.dirname(os.path.abspath(
    Products.zms.__file__)),)


class ZPublishTest(unittest.TestCase):

    def test_deprecatedapi_not_published(self):
        """Only the explicitly @zpublish-decorated ajax endpoints of the
        deprecated API stay URL-callable; everything else is forbidden."""
        allowed = ('ajaxGetNodes', 'ajaxGetNode',
                   'ajaxGetParentNodes', 'ajaxGetChildNodes')
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

    def test_default_deny_complete(self):
        """Every public method of every class in Products.zms must carry an
        explicit zpublish mark (True or False) - no docstring fallback."""
        unmarked = []
        for modinfo in pkgutil.iter_modules(_pkg_path):
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

    def test_guard_marks_source_decorated_methods(self):
        """The guard must not override explicit @zpublish marks from the
        source: exactly the decorated methods are publishable, all other
        public methods are explicitly non-publishable."""
        decorated = []
        guarded = []
        for modinfo in pkgutil.iter_modules(_pkg_path):
            module = importlib.import_module(
                'Products.zms.' + modinfo.name)
            for cls in vars(module).values():
                if (not isinstance(cls, type)
                        or cls.__module__ != module.__name__):
                    continue
                for name, func in vars(cls).items():
                    if name.startswith('_') or not inspect.isfunction(func):
                        continue
                    if zpublish_mark(func) is True:
                        decorated.append(
                            '%s.%s.%s' % (modinfo.name, cls.__name__, name))
                    elif zpublish_mark(func) is False:
                        guarded.append(
                            '%s.%s.%s' % (modinfo.name, cls.__name__, name))
        # (107 = 4 ajax endpoints in _deprecatedapi + 103 allow-listed
        #  methods decorated with @zpublish in the source.)
        self.assertEqual(107, len(decorated))
        self.assertGreater(len(guarded), 800)

    def test_guard_preserves_source_mark_false(self):
        """Explicit @zpublish(False) marks from the source (e.g. the
        http_import wrapper) remain False and are not re-enabled."""
        from Products.zms import _confmanager
        self.assertIs(zpublish_mark(
            _confmanager.ConfManager.getConfXmlFile), False)


if __name__ == '__main__':
    unittest.main()
