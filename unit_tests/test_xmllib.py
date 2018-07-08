# encoding: utf-8

import sys
import unittest
sys.path.append("..")
# Product imports.
from zms_test_util import *
import standard
import zms

# /Products/zms> python -m unittest discover -s unit_tests
# /Products/zms> python -m unittest unit_tests.test_xmllib.XmlUtilTest
def remove_whitespace_between_tags(xml):
  import re
  xml = re.sub('>(\\s+?)<','><',xml).strip()
  return xml

class XmlUtilTest(ZMSTestCase):

    def setUp(self):
        print(self,"setUp")
        self.context = zms.ZMS()


    def test_toXmlString(self):
      
      v = {'a':1,'b':2,'c':'XXX','d':'YYY'}
      xml = standard.toXmlString(self.context,v)
      expected = '<dictionary><item key="a" type="int">1</item><item key="b" type="int">2</item><item key="c">XXX</item><item key="d">YYY</item></dictionary>'
      self.assertEqual(expected,remove_whitespace_between_tags(xml))
      nv = standard.parseXmlString(xml)
      self.assertEqual(v,nv)
      
      v = ['a',1,'b',2]
      xml = standard.toXmlString(self.context,v)
      expected = '<list><item>a</item><item type="int">1</item><item>b</item><item type="int">2</item></list>'
      self.assertEqual(expected,remove_whitespace_between_tags(xml))
      nv = standard.parseXmlString(xml)
      self.assertEqual(v,nv)
      
      v = ['a',{'b':2},1]
      xml = standard.toXmlString(self.context,v)
      expected = '<list><item>a</item><item type="dictionary"><dictionary><item key="b" type="int">2</item></dictionary></item><item type="int">1</item></list>'
      self.assertEqual(expected,remove_whitespace_between_tags(xml))
      nv = standard.parseXmlString(xml)
      self.assertEqual(v,nv)
      
      v = {'a':['b',2],'c':1}
      xml = standard.toXmlString(self.context,v)
      expected = '<dictionary><item key="a" type="list"><list><item>b</item><item type="int">2</item></list></item><item key="c" type="int">1</item></dictionary>'
      self.assertEqual(expected,remove_whitespace_between_tags(xml))
      nv = standard.parseXmlString(xml)
      self.assertEqual(v,nv)


    def test_toXmlStringFile(self):
      v = standard.FileFromData(self.context,data='Hello World!',filename='HelloWorld.txt',content_type='text/plain')
      xml = standard.toXmlString(self.context,v)
      expected = '<data content_type="text/plain" filename="HelloWorld.txt" type="file"><![CDATA[Hello World!]]></data>'
      self.assertEquals(expected,remove_whitespace_between_tags(xml))
      nv = standard.parseXmlString(xml)
      xml = standard.toXmlString(self.context,nv)
      self.assertEquals(expected,remove_whitespace_between_tags(xml))
      
      v = {'a':[standard.FileFromData(self.context,data='Hello World!',filename='HelloWorld.txt',content_type='text/plain')]}
      xml = standard.toXmlString(self.context,v)
      expected = '<dictionary><item key="a" type="list"><list><item type="file"><data content_type="text/plain" filename="HelloWorld.txt" type="file"><![CDATA[Hello World!]]></data></item></list></item></dictionary>'
      self.assertEquals(expected,remove_whitespace_between_tags(xml))
      nv = standard.parseXmlString(xml)
      xml = standard.toXmlString(self.context,nv)
      self.assertEquals(expected,remove_whitespace_between_tags(xml))


    def tearDown(self):
        print(self,"tearDown")
        # super
        ZMSTestCase.tearDown(self)
