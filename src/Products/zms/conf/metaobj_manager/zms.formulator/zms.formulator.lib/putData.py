def putData(self):

  # Workaround: adding language for forms existing only in a secondary language
  #print "### ", self.REQUEST.form.get('LANG', 'foo')
  self.REQUEST.set('lang',self.REQUEST.form.get('LANG', self.getPrimaryLanguage()))

  frmu = self.ZMSFormulator(self)
  res = frmu.receiveData()
  self.REQUEST.RESPONSE.setHeader('Cache-Control', 'no-cache')
  self.REQUEST.RESPONSE.setHeader('Pragma', 'no-cache')
  self.REQUEST.RESPONSE.setHeader('Content-Type','text/html; charset=utf-8')
  if res:
    return 'OK'
  else:
    return 'NOK'