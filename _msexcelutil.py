# -*- coding: utf-8 -*- 
################################################################################
# _msexcelutil.py
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
################################################################################

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
_msexcelutil.export:
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def export(self, data, meta=None):
  request = self.REQUEST
  RESPONSE = request.RESPONSE
  RESPONSE.setHeader('Content-Type','application/vnd.ms-excel')
  RESPONSE.setHeader('Content-Disposition','inline;filename="export.xml"')
  RESPONSE.setHeader('Cache-Control', 'no-cache')
  RESPONSE.setHeader('Pragma', 'no-cache')
  l = []
  l.append('<?xml version="1.0"?>')
  l.append('<?mso-application progid="Excel.Sheet"?>')
  l.append('<Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet"')
  l.append('xmlns:o="urn:schemas-microsoft-com:office:office"')
  l.append('xmlns:x="urn:schemas-microsoft-com:office:excel"')
  l.append('xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet"')
  l.append('xmlns:html="http://www.w3.org/TR/REC-html40">')
  l.append('<Styles>')
  l.append('<Style ss:ID="head">')
  l.append('<Font x:Family="Swiss" ss:Bold="1"/>')
  l.append('<Interior ss:Color="#EEEE00" ss:Pattern="Solid"/>')
  l.append('</Style>')
  l.append('<Style ss:ID="string">')
  l.append('<Alignment ss:Vertical="Top" />')
  l.append('</Style>')
  l.append('</Styles>')
  l.append('<Worksheet ss:Name="%s1">'%self.getZMILangStr('ATTR_TABLE'))
  l.append('<Table>')
  if type(meta) is list:
    l.append('<Row>')
    for col in meta:
      l.append('<Cell ss:StyleID="head"><Data ss:Type="String">%s</Data></Cell>'%str(col))
    l.append('</Row>')
  for row in data:
    l.append('<Row>')
    if type(row) is dict:
      for col in meta:
        try:
          cell = row[col]
        except:
          cell = 'NONE'
        l.append('<Cell ss:StyleID="string"><Data ss:Type="String"><![CDATA[%s]]></Data></Cell>'%str(cell))
    else:
      for cell in row:
        l.append('<Cell ss:StyleID="string"><Data ss:Type="String"><![CDATA[%s]]></Data></Cell>'%str(cell))
    l.append('</Row>')
  l.append('</Table>')
  l.append('</Worksheet>')
  l.append('</Workbook>')
  return '\n'.join(l)

################################################################################