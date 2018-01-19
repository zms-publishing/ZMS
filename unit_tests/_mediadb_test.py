# encoding: utf-8

from App.ImageFile import ImageFile
import _mediadb
import inspect
import os
import tempfile
import shutil
import unittest
import sys
sys.path.append("..")

# /Products/zms> python -m unittest unit_tests._mediadb_test.MediaDbTest
class MediaDbTest(unittest.TestCase):

    def setUp(self):
        print(self,"setUp")
        self.tempfolder = tempfile.mktemp()
        os.makedirs(self.tempfolder)
        self.mediadb = _mediadb.MediaDb(self.tempfolder)

    def tearDown(self):
        print(self,"tearDown")
        shutil.rmtree(self.tempfolder)  

    def test_getLocation(self):
        print(self,"test_getLocation")
        self.assertEqual( self.mediadb.getLocation(), self.tempfolder)

    def test_getStructure(self):
        print(self,"test_getStructure")
        self.assertEqual( self.mediadb.getStructure(), 0)

    def test_targetFile(self):
        print(self,"test_targetFile")
        filename = "acl_mediadb.png"
        filepath = "../plugins/www/img/%s"%filename
        targetfile = self.mediadb.targetFile(filepath)
        self.assertEqual(targetfile,os.path.join(self.tempfolder,filename))

    def test_storeFile(self):
        print(self,"test_storeFile")
        filepath = "../plugins/www/img/acl_mediadb.png"
        modulepath = list(os.path.split(inspect.getfile(self.__class__))[:-1])
        file = open(os.path.join(modulepath)+os.sep+filepath,"rb")
        filedata = file.read()
        file.close()
        image = ImageFile(filepath,globals())
        image.filename = filepath
        mediadb_filename = self.mediadb.storeFile(image)
        filename, fileext = os.path.splitext(mediadb_filename)
        self.assertTrue( filename.startswith("acl_mediadb_"))
        self.assertEqual( fileext, ".png")
        data = self.mediadb.retrieveFile(mediadb_filename)
        self.assertEqual(filedata,data)

if __name__ == '__main__':
    unittest.main()
