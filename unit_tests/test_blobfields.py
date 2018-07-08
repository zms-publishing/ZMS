# encoding: utf-8

from App.ImageFile import ImageFile
import sys
import unittest
sys.path.append("..")
# Product imports.
from zms_test_util import *
import _blobfields

# /Products/zms> python -m unittest discover -s unit_tests
# /Products/zms> python -m unittest unit_tests.test_blobfields.BlobfieldsTest
class BlobfieldsTest(ZMSTestCase):

    def test_getDataURI(self):
        print(self,"test_getDataURI")
        filepath = "../plugins/www/img/acl_mediadb.png"
        modulepath = os.sep.join(inspect.getfile(self.__class__).split(os.sep)[:-1])
        file = open(os.path.join(modulepath,filepath),"rb")
        filedata = file.read()
        file.close()
        blob = _blobfields.createBlobField(self.context,_blobfields.MyImage,filedata)
        dataURI = blob.getDataURI()
        self.assertTrue(dataURI.startswith('data:image/png;base64,'))
        self.assertEqual(622,len(dataURI))
        blob2 = _blobfields.createBlobField(self.context,_blobfields.MyImage,dataURI)
        dataURI2 = blob2.getDataURI()
        self.assertEqual(dataURI,dataURI2)

if __name__ == '__main__':
    unittest.main()
