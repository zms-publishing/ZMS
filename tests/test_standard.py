# encoding: utf-8

import unittest
import json
import time
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
