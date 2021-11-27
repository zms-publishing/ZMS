def getJSONSchema(self):
  frmu = self.ZMSFormulator(self)
  jsed = self.JSONEditor(frmu)
  self.REQUEST.RESPONSE.setHeader('Cache-Control', 'no-cache')
  self.REQUEST.RESPONSE.setHeader('Pragma', 'no-cache')
  return jsed.getSchema()