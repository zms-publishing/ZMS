# encoding: utf-8

import unittest
import json
import time
import zExceptions
from unittest.mock import Mock, MagicMock, patch
from Products.zms import standard
from Products.zms import zms

# /Products/zms> python -m unittest discover -s unit_tests
# /Products/zms> python -m unittest tests.test_standard.StandardTest
class StandardTest(unittest.TestCase):

    def test_pystr(self):
        self.assertEqual(standard.pystr('ABC'),'ABC')
        self.assertEqual(standard.pystr(b'ABC'),'ABC')
        self.assertEqual(standard.pystr(123),'123')

    def test_url_append_params(self):
        expected = 'index.html?a=b&c=d&e=1&f:list=1&f:list=2&f:list=3'
        v = standard.url_append_params('index.html?a=b',{'c':'d','e':1,'f':[1,2,3]})
        self.assertEqual(expected,v)

    def test_url_inherit_params(self):
        request = Mock()
        request.form = {'form_modified':True,'is_new':False,'pageIndex':2,'qsize':20,'ratio':1.5,'qcolumns':['a','b'],'qentity':'person'}
        v = standard.url_inherit_params('manage_main', request, exclude=['pageIndex'], sep='&')
        expected = 'manage_main?form_modified%3Aboolean=True&is_new%3Aboolean=False&qsize%3Aint=20&ratio%3Afloat=1.5&qcolumns%3Alist=a&qcolumns%3Alist=b&qentity=person'
        self.assertEqual(expected,v)

    def test_url_inherit_params_roundtrip(self):
        # The inherited params must convert back to the same values in ZPublisher
        # (a bool used to be sent as key:int=True, which raised a ValueError in field2int).
        from urllib.parse import parse_qsl, urlsplit
        from ZPublisher.Converters import get_converter
        request = Mock()
        request.form = {'form_modified':True,'is_new':False,'qsize':20,'ratio':1.5}
        url = standard.url_inherit_params('manage_main', request, sep='&')
        parsed = {}
        for key, value in parse_qsl(urlsplit(url).query):
            name, _, typ = key.partition(':')
            parsed[name] = get_converter(typ)(value)
        self.assertEqual(request.form, parsed)
        self.assertIs(parsed['form_modified'], True)
        self.assertIs(parsed['is_new'], False)

    def test_remove_tags(self):
        self.assertEqual('foo bar',standard.remove_tags('foo\n<\tscript\ttype="javascript"\n>window.onload(\'<script>\')</script\t\n>bar'))
        self.assertEqual('foo bar',standard.remove_tags('foo\n<\tstyle\t\n>body {}</style\t\n>bar'))
        self.assertEqual('foo bar',standard.remove_tags('''
            <!DOCTYPE html>
            <meta name="description" content="Test regular expressions">
            
            <!--	###comment
            --><body>	
            	foo	
            </body><!-- -->

                <script	type="text/javascript"
                nonce="Ow7cULQDb0b483xVnZngrwRoCICLoMVI8GOprsWtvWU=">
                	try {
                		window._pageTimings = window._pageTimings || {};
                		window._pageTimings["TTJSStart"] = Math.round(performance.now());
                	} catch (e) {
                		console.error("Error in adding TTJSStart marker");
                	}
                </script 
                bar>
            bar</em>
                <script type="text/javascript">
                </script	>
                
                <style>
                /* style */
            .dropdown-submenu {
                position: relative;
            }
            .dropdown-submenu>.dropdown-menu>li>a:hover {
                background-color: #F5F5F5;
                border-left-width: 5px;
                padding-left: 15px;
            }
            </style>
        '''))

    def test_string_maxlen(self):
        self.assertEqual('foo\nbar',standard.string_maxlen('foo\n<\tscript\ttype="javascript"\n>window.onload(\'<script>\')</script\t\n>bar'))
        self.assertEqual('foo\nbar',standard.string_maxlen('foo\n<\tstyle\t\n>body {}</style\t\n>bar'))

    def test_sort_item(self):
        self.assertEqual(0.1,standard.sort_item(0.1))
        self.assertEqual(0,standard.sort_item(None))
        self.assertEqual(0,standard.sort_item(''))
        self.assertEqual(0,standard.sort_item(False))
        self.assertEqual(1,standard.sort_item(True))
        self.assertEqual('foo',standard.sort_item('foo'))
        self.assertEqual('bar',standard.sort_item('bar'))
        self.assertEqual('aeoeue',standard.sort_item(u'äöü'))

    def test_sort_list(self):
        self.assertEqual([1,2,3],standard.sort_list([3,1,2]))
        self.assertEqual([{'sort_id':1,'value':'C'},{'sort_id':2,'value':'B'},{'sort_id':3,'value':'A'}],standard.sort_list([{'sort_id':3,'value':'A'},{'sort_id':1,'value':'C'},{'sort_id':2,'value':'B'}],'sort_id'))


    class FakeHTTPConnection:
        def __init__(self, status=200, reason='OK'):
            self.status = status
            self.reason = reason
        def request(self, *args):
            # If you need to do any logic to change what is returned, you can do it in this class
            pass
        def getresponse(self):
            class FakeHTTPResponse:
                def __init__(self, status, reason):
                    self.status = status
                    self.reason = reason
                def read(self):
                    return ''
            return FakeHTTPResponse(self.status, self.reason)

    @patch('http.client.HTTPConnection', new=MagicMock(return_value=FakeHTTPConnection(200)))
    def test_httpimport(self):
        context = Mock(spec=zms.ZMS)
        context.getConfProperty.side_effect = (lambda x, y: y)
        url = "http://foo/bar?john=doe"
        v = standard.http_import(context,url)

    def test_scalar(self):
        self.assertEqual(123, standard.scalar(123))
        self.assertEqual(12.34, standard.scalar(12.34))
        self.assertEqual("abc", standard.scalar("abc"))
        self.assertEqual('"2024-01-01T00:00:00-00:00"', json.dumps(standard.scalar(time.struct_time((2024, 1, 1, 0, 0, 0, 0, 1, -1)))))
        self.assertEqual('{"key": "value"}', json.dumps(standard.scalar( {"key": "value"} ) ) )

    def test_getPACKAGE_HOME(self):
        # Test that getPACKAGE_HOME returns a valid path
        result = standard.getPACKAGE_HOME()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)
        # Verify it contains typical site-packages indicators
        self.assertTrue('site-packages' in result or 'dist-packages' in result)

    def test_localfs_permission_without_context_is_valueerror(self):
        with self.assertRaises(ValueError):
            standard._localfs_permitted(None, '/not/configured', 'read')

    @patch('Products.zms.standard.getTempFolder', return_value='/tmp/zms-temp')
    @patch('Products.zms.standard.package_home', return_value='/tmp/zms-package')
    def test_localfs_permission_uses_context_configuration(self, _, __):
        context = Mock()
        context.getConfProperty.return_value = '/allowed'
        context.getMediaDb.return_value = None

        self.assertTrue(standard._localfs_permitted(context, '/allowed/file.txt', 'read'))
        with self.assertRaises(zExceptions.Forbidden) as exc:
            standard._localfs_permitted(context, '/denied/file.txt', 'read')
        self.assertEqual(exc.exception.status, 403)

