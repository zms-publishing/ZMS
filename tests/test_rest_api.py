# encoding: utf-8

from OFS.Folder import Folder
import json

# Product imports.
from tests.zms_test_util import *
from Products.zms import rest_api
from Products.zms import standard

# /Products/zms> python -m unittest discover -s unit_tests
# /Products/zms> python -m unittest tests.test_rest_api.RestAPITest
class RestAPITest(ZMSTestCase):

  temp_title = 'temp-test'
  lang = 'eng'

  def setUp(self):
    folder = Folder('site')
    folder.REQUEST = MockHTTPRequest({'lang':'eng','preview':'preview','url':'{$}'})
    self.context = standard.initZMS(folder, 'myzmsx', 'titlealt', 'title', self.lang, self.lang, folder.REQUEST)
    print('[setUp] create %s'%self.temp_title)

  def test_get_rest_api_url(self):
     self.assertEqual("http://foo/++rest_api/bar",rest_api.get_rest_api_url("http://foo/bar"))
     self.assertEqual("http://foo/content/++rest_api/bar",rest_api.get_rest_api_url("http://foo/content/bar"))

  def test_zmsindex(self):
      name = '++rest_api'
      path_to_handle = [name, 'zmsindex']
      request = MockHTTPRequest({'REQUEST_METHOD':'GET','TraversalRequestNameStack':path_to_handle,'path_to_handle':path_to_handle})
      request.form['meta_id'] = 'ZMSDocument'
      print("path_to_handle", request.get('path_to_handle'))
      actual = json.loads( self.context.__bobo_traverse__(request, name)(request))
      print(json.dumps(actual))
      self.assertTrue(isinstance(actual, list))
      self.assertEqual( len(actual), 234)
      request.form['meta_id'] = 'ZMSFolder'
      print("path_to_handle", request.get('path_to_handle'))
      actual = json.loads( self.context.__bobo_traverse__(request, name)(request))
      print(json.dumps(actual))
      self.assertTrue(isinstance(actual, list))
      self.assertEqual( len(actual), 15)

  def test_metaobj_manager(self):
      name = '++rest_api'
      path_to_handle = [name, 'metaobj_manager']
      request = MockHTTPRequest({'REQUEST_METHOD':'GET','TraversalRequestNameStack':path_to_handle,'path_to_handle':path_to_handle})
      print("path_to_handle", request.get('path_to_handle'))
      actual = json.loads( self.context.__bobo_traverse__(request, name)(request))
      print(json.dumps(actual))
      self.assertTrue(isinstance(actual, dict))
      self.assertEqual( len(actual), 38)

  def test_get(self):
    count = 0
    for document in self.context.getTreeNodes(MockHTTPRequest(), 'ZMSDocument'):
        name = '++rest_api'
        for path_to_handle in [list(document.getPhysicalPath()), [name, document.get_uid()]]:
            # multilingual
            request = MockHTTPRequest({'REQUEST_METHOD':'GET','TraversalRequestNameStack':path_to_handle,'path_to_handle':path_to_handle})
            print("path_to_handle", request.get('path_to_handle'))
            actual = json.loads( self.context.__bobo_traverse__(request, name)(request))
            print(json.dumps(actual))
            self.assertEqual( actual['id'], document.id)
            self.assertEqual( actual['meta_id'], 'ZMSDocument')
            self.assertFalse( 'title' in actual)
            self.assertTrue( 'title_%s'%self.lang in actual)
            # monolingual
            request = MockHTTPRequest({'REQUEST_METHOD':'GET','TraversalRequestNameStack':path_to_handle+[self.lang],'path_to_handle':path_to_handle+[self.lang]})
            print("path_to_handle", request.get('path_to_handle'))
            actual = json.loads( self.context.__bobo_traverse__(request, name)(request))
            print(json.dumps(actual))
            self.assertEqual( actual['id'], document.id)
            self.assertEqual( actual['meta_id'], 'ZMSDocument')
            self.assertTrue( 'title' in actual)
            self.assertFalse( 'title_%s'%self.lang in actual)
            # list_parent_nodes
            request = MockHTTPRequest({'REQUEST_METHOD':'GET','TraversalRequestNameStack':path_to_handle+['list_parent_nodes'],'path_to_handle':path_to_handle+['list_parent_nodes']})
            print("path_to_handle", request.get('path_to_handle'))
            actual = json.loads( self.context.__bobo_traverse__(request, name)(request))
            print(json.dumps(actual))
            self.assertEqual( len(actual), len(document.breadcrumbs_obj_path()))
            # list_child_nodes
            request = MockHTTPRequest({'REQUEST_METHOD':'GET','TraversalRequestNameStack':path_to_handle+['list_child_nodes'],'path_to_handle':path_to_handle+['list_child_nodes']})
            print("path_to_handle", request.get('path_to_handle'))
            actual = json.loads( self.context.__bobo_traverse__(request, name)(request))
            print(json.dumps(actual))
            self.assertEqual( len(actual), len(document.getChildNodes(request)))
            # list_tree_nodes
            request = MockHTTPRequest({'REQUEST_METHOD':'GET','TraversalRequestNameStack':path_to_handle+['list_tree_nodes'],'path_to_handle':path_to_handle+['list_tree_nodes']})
            print("path_to_handle", request.get('path_to_handle'))
            actual = json.loads( self.context.__bobo_traverse__(request, name)(request))
            print(json.dumps(actual))
            self.assertEqual( len(actual), len(document.getTreeNodes(request)))
            # get_child_nodes + multilingual
            request = MockHTTPRequest({'REQUEST_METHOD':'GET','TraversalRequestNameStack':path_to_handle+['get_child_nodes'],'path_to_handle':path_to_handle+['get_child_nodes']})
            print("path_to_handle", request.get('path_to_handle'))
            actual = json.loads( self.context.__bobo_traverse__(request, name)(request))
            print(json.dumps(actual))
            self.assertTrue( isinstance( actual, list))
            self.assertEqual( len(actual), len(document.getChildNodes(request)))
            if actual:
                self.assertFalse( 'title' in actual[0])
                self.assertTrue( 'title_%s'%self.lang in actual[0])
            # get_child_nodes + monolingual
            request = MockHTTPRequest({'REQUEST_METHOD':'GET','TraversalRequestNameStack':path_to_handle+['get_child_nodes'],'path_to_handle':path_to_handle+['get_child_nodes', self.lang]})
            print("path_to_handle", request.get('path_to_handle'))
            actual = json.loads( self.context.__bobo_traverse__(request, name)(request))
            print(json.dumps(actual))
            self.assertTrue( isinstance( actual, list))
            self.assertEqual( len(actual), len(document.getChildNodes(request)))
            if actual:
                self.assertTrue( 'title' in actual[0])
                self.assertFalse( 'title_%s'%self.lang in actual[0])
            # get_tree_nodes
            request = MockHTTPRequest({'REQUEST_METHOD':'GET','TraversalRequestNameStack':path_to_handle+['get_tree_nodes'],'path_to_handle':path_to_handle+['get_tree_nodes']})
            print("path_to_handle", request.get('path_to_handle'))
            actual = json.loads( self.context.__bobo_traverse__(request, name)(request))
            print(json.dumps(actual))
            # TODO implement here
        count += 1
    self.assertEqual( 64, count)
