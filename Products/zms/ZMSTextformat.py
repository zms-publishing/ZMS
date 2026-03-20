"""
ZMSTextformat.py

Text-format model and rendering helpers for ZMS rich-text output.

This module contains:

1. C{br_quote}: a helper that transforms plain text into HTML fragments while
  preserving line breaks, indentation, and simple nested list markers.
2. C{ZMSTextformat}: a small value object representing one configured text
  format (tag, optional sub-tag, attributes, and usage metadata), plus
  rendering helpers to convert input text into wrapped HTML.

License: GNU General Public License v2 or later
Organization: ZMS Publishing
"""

# Imports.
import re

# Product Imports.
from Products.zms import standard


def br_quote(self, text, subtag):
  """
  Convert a plain text fragment to HTML according to the configured sub-tag.

  The function preserves leading whitespace, supports C{<br>} handling,
  injects management-interface markers for visible line breaks, and converts
  simple tab-prefixed list syntax (C{'\t* '} / C{'\t# '}) into nested
  C{<ul>} / C{<ol>} structures.

  @param self: Rendering context used to detect management interface mode.
  @type self: C{object}
  @param text: Input text to transform.
  @type text: C{str}
  @param subtag: Optional sub-tag name used for line wrapping (e.g. C{'br'}).
  @type subtag: C{str}
  @return: HTML fragment with transformed line and list markup.
  @rtype: C{str}
  """
  if len(subtag) == 0:
    return text
  if type(text) not in [str, str]:
    text = str(text)
  rtn = ''
  qcr = ''
  qtab = '&nbsp;'*6
  
  if standard.isManagementInterface(self):
    if 'format' not in self.REQUEST:
      qcr = '<span class="unicode">&crarr;</span>'
      qtab = '<span class="unicode">&rarr;</span>' + '&nbsp;' * 5
  
  if subtag == 'br':
    tmp = []
    for s in text.split('<%s>'%subtag):
      while len(s) > 0 and ord(s[0]) in [10, 13]: s = s[1:]
      if len(tmp) > 0:
        tmp.append('\n')
      tmp.append(s)
    text = ''.join(tmp)
  
  # handle nested lists
  ts = text.split('\n')
  ll = []
  c = 0
  for line in ts:
    if line.find( '\t* ') >= 0 or line.find( '\t# ') >= 0:
      i = 0
      while i < len( line) and line[ i] == '\t':
        i += 1
      if line[ i] in [ '*', '#']:
        level = i
        
        # open nested lists
        if level > len(ll):
          if line[ i] == '*':
            rtn += '<ul>'*(level-len(ll))
            ll.extend(['ul']*(level-len(ll)))
          elif line[ i] == '#':
            rtn += '<ol>'*(level-len(ll))
            ll.extend(['ol']*(level-len(ll)))
        
        # close nested lists
        elif level < len(ll):
          for li in range(len(ll)-level):
            rtn += '</%s>'%ll[-1]
            ll = ll[0:-1]
        
        rtn += '<li>%s</li>'%line[i+2:]
        continue
    
    # close nested lists
    if len(ll) > 0:
      level = 0
      for li in range(len(ll)-level):
        rtn += '</%s>'%ll[-1]
        ll = ll[0:-1]
    
    # handle leading whitespaces and tabs
    i = 0
    while i < len( line) and line[ i] in [ ' ', '\t']:
      if line[ i] == ' ':
        rtn += '&nbsp;'
      elif line[ i] == '\t':
        rtn += qtab
      i += 1
    rtn += '\n'
    line = line[ i:].strip()
    
    if subtag == 'br':
      rtn += line+qcr
      if c < len( ts):
        rtn += '<%s />'%subtag
    elif len(line) > 0:
      rtn += '<%s'%subtag
      rtn += '>'
      rtn += line+qcr
      rtn += '</%s>'%subtag
    c += 1
  
  # close nested lists
  if len(ll) > 0:
    level = 0
    for li in range(len(ll)-level):
      rtn += '</%s>'%ll[-1]
      ll = ll[0:-1]
  
  return rtn


