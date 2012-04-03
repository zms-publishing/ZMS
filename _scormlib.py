################################################################################
# _scormlib.py
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


# Product Imports.
import zmscontainerobject
import _globals
import _xmllib

# ------------------------------------------------------------------------------
#  _scormlib.getIMSManifestItems:
# ------------------------------------------------------------------------------
def getIMSManifestItems(self, REQUEST):
  obs = self.getChildNodes( REQUEST)
  xml = []
  if self.isActive( REQUEST):
    xml.append('<item')
    xml.append(' identifier="%s"'%self.id)
    if len(filter(lambda x: x.isPageElement(), obs)) > 0 or \
       len(filter(lambda x: x.isPage(), obs)) == 0:
      xml.append(' identifierref="R_%s"'%self.id)
      learningresourcetype = self.getObjProperty( 'learningresourcetype', REQUEST)
      if learningresourcetype is None or learningresourcetype == '':
        if self.meta_id == 'ZMSDocument':
          learningresourcetype = 'lecture.document'
        elif self.meta_id == 'ZMSFolder':
          learningresourcetype = 'lecture.folder'
        else:
          learningresourcetype = 'Unknown'
      xml.append(' learningresourcetype="%s"'%str(learningresourcetype))
    if self.getObjProperty('attr_ims_isvisible',REQUEST)==0:
      xml.append(' isvisible="false"')
    else:
      xml.append(' isvisible="true"')
    xml.append('>')
    # Title (place always before Sequencing-Rules!)
    xml.append('<title><string language="%s"><![CDATA[%s]]></string></title>\n'%(REQUEST.get('lang',self.getPrimaryLanguage()),self.getTitlealt(REQUEST)))
    # Score
    xml.append( self.getObjProperty( 'imsmanifestScore', REQUEST))
    # Sequencing-Rules
    self.initObjChildren(REQUEST)
    for ob in self.getObjChildren('',REQUEST):
      if 'imsmanifest' in self.getMetaobjAttrIds(ob.meta_id):
        xml.append( ob.getObjProperty( 'imsmanifest', REQUEST))
    for ob in obs:
      if ob.isPage():
        xml.extend(getIMSManifestItems(ob,REQUEST))
    xml.append('</item>')
  return ''.join(xml)

# ------------------------------------------------------------------------------
#  getIMSManifestResources:
# ------------------------------------------------------------------------------
def getIMSManifestResources(base, self, scoType, REQUEST):
  from _exportable import localHtml
  obs = self.getChildNodes(REQUEST)
  xml = ''
  if not self.isActive( REQUEST) or self.isResource( REQUEST):
    scoType = 'asset'
  if self.isActive( REQUEST) and \
     (len(filter(lambda x: x.isPageElement(), obs)) > 0 or \
      len(filter(lambda x: x.isPage(), obs)) == 0):
    href =  self.getHref2IndexHtml(REQUEST)[len(base.absolute_url())+1:]
    xml += '<resource'
    xml += ' identifier="R_%s"'%self.id
    xml += ' type="webcontent"'
    xml += ' adlcp:scormType="%s"'%scoType
    xml += ' href="%s"'%href
    xml += '>\n'
    xml += '<metadata/>\n'
    xml += '\t<file href="%s" />\n'%href
    REQUEST.set('ZMS_PATH_HANDLER', True)
    try:
      html = self.index_html( self, REQUEST)
    except:
      html = ''
      _globals.writeError( self, "[getIMSManifestResources]: An unexpected error occured!")
    html = localHtml( self, html)
    hrefs = []
    i = -1
    s0 = 'href="'
    s1 = '"'
    while True:
      i = html.find( s0, i + 1)
      if i < 0: break
      j = html.find( s1, i + len( s0))
      hrefs.append( html[i + len( s0) : j])
    i = -1
    s0 = 'src="'
    s1 = '"'
    while True:
      i = html.find( s0, i + 1)
      if i < 0: break
      j = html.find( s1, i + len( s0))
      hrefs.append( html[i + len( s0) : j])
    homeUrl = self.getHome().absolute_url()+'/'
    baseUrl = base.absolute_url()+'/'
    docUrl = self.getDocumentElement().absolute_url()+'/'
    commonUrl = self.getHome().common.absolute_url()+'/'
    for href in hrefs:
      if href.find( homeUrl) == 0:
        if href.find( baseUrl) == 0:
          href = href[ len( baseUrl) : ]
        elif href.find( docUrl) == 0:
          href = href[ len( docUrl) : ]
        elif href.find( commonUrl) == 0:
          href = href[ len( commonUrl) : ]
        xml += '\t<file href="%s" />\n'%href
    xml += '</resource>\n'
  for ob in obs:
    if ob.isPage():
      xml += getIMSManifestResources(base,ob,scoType,REQUEST)
  return xml


