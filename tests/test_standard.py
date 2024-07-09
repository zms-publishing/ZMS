# encoding: utf-8

import unittest
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

    def test_date_api(self):
        from DateTime.DateTime import DateTime
        self.assertEquals(35, standard.daysBetween((2024,1,1,12,0,0,0,0,0), (2024,2,5,12,0,0,0,0,0)))
        self.assertEquals(0, standard.daysBetween((2024,1,1,12,0,0,0,0,0), (2024,1,1,12,0,0,0,0,0)))
        self.assertEquals(-50, standard.daysBetween((2024,1,1,12,0,0,0,0,0), (2023,11,12,12,0,0,0,0,0)))
        self.assertEquals(1, standard.compareDate((2024,1,1,12,0,0,0,0,0), (2024,2,5,12,0,0,0,0,0)))
        self.assertEquals(0, standard.compareDate((2024,1,1,12,0,0,0,0,0), (2024,1,1,12,0,0,0,0,0)))
        self.assertEquals(-1, standard.compareDate((2024,1,1,12,0,0,0,0,0), (2023,11,12,12,0,0,0,0,0)))        

    def test_operator_api(self):
        self.assertEquals(int, standard.operator_gettype(1))
        self.assertEquals(str, standard.operator_gettype('foo'))
        self.assertEquals(str, standard.operator_gettype(u'foo'))
        d = {'john':'doe'}
        self.assertFalse('foo' in d)
        self.assertIsNone(d.get('foo'))
        standard.operator_setitem(d, 'foo', 'bar')
        self.assertTrue('foo' in d)
        self.assertEquals('bar', d.get('foo'))
        self.assertEquals('bar', standard.operator_getitem(d, 'foo'))
        self.assertEquals('bar', standard.operator_getitem(d, 'Foo'))
        self.assertEquals('bar', standard.operator_getitem(d, 'FOO'))
        standard.operator_delitem(d, 'foo')
        self.assertFalse('foo' in d)
        self.assertIsNone(d.get('foo'))

    def test_mappings_api(self):
        l1 = ['A', 'B', 'B', 'C']
        l2 = ['C', 'D']
        self.assertListEqual(['C'], standard.intersection_list(l1, l2))
        self.assertListEqual(['A', 'B', 'B'], standard.difference_list(l1, l2))
        self.assertListEqual(['A', 'B', 'B', 'C', 'D'], standard.concat_list(l1, l2))
        self.assertDictEqual({'A':'B','B':'C'}, standard.dict_list(l1))
        self.assertListEqual(['A', 'B', 'C'], standard.distinct_list(l1))
