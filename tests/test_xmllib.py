from Products.zms import standard
import test_util

def remove_whitespace_between_tags(xml):
  import re
  xml = re.sub('>(\\s+?)<','><',xml).strip()
  return xml

class XmlUtilTest(test_util.BaseTest):

  def test_toXmlString(self):

    v = {'a':1,'b':2,'c':'XXX','d':'YYY'}
    xml = standard.toXmlString(self.context,v)
    expected = '<dictionary><item key="a" type="int">1</item><item key="b" type="int">2</item><item key="c"><![CDATA[XXX]]></item><item key="d"><![CDATA[YYY]]></item></dictionary>'
    self.assertEquals('standard.toXmlString(dict)',expected,remove_whitespace_between_tags(xml))
    nv = standard.parseXmlString(xml)
    self.assertEquals('standard.parseXml(dict)',v,nv)

    v = ['a',1,'b',2]
    xml = standard.toXmlString(self.context,v)
    expected = '<list><item><![CDATA[a]]></item><item type="int">1</item><item><![CDATA[b]]></item><item type="int">2</item></list>'
    self.assertEquals('standard.toXmlString(list)',expected,remove_whitespace_between_tags(xml))
    nv = standard.parseXmlString(xml)
    self.assertEquals('standard.parseXml(list)',v,nv)

    v = ['a',{'b':2},1]
    xml = standard.toXmlString(self.context,v)
    expected = '<list><item><![CDATA[a]]></item><item type="dictionary"><dictionary><item key="b" type="int">2</item></dictionary></item><item type="int">1</item></list>'
    self.assertEquals('standard.toXmlString(list(dict))',expected,remove_whitespace_between_tags(xml))
    nv = standard.parseXmlString(xml)
    self.assertEquals('standard.parseXml(list(dict))',v,nv)

    v = {'a':['b',2],'c':1}
    xml = standard.toXmlString(self.context,v)
    expected = '<dictionary><item key="a" type="list"><list><item><![CDATA[b]]></item><item type="int">2</item></list></item><item key="c" type="int">1</item></dictionary>'
    self.assertEquals('standard.toXmlString(dict(list))',expected,remove_whitespace_between_tags(xml))
    nv = standard.parseXmlString(xml)
    self.assertEquals('standard.parseXml(dict(list))',v,nv)

    v = standard.FileFromData(self.context,data='Hello World!',filename='HelloWorld.txt',content_type='text/plain')
    xml = standard.toXmlString(self.context,v)
    expected = '<data content_type="text/plain" filename="HelloWorld.txt" type="file"><![CDATA[Hello World!]]></data>'
    self.assertEquals('standard.toXmlString(MyFile)',expected,remove_whitespace_between_tags(xml))
    nv = standard.parseXmlString(xml)
    self.assertEquals('standard.parseXml(MyFile)',v,nv)

    v = {'a':[standard.FileFromData(self.context,data='Hello World!',filename='HelloWorld.txt',content_type='text/plain')]}
    xml = standard.toXmlString(self.context,v)
    expected = '<dictionary><item key="a" type="list"><list><item type="file"><data content_type="text/plain" filename="HelloWorld.txt" type="file"><![CDATA[Hello World!]]></data></item></list></item></dictionary>'
    self.assertEquals('standard.toXmlString(dict(list(MyFile)))',expected,remove_whitespace_between_tags(xml))
    nv = standard.parseXmlString(xml)
    self.assertEquals('standard.parseXml(dict(list(MyFile)))',v,nv)
