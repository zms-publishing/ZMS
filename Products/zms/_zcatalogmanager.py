"""
_zcatalogmanager.py - ZMS Catalog Manager for Search Query Formatting and Object Traversal

Provides ZCatalogManager for catalog indexing. It centralizes manager 
methods for catalog indexing, connector integration, and search-facing 
metadata, keeping administrative logic in one place and reducing duplication
in callers.

License: GNU General Public License v2 or later,
Organization: ZMS Publishing
"""


class ZCatalogManager(object):
    """
    Provide catalog utility methods for search query formatting and object traversal.
    
    Includes helpers for building catalog search query strings with AND/OR operators,
    executing catalog queries, and resolving catalog object paths for ZMS objects.
    """

    # @deprecated
    def getCatalogQueryString(self, raw, option='AND', only_words=False):
      qs = []
      i = 0
      for si in raw.split('"'):
        si = si.strip()
        if si:
          if i % 2 == 0:
            for raw_item in si.split(' '):
              raw_item = raw_item.strip()
              if len(raw_item) > 1 and not raw_item.upper() in ['AND', 'OR']:
                raw_item = raw_item.replace('-', '* AND *')
                if not only_words and not raw_item.endswith('*'):
                  raw_item += '*'
                if raw_item not in qs:
                  qs.append( raw_item)
          else:
            raw_item = '"%s"'%si
            if raw_item not in qs:
              qs.append( raw_item)
        i += 1
      return (' %s '%option).join([x for x in qs if x.strip()])


    # @deprecated
    def getCatalogPathObject(self, path):
      ob = self.getHome()
      l = path.split( '/')
      if ob.id not in l:
        docElmnt = self.getDocumentElement()
        if docElmnt.id not in l:
          ob = docElmnt
      else:
        l = l[ l.index(ob.id)+1:]
      for id in l:
         if len( id) > 0 and ob is not None:
          ob = getattr(ob, id, None)
      return ob


    # @deprecated
    def submitCatalogQuery(self, search_query, search_order_by, search_meta_types=[], search_clients=False, REQUEST=None):
      return self.getCatalogAdapter().search(search_query, search_order_by)

