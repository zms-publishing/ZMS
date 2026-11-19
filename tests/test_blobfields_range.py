# encoding: utf-8

"""
Unit test for HTTP range requests on blobs (MyBlob._range_request_handler).

If the site uses a MediaDB, on_setobjattr() moves the file content into the
MediaDB and sets self.data to ''. A range request must still answer with the
requested bytes and not with an empty 206 response.

No ZMS instance is needed: the blob, its parent and the MediaDB are stubbed.
"""

import unittest

# Product imports.
from Products.zms import _blobfields


DATA = bytes(range(256)) * 4  # 1024 bytes


class MockMediaDb(object):

  def __init__(self, files):
    self.files = files

  def retrieveFile(self, filename):
    return self.files[filename]


class MockParent(object):

  _p_mtime = 1700000000.0

  def __init__(self, mediadb=None):
    self.mediadb = mediadb

  def getMediaDb(self):
    return self.mediadb


class MockRequest(object):

  def __init__(self, headers):
    self.headers = headers

  def get_header(self, name, default=None):
    return self.headers.get(name, default)


class MockResponse(object):

  def __init__(self):
    self.headers = {}
    self.status = 200
    self.body = b''

  def setHeader(self, name, value):
    self.headers[name] = value

  def setStatus(self, status):
    self.status = status

  def write(self, data):
    if isinstance(data, str):
      data = data.encode('latin-1')
    self.body += data


class Blob(_blobfields.MyBlob):

  content_type = 'image/png'

  def __init__(self, data, mediadbfile=None, parent=None):
    self.data = data
    self.size = len(DATA)
    self.mediadbfile = mediadbfile
    self.aq_parent = parent

  def getMediadbfile(self):
    return self.mediadbfile


# /ZMS> python3 -m unittest tests.test_blobfields_range
class BlobRangeRequestTest(unittest.TestCase):

  def _blob(self, mediadb):
    if mediadb:
      parent = MockParent(MockMediaDb({'image.png': DATA}))
      # Content moved to the MediaDB, see MyBlob.on_setobjattr.
      return Blob('', mediadbfile='image.png', parent=parent)
    return Blob(DATA, parent=MockParent())

  def _get(self, blob, range_header):
    response = MockResponse()
    served = blob._range_request_handler(MockRequest({'Range': range_header}), response)
    return served, response

  def test_single_range_zodb(self):
    served, response = self._get(self._blob(mediadb=False), 'bytes=100-199')
    self.assertTrue(served)
    self.assertEqual(206, response.status)
    self.assertEqual(DATA[100:200], response.body)

  def test_single_range_mediadb(self):
    served, response = self._get(self._blob(mediadb=True), 'bytes=100-199')
    self.assertTrue(served)
    self.assertEqual(206, response.status)
    self.assertEqual(100, response.headers['Content-Length'])
    self.assertEqual(DATA[100:200], response.body)

  def test_multiple_ranges_mediadb(self):
    served, response = self._get(self._blob(mediadb=True), 'bytes=0-9,500-509')
    self.assertTrue(served)
    self.assertEqual(206, response.status)
    self.assertIn(b'\r\n\r\n' + DATA[0:10] + b'\r\n--', response.body)
    self.assertIn(b'\r\n\r\n' + DATA[500:510] + b'\r\n--', response.body)


if __name__ == '__main__':
  unittest.main()
