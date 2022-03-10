##############################################################################
#
# Copyright (c) 2011 Zope Foundation and Contributors
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this
# distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
import unittest
from unittest.mock import Mock, MagicMock, patch
from Products.zms import standard
from Products.zms import zms

class StandardTests(unittest.TestCase):

    def test_pystr(self):
        self.assertEquals(standard.pystr('ABC'),'ABC')
        self.assertEquals(standard.pystr_('ABC'),'ABC')
        self.assertEquals(standard.pystr(b'ABC'),'ABC')
        self.assertEquals(standard.pystr_(b'ABC'),'b\'ABC\'')
        self.assertEquals(standard.pystr(123),'123')
        self.assertEquals(standard.pystr_(123),'123')

    def test_url_append_params(self):
        expected = 'index.html?a=b&c=d&e=1&f:list=1&f:list=2&f:list=3'
        v = standard.url_append_params('index.html?a=b',{'c':'d','e':1,'f':[1,2,3]})
        self.assertEqual(expected,v)

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

