# encoding: utf-8

from OFS.Folder import Folder
import json

# Product imports.
from tests.zms_test_util import *
from Products.zms import mock_http
from Products.zms import rest_api
from Products.zms import standard

# /Products/zms> python -m unittest discover -s unit_tests
# /Products/zms> python -m unittest tests.test_rest_api.RestAPITest
class RestAPITest(ZMSTestCase):

  temp_title = 'temp-test'
  lang = 'eng'

  def setUp(self):
    folder = Folder('site')
    folder.REQUEST = mock_http.MockHTTPRequest({'lang':'eng','preview':'preview','url':'{$}'})
    self.context = standard.initZMS(folder, 'myzmsx', 'titlealt', 'title', self.lang, self.lang, folder.REQUEST)
    print('[setUp] create %s'%self.temp_title)
    zmsindex = self.context.getZMSIndex()
    self.assertIsNotNone(zmsindex)
    zmsindex.manage_reindex(regenerate_all=True)

  def test_get_rest_api_url(self):
     self.assertEqual("http://foo/++rest_api/bar",rest_api.get_rest_api_url("http://foo/bar"))
     self.assertEqual("http://foo/content/++rest_api/bar",rest_api.get_rest_api_url("http://foo/content/bar"))

  def test_zmsindex(self):
      name = '++rest_api'
      path_to_handle = [name, 'zmsindex']
      request = mock_http.MockHTTPRequest({'REQUEST_METHOD':'GET','TraversalRequestNameStack':path_to_handle,'path_to_handle':path_to_handle})
      request.form['meta_id'] = 'ZMSDocument'
      print("path_to_handle", request.get('path_to_handle'))
      actual = json.loads( self.context.__bobo_traverse__(request, name)(request))
      print(json.dumps(actual))
      self.assertTrue(isinstance(actual, list))
      self.assertEqual( 106, len(actual))
      request.form['meta_id'] = 'ZMSFolder'
      print("path_to_handle", request.get('path_to_handle'))
      actual = json.loads( self.context.__bobo_traverse__(request, name)(request))
      print(json.dumps(actual))
      self.assertTrue(isinstance(actual, list))
      self.assertEqual( 7, len(actual))

  def test_metaobj_manager(self):
      name = '++rest_api'
      path_to_handle = [name, 'metaobj_manager']
      request = mock_http.MockHTTPRequest({'REQUEST_METHOD':'GET','TraversalRequestNameStack':path_to_handle,'path_to_handle':path_to_handle})
      print("path_to_handle", request.get('path_to_handle'))
      actual = json.loads( self.context.__bobo_traverse__(request, name)(request))
      print(json.dumps(actual))
      self.assertTrue(isinstance(actual, dict))
      self.assertEqual( len(actual), 39)

  def test_headless_get(self):
      count = 0
      for document in self.context.getTreeNodes(mock_http.MockHTTPRequest(), 'ZMSDocument'):
          headless = rest_api.RestApiController()
          # multilingual
          actual = headless.get(document)
          print("headless:actual",actual)
          self.assertTrue(isinstance(actual, dict))
          self.assertEqual( actual['meta_id'], 'ZMSDocument')
          # list_child_nodes
          actual = headless.list_child_nodes(document)
          self.assertTrue(isinstance(actual, list))
          #
          count += 1
      self.assertEqual( 64, count)

  def test_get(self):
    count = 0
    for document in self.context.getTreeNodes(mock_http.MockHTTPRequest(), 'ZMSDocument'):
        name = '++rest_api'
        for path_to_handle in [list(document.getPhysicalPath()), [name, document.get_uid()]]:
            # multilingual
            self.context.REQUEST = mock_http.MockHTTPRequest({'REQUEST_METHOD':'GET','TraversalRequestNameStack':path_to_handle,'path_to_handle':path_to_handle})
            print("multilingual:path_to_handle", self.context.REQUEST.get('path_to_handle'))
            actual = json.loads( self.context.__bobo_traverse__(self.context.REQUEST, name)(self.context.REQUEST))
            print("multilingual:actual",json.dumps(actual))
            self.assertEqual( actual['id'], document.id)
            self.assertEqual( actual['meta_id'], 'ZMSDocument')
            self.assertFalse( 'title' in actual)
            self.assertTrue( 'title_%s'%self.lang in actual)
            # monolingual
            self.context.REQUEST = mock_http.MockHTTPRequest({'REQUEST_METHOD':'GET','TraversalRequestNameStack':path_to_handle,'path_to_handle':path_to_handle})
            self.context.REQUEST.set('lang',self.lang)
            print("monolingual:path_to_handle", self.context.REQUEST.get('path_to_handle'))
            actual = json.loads( self.context.__bobo_traverse__(self.context.REQUEST, name)(self.context.REQUEST))
            print("monolingual:actual",json.dumps(actual))
            self.assertEqual( actual['id'], document.id)
            self.assertEqual( actual['meta_id'], 'ZMSDocument')
            self.assertTrue( 'title' in actual)
            self.assertFalse( 'title_%s'%self.lang in actual)
            # list_parent_nodes
            self.context.REQUEST = mock_http.MockHTTPRequest({'REQUEST_METHOD':'GET','TraversalRequestNameStack':path_to_handle+['list_parent_nodes'],'path_to_handle':path_to_handle+['list_parent_nodes']})
            print("path_to_handle", self.context.REQUEST.get('path_to_handle'))
            actual = json.loads( self.context.__bobo_traverse__(self.context.REQUEST, name)(self.context.REQUEST))
            print(json.dumps(actual))
            self.assertEqual( len(actual), len(document.breadcrumbs_obj_path()))
            # list_child_nodes
            self.context.REQUEST = mock_http.MockHTTPRequest({'REQUEST_METHOD':'GET','TraversalRequestNameStack':path_to_handle+['list_child_nodes'],'path_to_handle':path_to_handle+['list_child_nodes']})
            print("path_to_handle", self.context.REQUEST.get('path_to_handle'))
            actual = json.loads( self.context.__bobo_traverse__(self.context.REQUEST, name)(self.context.REQUEST))
            print(json.dumps(actual))
            self.assertEqual( len(actual), len(document.getChildNodes(self.context.REQUEST)))
            self.assertEqual( len(actual), len(document.getChildNodes(self.context.REQUEST)))
            # list_tree_nodes
            self.context.REQUEST = mock_http.MockHTTPRequest({'REQUEST_METHOD':'GET','TraversalRequestNameStack':path_to_handle+['list_tree_nodes'],'path_to_handle':path_to_handle+['list_tree_nodes']})
            print("path_to_handle", self.context.REQUEST.get('path_to_handle'))
            actual = json.loads( self.context.__bobo_traverse__(self.context.REQUEST, name)(self.context.REQUEST))
            print(json.dumps(actual))
            self.assertEqual( len(actual), len(document.getTreeNodes(self.context.REQUEST)))
            # get_child_nodes + multilingual
            self.context.REQUEST = mock_http.MockHTTPRequest({'REQUEST_METHOD':'GET','TraversalRequestNameStack':path_to_handle+['get_child_nodes'],'path_to_handle':path_to_handle+['get_child_nodes']})
            print("path_to_handle", self.context.REQUEST.get('path_to_handle'))
            actual = json.loads( self.context.__bobo_traverse__(self.context.REQUEST, name)(self.context.REQUEST))
            print(json.dumps(actual))
            self.assertTrue( isinstance( actual, list))
            self.assertEqual( len(actual), len(document.getChildNodes(self.context.REQUEST)))
            self.assertEqual( len(actual), len(document.getChildNodes(self.context.REQUEST)))
            if actual:
                self.assertFalse( 'title' in actual[0])
                self.assertTrue( 'title_%s'%self.lang in actual[0])
            # get_child_nodes + monolingual
            self.context.REQUEST = mock_http.MockHTTPRequest({'REQUEST_METHOD':'GET','TraversalRequestNameStack':path_to_handle+['get_child_nodes'],'path_to_handle':path_to_handle+['get_child_nodes']})
            self.context.REQUEST.set('lang',self.lang)
            print("path_to_handle", self.context.REQUEST.get('path_to_handle'))
            actual = json.loads( self.context.__bobo_traverse__(self.context.REQUEST, name)(self.context.REQUEST))
            print(json.dumps(actual))
            self.assertTrue( isinstance( actual, list))
            self.assertEqual( len(actual), len(document.getChildNodes(self.context.REQUEST)))
            self.assertEqual( len(actual), len(document.getChildNodes(self.context.REQUEST)))
            if actual:
                self.assertTrue( 'title' in actual[0])
                self.assertFalse( 'title_%s'%self.lang in actual[0])
            # get_tree_nodes
            self.context.REQUEST = mock_http.MockHTTPRequest({'REQUEST_METHOD':'GET','TraversalRequestNameStack':path_to_handle+['get_tree_nodes'],'path_to_handle':path_to_handle+['get_tree_nodes']})
            print("path_to_handle", self.context.REQUEST.get('path_to_handle'))
            actual = json.loads( self.context.__bobo_traverse__(self.context.REQUEST, name)(self.context.REQUEST))
            print(json.dumps(actual))
            # TODO implement here
        #
        count += 1
    self.assertEqual( 64, count)
