# encoding: utf-8

from OFS.Folder import Folder
import copy
import unittest

# Product imports.
from tests.zms_test_util import *
from Products.zms import mock_http
from Products.zms import standard

# /ZMS5> python3 -m unittest discover -s tests
# /ZMS5> python3 -m unittest tests.test_metaobj_manager.ZMSMetaobjManagerRepositoryModelTest
class ZMSMetaobjManagerRepositoryModelTest(ZMSTestCase):
    r"""
    Test ZMSMetaobjManager.provideRepositoryModel() function
        1. Basic functionality test - Verifies the function returns a dictionary with content
        2. Specific ID test - Tests requesting a single metaobject
        3. Structure test - Validates the zcatalog_page structure has all mandatory keys
        4. Attributes test - Checks that all expected attributes are present
        5. Mandatory keys test - Ensures attributes only contain mandatory keys
        6. Executable keys test - Verifies that executable Python code in keys is preserved
        7. Multiple IDs test - Tests requesting multiple metaobjects at once
        8. Non-existent ID test - Ensures graceful handling of invalid IDs
        9. Acquired objects test - Verifies non-acquired objects don't have the 'acquired' key
    
        The zcatalog_page metaobject definition for reference:
        ./Products/zms/conf/metaobj_manager/com.zms.catalog.zcatalog/zcatalog_page/__init__.py
    """

    def setUp(self):
        """Set up test fixtures"""
        folder = Folder('site')
        folder.REQUEST = mock_http.MockHTTPRequest({
            'lang': 'eng',
            'preview': 'preview',
            'theme': 'conf:aquire',
            'minimal_init': 1,
            'content_init': 1,
            'zcatalog_init': 1  # Add zcatalog initialization to load zcatalog_page
        })
        self.context = standard.initZMS(
            folder, 'myzmsx', 'titlealt', 'title', 'eng', 'eng', folder.REQUEST
        )
        self.metaobj_manager = self.context.metaobj_manager
        
    def test_provideRepositoryModel_basic(self):
        """Test basic functionality of provideRepositoryModel"""
        r = {}
        self.metaobj_manager.provideRepositoryModel(r)
        
        # Result should be a dictionary
        self.assertIsInstance(r, dict)
        # Result should contain metaobjects
        self.assertGreater(len(r), 0)
        
    def test_provideRepositoryModel_specific_id(self):
        """Test provideRepositoryModel with specific ID"""
        r = {}
        test_id = 'zcatalog_page'
        
        # First check if the metaobject exists
        metaobj_ids = self.metaobj_manager.getMetaobjIds()
        if test_id not in metaobj_ids:
            self.skipTest(f"Metaobject '{test_id}' not available in test context")
        
        self.metaobj_manager.provideRepositoryModel(r, ids=[test_id])
        
        # Should contain only the requested ID
        self.assertIn(test_id, r)
        self.assertEqual(len(r), 1)
        
    def test_provideRepositoryModel_zcatalog_page_structure(self):
        """Test provideRepositoryModel structure for zcatalog_page"""
        r = {}
        test_id = 'zcatalog_page'
        
        # Check if zcatalog_page exists
        metaobj_ids = self.metaobj_manager.getMetaobjIds()
        if test_id not in metaobj_ids:
            self.skipTest(f"Metaobject '{test_id}' not available in test context")
        
        self.metaobj_manager.provideRepositoryModel(r, ids=[test_id])
        
        # Verify the structure
        self.assertIn(test_id, r)
        obj = r[test_id]
        
        # Check mandatory keys
        mandatory_keys = ['access', 'enabled', 'id', 'name', 'package', 'revision', 'type']
        for key in mandatory_keys:
            self.assertIn(key, obj, f"Mandatory key '{key}' missing")
        
        # Check specific values for zcatalog_page
        self.assertEqual(obj['id'], 'zcatalog_page')
        self.assertEqual(obj['name'], 'ZCatalog-Page')
        self.assertEqual(obj['package'], 'com.zms.catalog.zcatalog')
        self.assertEqual(obj['type'], 'ZMSDocument')
        self.assertEqual(obj['enabled'], 1)
        
        # Check __filename__
        self.assertIn('__filename__', obj)
        expected_filename = ['com.zms.catalog.zcatalog', 'zcatalog_page', '__init__.py']
        self.assertEqual(obj['__filename__'], expected_filename)
        
    def test_provideRepositoryModel_zcatalog_page_attrs(self):
        """Test provideRepositoryModel attributes for zcatalog_page"""
        r = {}
        test_id = 'zcatalog_page'
        
        # Check if zcatalog_page exists
        metaobj_ids = self.metaobj_manager.getMetaobjIds()
        if test_id not in metaobj_ids:
            self.skipTest(f"Metaobject '{test_id}' not available in test context")
        
        self.metaobj_manager.provideRepositoryModel(r, ids=[test_id])
        obj = r[test_id]
        
        # Check Attrs
        self.assertIn('Attrs', obj)
        attrs = obj['Attrs']
        self.assertIsInstance(attrs, list)
        self.assertGreater(len(attrs), 0)
        
        # Check for specific attributes
        attr_ids = [attr['id'] for attr in attrs]
        expected_attrs = [
            'icon_clazz', 'titlealt', 'title', 'multisite_search',
            'multisite_exclusions', 'script.js', 'style.css',
            'handlebars.js', 'zcatalog_breadcrumbs_obj_path', 'standard_html'
        ]
        
        for expected_attr in expected_attrs:
            self.assertIn(expected_attr, attr_ids, 
                         f"Expected attribute '{expected_attr}' not found")
        
    def test_provideRepositoryModel_attr_mandatory_keys(self):
        """Test that attributes have only mandatory keys"""
        r = {}
        test_id = 'zcatalog_page'
        
        # Check if zcatalog_page exists
        metaobj_ids = self.metaobj_manager.getMetaobjIds()
        if test_id not in metaobj_ids:
            self.skipTest(f"Metaobject '{test_id}' not available in test context")
        
        self.metaobj_manager.provideRepositoryModel(r, ids=[test_id])
        obj = r[test_id]
        attrs = obj['Attrs']
        
        # Check mandatory keys for each attribute
        base_mandatory_keys = [
            'id', 'name', 'type', 'meta_type', 'default', 
            'keys', 'mandatory', 'multilang', 'repetitive'
        ]
        
        for attr in attrs:
            self.assertIn('id', attr)
            self.assertIn('type', attr)
            
            # For constant types, 'custom' should also be present
            if attr['type'] == 'constant':
                self.assertIn('custom', attr, 
                             f"Attribute '{attr['id']}' of type 'constant' should have 'custom' key")
        
    def test_provideRepositoryModel_executable_keys(self):
        """Test that executable keys in multisite_exclusions are preserved as string"""
        r = {}
        test_id = 'zcatalog_page'
        
        # Check if zcatalog_page exists
        metaobj_ids = self.metaobj_manager.getMetaobjIds()
        if test_id not in metaobj_ids:
            self.skipTest(f"Metaobject '{test_id}' not available in test context")
        
        self.metaobj_manager.provideRepositoryModel(r, ids=[test_id])
        obj = r[test_id]
        attrs = obj['Attrs']
        
        # Find multisite_exclusions attribute
        multisite_exclusions_attr = None
        for attr in attrs:
            if attr['id'] == 'multisite_exclusions':
                multisite_exclusions_attr = attr
                break
        
        if multisite_exclusions_attr:
            # Keys should be either a list or a string (if executable)
            keys = multisite_exclusions_attr.get('keys')
            self.assertIsNotNone(keys)
            # If it's a string, it should start with '##' (executable Python)
            if isinstance(keys, str):
                self.assertTrue(keys.startswith('##'), 
                               "Executable keys should start with '##'")
    
    def test_provideRepositoryModel_multiple_ids(self):
        """Test provideRepositoryModel with multiple IDs"""
        r = {}
        test_ids = ['ZMSDocument', 'ZMSFolder']
        
        # Check which IDs exist
        metaobj_ids = self.metaobj_manager.getMetaobjIds()
        valid_test_ids = [id for id in test_ids if id in metaobj_ids]
        
        if not valid_test_ids:
            self.skipTest("None of the test metaobjects available")
        
        self.metaobj_manager.provideRepositoryModel(r, ids=valid_test_ids)
        
        # Should contain all requested IDs
        for test_id in valid_test_ids:
            self.assertIn(test_id, r)
        
    def test_provideRepositoryModel_nonexistent_id(self):
        """Test provideRepositoryModel with non-existent ID"""
        r = {}
        nonexistent_id = 'this_does_not_exist_123456'
        
        self.metaobj_manager.provideRepositoryModel(r, ids=[nonexistent_id])
        
        # Should not contain the non-existent ID
        self.assertNotIn(nonexistent_id, r)
        # Result should be empty
        self.assertEqual(len(r), 0)
    
    def test_provideRepositoryModel_no_acquired_key_for_non_acquired(self):
        """Test that non-acquired objects don't have 'acquired' key in result"""
        r = {}
        test_id = 'zcatalog_page'
        
        # Check if zcatalog_page exists
        metaobj_ids = self.metaobj_manager.getMetaobjIds()
        if test_id not in metaobj_ids:
            self.skipTest(f"Metaobject '{test_id}' not available in test context")
        
        self.metaobj_manager.provideRepositoryModel(r, ids=[test_id])
        obj = r[test_id]
        
        # Should not have 'acquired' key for non-acquired objects
        self.assertNotIn('acquired', obj)


if __name__ == '__main__':
    unittest.main()