class ZMSTextformat(object):
  """
  Represent one text-format definition and provide rendering helpers.

  A text format defines the outer tag, optional inner sub-tag, additional
  HTML attributes, editor-availability flag, and usage categories.
  """

  def __init__(self, id, ob, manage_lang):
    """
    Initialize the text-format object from its persisted configuration mapping.

    @param id: Text-format identifier.
    @type id: C{str}
    @param ob: Persisted format definition containing keys like C{display},
      C{tag}, C{subtag}, C{attrs}, optional C{richedit}, and optional C{usage}.
    @type ob: C{dict}
    @param manage_lang: Language used to select the display label.
    @type manage_lang: C{str}
    """
    self.setId(id)
    self.setDisplay(ob['display'].get(manage_lang,id))
    self.setTag(ob['tag'])
    self.setSubTag(ob['subtag'])
    self.setAttrs(ob['attrs'])
    self.setRichedit(ob.get('richedit', 0))
    self.setUsage(ob.get('usage', ['standard']))

  getId__roles__ = None

  def getId(self):
    """Return the text-format identifier."""
    return self.id


  def setId(self, id):
    """Set the text-format identifier."""
    self.id = id

  getDisplay__roles__ = None

  def getDisplay(self):
    """Return the management label shown for this text format."""
    return self.display


  def setDisplay(self, display):
    """Set the management label shown for this text format."""
    self.display = display

  getTag__roles__ = None

  def getTag(self):
    """Return the outer HTML tag used for rendering."""
    return self.tag


  def setTag(self, tag):
    """Set the outer HTML tag used for rendering."""
    self.tag = tag

  getStartTag__roles__ = None

  def getStartTag(self, id=None, clazz=None): 
    """
    Build the opening HTML tag for this text format.

    @param id: Optional DOM id attribute for the opening tag.
    @type id: C{str} or C{None}
    @param clazz: Optional CSS class attribute for the opening tag.
    @type clazz: C{str} or C{None}
    @return: Opening tag HTML or an empty string when no outer tag is defined.
    @rtype: C{str}
    """
    html = ''
    tag = self.getTag()
    if len(tag) > 0:
      html += '<%s'%tag
      if id is not None:
        html += ' id="%s"'%id
      if clazz is not None:
        html += ' class="%s"'%clazz
      attrs = self.getAttrs()
      if len(attrs) > 0:
        html += ' ' + attrs
      html += '>'
    return html

  getEndTag__roles__ = None

  def getEndTag(self): 
    """Return the closing HTML tag for the configured outer tag."""
    html = ''
    tag = self.getTag()
    if len(tag) > 0:
      html += '</%s'%tag
      html += '>'
    return html

  getSubTag__roles__ = None

  def getSubTag(self):
    """Return the optional sub-tag used for line-level wrapping."""
    return self.subtag


  def setSubTag(self, subtag):
    """Set the optional sub-tag used for line-level wrapping."""
    self.subtag = subtag

  getAttrs__roles__ = None

  def getAttrs(self):
    """Return the raw HTML attribute string for the outer tag."""
    return self.attrs


  parseAttrs__roles__ = None

  def parseAttrs(self):
    """
    Parse the raw attribute string into C{(name, value)} tuples.

    @return: List of parsed attribute-name/value tuples.
    @rtype: C{list}
    """
    d = []
    l = re.split('(.*?)="(.*?)"', self.attrs)
    for i in range(len(l)//3):
      d.append((l[i*3+1], l[i*3+2]))
    return d


  def setAttrs(self, attrs):
    """Set the raw HTML attribute string for the outer tag."""
    self.attrs = attrs

  getRichedit__roles__ = None

  def getRichedit(self):
    """Return whether this format is available in rich-text editing."""
    return self.richedit


  def setRichedit(self, richedit):
    """
    Set the rich-text-editor availability flag.

    Non-empty string/bytes values are normalized to C{1} for compatibility with
    historic persisted values.
    """
    if isinstance(richedit, bytes) or isinstance(richedit, str) and len(richedit) > 0:
      richedit = 1
    self.richedit = richedit

  getUsage__roles__ = None

  def getUsage(self):
    """Return the usage categories where this format is offered."""
    return self.usage


  def setUsage(self, usage):
    """Set the usage categories where this format is offered."""
    self.usage = usage

  getHtml__roles__ = None

  def getHtml(self): 
    """
    Return a management-preview HTML snippet for this text format.

    @return: HTML preview showing opening tag, sample content, and closing tag.
    @rtype: C{str}
    """
    html = ''
    # Open tag.
    if len(self.getTag()) > 0:
      html += '&lt;'
      html += self.getTag()
      if len(self.getAttrs()) > 0:
        html += ' ' + self.getAttrs()
      html += '&gt;'
      html += '<br />'
    # Sub tag.
    subtag = self.getSubTag()
    if len(subtag)>0:
      if subtag == 'br':
        html += '&nbsp;&nbsp;...&lt;' + subtag + ' /&gt;'
      else:
        html += '&nbsp;&nbsp;&lt;' + subtag + '&gt;...&lt;/' + subtag + '&gt;'
      html += '<br />'
    else:
      html += '...'
    # Close tag.
    if len(self.getTag()) > 0:
      html += '&lt;/'
      html += self.getTag()
      html += '&gt;'
      html += '<br />'
    return html

  renderText__roles__ = None

  def renderText(self, context, text, id=None, clazz=None, encoding='utf-8', errors='strict'):
    """
    Render input text according to this text format definition.

    The method wraps transformed text with opening/closing tags generated by
    this format.  Line handling is delegated to L{br_quote}.

    @param context: Rendering context passed to L{br_quote}.
    @type context: C{object}
    @param text: Input text or bytes to render.
    @type text: C{str} or C{bytes}
    @param id: Optional DOM id for the opening tag.
    @type id: C{str} or C{None}
    @param clazz: Optional CSS class for the opening tag.
    @type clazz: C{str} or C{None}
    @param encoding: Character encoding used when decoding byte strings.
    @type encoding: C{str}
    @param errors: Error handling mode for byte decoding.
    @type errors: C{str}
    @return: Rendered HTML fragment.
    @rtype: C{str}
    """
    html = ''
    # Open tag.
    html += self.getStartTag( id, clazz)
    # Sub tag.
    text = br_quote( context, text, self.getSubTag())
    # Value.
    try:
      html += str(text, encoding, errors)
    except:
      html += text
    # Close tag.
    html += self.getEndTag()
    # Return.
    return html

