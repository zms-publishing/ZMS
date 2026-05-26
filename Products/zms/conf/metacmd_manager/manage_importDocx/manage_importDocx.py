#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import re
import shutil
import tempfile
from xml.dom import minidom
from Products.zms import _fileutil

def manage_importDocx( self):
  request = self.REQUEST
  
  if request.get('btn')==self.getZMILangStr('BTN_IMPORT'):
    def getTextContent(cells):
        rc = []
        for cell in cells:
          for node in cell.childNodes:
              if node.nodeType in [node.TEXT_NODE,node.CDATA_SECTION_NODE]:
                  nd = node.data
                  rc.append(nd)
        return ''.join(rc).strip()
    result = []
    tempfolder = tempfile.mkdtemp()
    f = request['file']
    filename = os.path.join(tempfolder,f.filename)
    _fileutil.exportObj(f,filename)
    _fileutil.extractZipArchive(filename)
    document = minidom.parse(os.path.join(tempfolder,'word','document.xml'))
    for wpNode in document.getElementsByTagName("w:p"):
      for wrNode in wpNode.getElementsByTagName("w:r"):
        for wtNode in wrNode.getElementsByTagName("w:t"):
          result.append(getTextContent([wtNode]))
    shutil.rmtree(tempfolder)
    result.append('imported to %s'%tempfolder)
    return '\n'.join(result)
  
  html = ''
  html += '<!DOCTYPE html>'
  html += '<html lang="en">'
  html += self.zmi_html_head(self,request)
  html += '<body class="%s">'%(' '.join(['zmi',request['lang'],self.meta_id]))
  html += self.zmi_body_header(self,request,options=[{'action':'#','label':'Import DOCX...'}])
  html += '<div id="zmi-tab">'
  html += self.zmi_breadcrumbs(self,request)
  html += '<form class="form-horizontal" method="post" enctype="multipart/form-data">'
  html += '<legend>Import DOCX</legend>'
  html += '<div class="form-group row">'
  html += '<label class="control-label col-sm-2" for="file"><span>%s</span></label>'%self.getZMILangStr('ATTR_FILE')
  html += '<div class="col-sm-10"><input class="btn btn-file" size="25" name="file" type="file"/></div>'
  html += '</div><!-- .form-group -->'
  html += '<div class="form-group row">'
  html += '<div class="controls save">'
  html += '<button type="submit" name="btn" class="btn btn-primary" value="%s">%s</button> '%(self.getZMILangStr('BTN_IMPORT'),self.getZMILangStr('BTN_IMPORT'))
  html += '<button type="button" name="btn" class="btn btn-secondary" value="return %s" onclick="btn_execute_click()">%s</button> '%(self.getZMILangStr('BTN_EXECUTE'),self.getZMILangStr('BTN_EXECUTE'))
  html += '</div>'
  html += '</div><!-- .form-group -->'
  
  # ---------------------------------
  
  html += '</form><!-- .form-horizontal -->'
  html += '</div><!-- #zmi-tab -->'
  html += self.zmi_body_footer(self,request)
  html += '</body>'
  html += '</html>'
  
  return html