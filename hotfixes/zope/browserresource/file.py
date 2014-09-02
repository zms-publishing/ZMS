##############################################################################
#
# Copyright (c) 2002 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""File-based browser resources.
"""

import os
import time
import re
try:
    from email.utils import formatdate, parsedate_tz, mktime_tz
except ImportError: # python 2.4
    from email.Utils import formatdate, parsedate_tz, mktime_tz

from zope.contenttype import guess_content_type
from zope.interface import implementer, provider
from zope.component import adapter, getMultiAdapter
from zope.publisher.browser import BrowserView
from zope.publisher.interfaces import NotFound
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IBrowserPublisher

from zope.browserresource.resource import Resource
from zope.browserresource.interfaces import IETag
from zope.browserresource.interfaces import IFileResource
from zope.browserresource.interfaces import IResourceFactory
from zope.browserresource.interfaces import IResourceFactoryFactory


ETAG_RX = re.compile(r'[*]|(?:W/)?"(?:[^"\\]|[\\].)*"')


def parse_etags(value):
    r"""Parse a list of entity tags.

    HTTP/1.1 specifies the following syntax for If-Match/If-None-Match
    headers::

        If-Match = "If-Match" ":" ( "*" | 1#entity-tag )
        If-None-Match = "If-None-Match" ":" ( "*" | 1#entity-tag )

        entity-tag = [ weak ] opaque-tag

        weak       = "W/"
        opaque-tag = quoted-string

        quoted-string  = ( <"> *(qdtext) <"> )
        qdtext         = <any TEXT except <">>

        The backslash character ("\") may be used as a single-character
        quoting mechanism only within quoted-string and comment constructs.

    Examples:

        >>> parse_etags('*')
        ['*']

        >>> parse_etags(r' "qwerty", ,"foo",W/"bar" , "baz","\""')
        ['"qwerty"', '"foo"', 'W/"bar"', '"baz"', '"\\""']

    Ill-formed headers are ignored

        >>> parse_etags("not an etag at all")
        []

    """
    return ETAG_RX.findall(value)


def etag_matches(etag, tags):
    """Check if the entity tag matches any of the given tags.

        >>> etag_matches('"xyzzy"', ['"abc"', '"xyzzy"', 'W/"woof"'])
        True

        >>> etag_matches('"woof"', ['"abc"', 'W/"woof"'])
        False

        >>> etag_matches('"xyzzy"', ['*'])
        True

    Note that you pass quoted etags in both arguments!
    """
    for tag in tags:
        if tag == etag or tag == '*':
            return True
    return False


def quote_etag(etag):
    r"""Quote an etag value

        >>> quote_etag("foo")
        '"foo"'

    Special characters are escaped

        >>> quote_etag('"')
        '"\\""'
        >>> quote_etag('\\')
        '"\\\\"'

    """
    return '"%s"' % etag.replace('\\', '\\\\').replace('"', '\\"')


class File(object):

    def __init__(self, path, name):
        self.path = path
        self.__name__ = name
        f = open(path, 'rb')
        self.data = f.read()
        f.close()
        self.content_type = guess_content_type(path, self.data)[0]

        self.lmt = float(os.path.getmtime(path)) or time.time()
        self.lmh = formatdate(self.lmt, usegmt=True)


@implementer(IFileResource, IBrowserPublisher)
class FileResource(BrowserView, Resource):

    cacheTimeout = 86400

    def publishTraverse(self, request, name):
        '''File resources can't be traversed further, so raise NotFound if
        someone tries to traverse it.

          >>> factory = FileResourceFactory(testFilePath, nullChecker, 'test.txt')
          >>> request = TestRequest()
          >>> resource = factory(request)
          >>> resource.publishTraverse(request, '_testData')
          Traceback (most recent call last):
          ...
          NotFound: Object: None, name: '_testData'

        '''
        raise NotFound(None, name)

    def browserDefault(self, request):
        '''Return a callable for processing browser requests.

          >>> factory = FileResourceFactory(testFilePath, nullChecker, 'test.txt')
          >>> request = TestRequest(REQUEST_METHOD='GET')
          >>> resource = factory(request)
          >>> view, next = resource.browserDefault(request)
          >>> view() == open(testFilePath, 'rb').read()
          True
          >>> next == ()
          True

          >>> request = TestRequest(REQUEST_METHOD='HEAD')
          >>> resource = factory(request)
          >>> view, next = resource.browserDefault(request)
          >>> view() == b''
          True
          >>> next == ()
          True

        '''
        return getattr(self, request.method), ()

    def chooseContext(self):
        '''Choose the appropriate context.

        This method can be overriden in subclasses, that need to choose
        appropriate file, based on current request or other condition,
        like, for example, i18n files.

        '''
        return self.context

    def GET(self):
        '''Return a file data for downloading with GET requests

          >>> factory = FileResourceFactory(testFilePath, nullChecker, 'test.txt')
          >>> request = TestRequest()
          >>> resource = factory(request)
          >>> resource.GET() == open(testFilePath, 'rb').read()
          True
          >>> request.response.getHeader('Content-Type') == 'text/plain'
          True

        '''

        file = self.chooseContext()
        request = self.request
        response = request.response

        etag = getMultiAdapter((self, request), IETag)(file.lmt, file.data)

        setCacheControl(response, self.cacheTimeout)

        can_return_304 = False
        all_cache_checks_passed = True

        # HTTP If-Modified-Since header handling. This is duplicated
        # from OFS.Image.Image - it really should be consolidated
        # somewhere...
        header = request.getHeader('If-Modified-Since', None)
        if header is not None:
            can_return_304 = True
            header = header.split(';')[0]
            # Some proxies seem to send invalid date strings for this
            # header. If the date string is not valid, we ignore it
            # rather than raise an error to be generally consistent
            # with common servers such as Apache (which can usually
            # understand the screwy date string as a lucky side effect
            # of the way they parse it).
            try:
                mod_since = int(mktime_tz(parsedate_tz(header)))
            except (ValueError, TypeError):
                mod_since = None
            if getattr(file, 'lmt', None):
                last_mod = int(file.lmt)
            else:
                last_mod = 0
            if mod_since is None or last_mod <= 0 or last_mod > mod_since:
                all_cache_checks_passed = False

        # HTTP If-None-Match header handling
        header = request.getHeader('If-None-Match', None)
        if header is not None:
            can_return_304 = True
            tags = parse_etags(header)
            if not etag or not etag_matches(quote_etag(etag), tags):
                all_cache_checks_passed = False

        # 304 responses MUST contain ETag, if one would've been sent with
        # a 200 response
        if etag:
            response.setHeader('ETag', quote_etag(etag))

        if can_return_304 and all_cache_checks_passed:
            response.setStatus(304)
            return b''

        # 304 responses SHOULD NOT or MUST NOT include other entity headers,
        # depending on whether the conditional GET used a strong or a weak
        # validator.  We only use strong validators, which makes it SHOULD
        # NOT.
        response.setHeader('Content-Type', file.content_type)
        response.setHeader('Last-Modified', file.lmh)

        return file.data

    def HEAD(self):
        '''Return proper headers and no content for HEAD requests

          >>> factory = FileResourceFactory(testFilePath, nullChecker, 'test.txt')
          >>> request = TestRequest()
          >>> resource = factory(request)
          >>> resource.HEAD() == b''
          True
          >>> request.response.getHeader('Content-Type') == 'text/plain'
          True

        '''
        file = self.chooseContext()
        etag = getMultiAdapter((self, self.request), IETag)(file.lmt, file.data)
        response = self.request.response
        response.setHeader('Content-Type', file.content_type)
        response.setHeader('Last-Modified', file.lmh)
        if etag:
            response.setHeader('ETag', etag)
        setCacheControl(response, self.cacheTimeout)
        return b''

    # for unit tests
    def _testData(self):
        f = open(self.context.path, 'rb')
        data = f.read()
        f.close()
        return data


@adapter(IFileResource, IBrowserRequest)
@implementer(IETag)
class FileETag(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, mtime, content):
        return '%s-%s' % (mtime, len(content))


def setCacheControl(response, secs=86400):
    # Cache for one day by default
    response.setHeader('Cache-Control', 'public,max-age=%s' % secs)
    t = time.time() + secs
    response.setHeader('Expires', formatdate(t, usegmt=True))


@implementer(IResourceFactory)
@provider(IResourceFactoryFactory)
class FileResourceFactory(object):

    resourceClass = FileResource

    def __init__(self, path, checker, name):
        self.__file = File(path, name)
        self.__checker = checker
        self.__name = name

    def __call__(self, request):
        resource = self.resourceClass(self.__file, request)
        resource.__Security_checker__ = self.__checker
        resource.__name__ = self.__name
        return resource
