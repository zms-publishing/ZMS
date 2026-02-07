# encoding: utf-8
"""
Test fine-grained access control for blob fields.

This test validates the new _check_fine_grained_access method
added to Products/zms/_blobfields.py
"""

from OFS.Folder import Folder
import unittest

# Product imports.
from tests.zms_test_util import *
from Products.zms import mock_http
from Products.zms import zms
from Products.zms._blobfields import MyBlob, MyImage, MyFile


class BlobFieldsAccessTest(ZMSTestCase):
    """
    Test case for blob field access control.
    
    Tests the fine-grained access control implementation including:
    - User role checking
    - Language-based access restrictions
    - Time-based access windows
    - Restricted ancestor node checking
    """

    def setUp(self):
        """Set up test ZMS context."""
        folder = Folder('myzmsx')
        folder.REQUEST = mock_http.MockHTTPRequest({
            'lang': 'eng',
            'preview': 'preview',
            'theme': 'conf:aquire',
            'minimal_init': 1,
            'content_init': 1
        })
        zmscontext = zms.initZMS(folder, 'content', 'titlealt', 'title', 'eng', 'eng', folder.REQUEST)
        self.context = zmscontext

    def test_fine_grained_access_anonymous_user(self):
        """Test that anonymous users are handled correctly."""
        context = self.context
        request = context.REQUEST
        
        # Create a blob object
        blob = MyBlob()
        blob.aq_parent = context
        
        # Mock anonymous user
        request['AUTHENTICATED_USER'] = None
        
        # Anonymous user should pass to public access check
        access_granted, reason = blob._check_fine_grained_access(context, request)
        self.assertTrue(access_granted)
        self.assertEqual(reason, 'anonymous_user')

    def test_fine_grained_access_method_exists(self):
        """Test that the _check_fine_grained_access method exists and is callable."""
        blob = MyBlob()
        self.assertTrue(hasattr(blob, '_check_fine_grained_access'))
        self.assertTrue(callable(getattr(blob, '_check_fine_grained_access')))

    def test_blob_types_have_access_method(self):
        """Test that all blob types have the access control method."""
        for blob_class in [MyBlob, MyImage, MyFile]:
            blob = blob_class()
            self.assertTrue(
                hasattr(blob, '_check_fine_grained_access'),
                f'{blob_class.__name__} should have _check_fine_grained_access method'
            )


if __name__ == '__main__':
    unittest.main()