# ------------------------------------------------------------------------------
#  getCdataOrLanguageString:
# ------------------------------------------------------------------------------
def getCdataOrLanguageString( self, nodeSet):
  for node in nodeSet:
    v = node.get('cdata')
    if v is not None and len( v) > 0:
      return v
    for string_node in self.xmlNodeSet( node, 'string'):
      v = string_node.get('cdata')
      if v is not None and len( v) > 0:
        return v
  return None


################################################################################
################################################################################
###
###   class SCORMLib
###
################################################################################
################################################################################
class SCORMLib:

  # ----------------------------------------------------------------------------
  #  parseIMSManifest:
  #
  #  Parse IMSManifest.xml
  # ----------------------------------------------------------------------------
  def parseIMSManifest(self, xml):
    IMSManifest = []
    NodeSet = self.xmlParse(xml)
    ResourceDict = {}
    for nResources in self.xmlNodeSet(NodeSet,'resources'):
      for nResource in self.xmlNodeSet(nResources,'resource'):
        attrs = nResource['attrs']
        identifier = attrs['identifier']
        ResourceDict[identifier] = attrs
    for nOrganizations in self.xmlNodeSet(NodeSet,'organizations'):
      for nOrganization in self.xmlNodeSet(nOrganizations,'organization'):
        level_offs = nOrganization['level']
        for nItem in self.xmlNodeSet(nOrganization,'item',1):
          attrs = nItem['attrs']
          level = nItem['level']
          identifier = attrs['identifier']
          identifierref = attrs.get('identifierref',None)
          isvisible = attrs.get('isvisible','true')=='true'
          learningresourcetype = attrs.get('learningresourcetype','Unknown')
          item = {}
          item['id'] = identifier
          item['visible'] = isvisible
          item['level'] = level-level_offs
          item['learningresourcetype'] = learningresourcetype
          # Sequencing-Rules
          item['sequencing_rules'] = []
          for nSequencing in self.xmlNodeSet(nItem,'imsss:sequencing'):
            for nSequencingRules in self.xmlNodeSet(nSequencing,'imsss:sequencingRules'):
              for nPreConditionRule in self.xmlNodeSet(nSequencingRules,'imsss:preConditionRule'):
                seqRule = {}
                for nRuleConditions in self.xmlNodeSet(nPreConditionRule,'imsss:ruleConditions'):
                  for nRuleCondition in self.xmlNodeSet(nRuleConditions,'imsss:ruleCondition'):
                    attrs = nRuleCondition['attrs']
                    seqRule['rule_condition'] = attrs.get('condition') 
                    seqRule['rule_condition_op'] = attrs.get('operator','') 
                    seqRule['rule_condition_ref'] = attrs.get('referencedObjective','') 
                for nRuleAction in self.xmlNodeSet(nPreConditionRule,'imsss:ruleAction'):
                  attrs = nRuleAction['attrs']
                  seqRule['rule_action'] = attrs.get('action')
                item['sequencing_rules'].append(seqRule)
          # Title
          item['title'] = getCdataOrLanguageString( self, self.xmlNodeSet( nItem, 'title'))
          # Href
          item['href'] = None
          if identifierref in ResourceDict.keys():
            item['href'] = ResourceDict[identifierref]['href']
          IMSManifest.append(item)
    return IMSManifest

  # ----------------------------------------------------------------------------
  #  getIMSManifest:
  #
  #  Returns IMSManifest.xml
  # ----------------------------------------------------------------------------
  def getIMSManifest(self, REQUEST):
    preview = REQUEST.get('preview')
    if preview: REQUEST.set('preview','')
    REQUEST.set('ZMS_INDEX_HTML',1)
    xml = self.getXmlHeader()
    xml += '<manifest identifier="%sManifest" version="1.3"\n'%self.id
    xml += 'xmlns="http://www.imsglobal.org/xsd/imscp_v1p1"\n'
    xml += 'xmlns:adlcp="http://www.adlnet.org/xsd/adlcp_v1p3"\n'
    xml += 'xmlns:imsss="http://www.imsglobal.org/xsd/imsss"\n'
    xml += '>\n'
    xml += '<metadata>\n'
    xml += '<schema>ADL SCORM</schema>\n'
    xml += '<schemaversion>CAM 1.3</schemaversion>\n'
    xml += '</metadata>\n'
    xml += '<organizations default="%s_org">\n'%self.id
    xml += '<organization identifier="%s_org">\n'%self.id
    xml += '<title><![CDATA[%s]]></title>\n'%self.getTitlealt(REQUEST)
    xml += getIMSManifestItems(self,REQUEST)
    xml += '</organization>\n'
    xml += '</organizations>\n'
    xml += '<resources>\n'
    xml += getIMSManifestResources( self, self, 'sco', REQUEST)
    xml += '</resources>\n'
    xml += '</manifest>\n'
    if preview: REQUEST.set('preview',preview)
    return xml;
  
  
################################################################################
