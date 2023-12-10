from Products.zms import standard

def zcatalog_suggest(self, REQUEST=None):
  request = self.REQUEST
  q = request.get('q','')
  limit = int(REQUEST.get('limit',5))
  lang = standard.nvl(request.get('lang'), self.getPrimaryLanguage())
  root = self.getRootElement()
  zcatalog = getattr(root, 'catalog_%s'%lang)
  
  # Find suggest-results.
  rtn = []
  lexicon = zcatalog.Lexicon
  ### All word
  # rtn = [x for x in list(lexicon.words()) if x.lower().find(q.lower())>=0]
  ### Filter/limit words
  for w in list(lexicon.words()):
    if (w[0] not in ['_', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']) and (w.lower().find(q.lower()) >= 0) and (w not in rtn):
      rtn.append(w)
    if len(rtn) >= limit:
      break

  # Return list of suggestions.
  return rtn