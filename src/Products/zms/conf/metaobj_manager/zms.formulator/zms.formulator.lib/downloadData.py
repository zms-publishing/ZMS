import zExceptions
import html
import ftfy

def downloadData(self):
  current_roles = self.getUserRoles(self.REQUEST['AUTHENTICATED_USER'])
  allowed_roles = ['Manager','ZMSAdministrator','ZMSEditor']
  authorized = len(self.intersection_list(current_roles,allowed_roles))>0 and True or False
  if not authorized:
    raise zExceptions.Unauthorized
  else:
    frmu = self.ZMSFormulator(self)
    content_type = 'text/csv; charset=utf-8'
    filename = '"%s_%s_%s.csv"'%(self.getLangStr('TYPE_ZMSFORMULATOR'),frmu.titlealt,frmu.this.getId())
    self.REQUEST.RESPONSE.setHeader('Content-Type',content_type)
    self.REQUEST.RESPONSE.setHeader('Content-Disposition','attachment;filename='+filename)
    self.REQUEST.RESPONSE.setHeader('Cache-Control', 'no-cache')
    self.REQUEST.RESPONSE.setHeader('Pragma', 'no-cache')
    data = frmu.printDataRaw(frmt='csv')
    if (self.REQUEST.get('encode','')=='excel'):
        data = html.unescape(data)
        tab = {'a&#776;':228,'o&#776;':246,'u&#776;':252,'O&#776;':214,'A&#776;':196,'U&#776;':220,'e&#769;':233,'e&#768;':232,
               'e&#770;':234,'a&#768;':224,'a&#770;':226,'o&#768;':242,'o&#770;':244,'u&#768;':249,'u&#770;':251}
        for t in tab:
          if data.find(t) >= 0:
            data = data.replace(t, chr(tab[t]))
        # preserve variants of apostrophes
        data = data.replace('&#39;','\'')
        data = data.replace('&#699;','\'')
        data = data.replace('&#700;','\'')
        data = data.replace('&#750;','\'')
        data = data.replace('&#1370;','\'')
        data = data.replace('&#8216;','\'')
        data = data.replace('&#8217;','\'')
        data = data.replace('&#8218;','\'')
        data = data.replace('&#8219;','\'')
        data = data.replace('&#8249;','\'')
        data = data.replace('&#8250;','\'')
        data = data.replace('&#42891;','\'')
        data = data.replace('&#42892;','\'')
        data = data.replace('&#65287;','\'')
        # preserve variants of quotation marks
        data = data.replace('&#34;','"')
        data = data.replace('&#171;','"')
        data = data.replace('&#187;','"')
        data = data.replace('&#8220;','"')
        data = data.replace('&#8221;','"')
        data = data.replace('&#8222;','"')
        data = data.replace('&#8223;','"')
        data = data.replace('&#12317;','"')
        data = data.replace('&#12318;','"')
        data = data.replace('&#12319;','"')
        data = data.replace('&#65282;','"')
    else:
        data = html.unescape(data)
    return ftfy.fix_text(data)