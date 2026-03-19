"""
_builder.py

This module provides the generic XML builder used to construct ZMS object
trees from expat parser events.

Implements a builder class (cp. design pattern "BUILDER") to build a tree of ZOPE objects
out of an XML formatted document. Uses the class "pyexpat" (cp. module "Shared.DC.xml") for
parsing the XML document. The general approach of the XML parser "pyexpat" is event driven, 
where handler methods are called on occurence of XML tags. Builder redirects these events to
a set of own handler methods (see below). To build up the object tree, Builder provides the
following functionality:

  1. Usually, the occurence of a XML tag induces the instanciation of a new node object. Therefore,
    Builder contains a mapping table ("dGlobalAttrs"), that maps XML tags to python classes. The
    handler method "Builder.OnStartElement()" creates a node object of the corresponding class.
    This node object is then made current.

  2. In General, events are directed to the current node object. Therefore, they have to contain 
    a set of interface methods (see below). The node objects are responsible for handling these 
    events. This includes the insertion into the object tree as well as the interpretation of 
    XML tag parameters.

  3. A dedicated root object is managed by Builder. The root object may be predefined or created
    during the parsing process.

Builder is usually used as a mix-in base class for other classes. For usage, the following
issues must be taken into consideration:

  1. Overwrite "dGlobalAttrs" with a dictionary, that maps XML-Tags to python classes.
  2. Call "Builder.parse()" to initiate the parsing and building process.
  3. Equip all python classes with the following interface methods:

    - xmlOnStartElement(self, dTagName, dTagAttrs, oParentNode)
    - xmlOnCharacterData(self, sData, bInCData)
    - xmlOnEndElement(self)
    - xmlOnUnknownStartTag(self, sTagName, dTagAttrs)
    - xmlOnUnknownEndTag(self, sTagName)
    - xmlGetParent(self)

License: GNU General Public License v2 or later
Organization: ZMS Publishing
"""

# Imports
import pyexpat
import time
# Product Imports.
from Products.zms import standard

class ParseError(Exception):
  """Exception raised when XML parsing fails."""

  pass


class Builder(object):
    """
    Generic XML builder for constructing ZMS object trees.

    The builder wires expat parser callbacks to object-creation and
    object-update hooks implemented by ZMS node classes.
    """

    iBufferSize = 1028 * 32  # buffer size for XML file parsing

    def __init__(self):
        """Initialize builder state."""
        self.oRootTag = None
        self.oCurrNode = None
        self.bInCData = False

    def parse(self, input, root=None, bInRootTag=0):
        """
        Parse an XML document and build a recursive object tree.

        @param input: XML document as bytes or file-like object
        @type input: C{bytes} or file-like
        @param root: Optional pre-existing root node
        @type root: C{object}
        @param bInRootTag: Flag indicating parsing starts inside an existing root tag
        @type bInRootTag: C{int}
        @return: Last parsed node or root object
        @raise ParseError: If the XML document contains syntax errors
        """
        self.oRootTag = None
        self.oCurrNode = None
        self.bInCData = False
        if bInRootTag:
            self.oCurrNode = root

        p = pyexpat.ParserCreate()
        p.StartElementHandler = self.OnStartElement
        p.EndElementHandler = self.OnEndElement
        p.CharacterDataHandler = self.OnCharacterData
        p.StartCdataSectionHandler = self.OnStartCData
        p.EndCdataSectionHandler = self.OnEndCData
        p.ProcessingInstructionHandler = self.OnProcessingInstruction
        p.CommentHandler = self.OnComment
        p.StartNamespaceDeclHandler = self.OnStartNamespaceDecl
        p.EndNamespaceDeclHandler = self.OnEndNamespaceDecl

        if isinstance(input, bytes):
            rv = p.Parse(input, 1)
        else:
            while True:
                v = input.read(self.iBufferSize)
                if v == "":
                    rv = 1
                    break

                rv = p.Parse(v, 0)
                if not rv:
                    break

        if not rv:
            raise ParseError('%s at line %s' % (pyexpat.ErrorString(p.ErrorCode), p.ErrorLineNumber))

        oLastNode = getattr(self.oCurrNode, 'oLastNode', self)
        try:
            delattr(self.oCurrNode, 'oLastNode')
        except:
            pass
        return oLastNode

    def OnStartElement(self, name, attrs):
        """
        Handle the start of an XML element.

        Creates a new node for known meta objects or forwards unknown tags
        to the current node.

        @param name: Element name
        @type name: C{str}
        @param attrs: Dictionary of element attributes
        @type attrs: C{dict}
        """
        standard.writeLog(self, "[Builder.OnStartElement(" + str(name) + ")]")
        name = standard.unencode(name)
        attrs = standard.unencode(attrs)
        skip = self.oCurrNode is not None and len([x for x in self.oCurrNode.dTagStack if x.get('skip')]) > 0
        if not skip and name in self.getMetaobjIds():
            meta_id = name
            if self.oRootTag is None:
                self.oRootTag = meta_id
            globalAttr = self.dGlobalAttrs.get(meta_id, self.dGlobalAttrs['ZMSCustom'])
            constructor = globalAttr.get('obj_class', self.dGlobalAttrs['ZMSCustom']['obj_class'])
            if constructor is None:
                newNode = self
            else:
                id = None
                if 'id' in attrs:
                    id = attrs.get('id')
                    if standard.pybool(self.REQUEST.get('ignore_ids')):
                        prefix = standard.id_prefix(id)
                        new_id = self.getNewId(prefix)
                        id = new_id
                elif 'id_prefix' in attrs:
                    prefix = attrs.get('id_prefix')
                    id = self.getNewId(prefix)

                while id is None or id in self.oCurrNode.objectIds():
                    prefix = standard.id_prefix([id, 'e'][int(id is None)])
                    id = self.oCurrNode.getNewId(prefix)

                sort_id = self.oCurrNode.getNewSortId()
                uid = '%s' % attrs.get('uid') if 'uid' in attrs else ''
                if standard.pybool(self.REQUEST.get('ignore_uids')):
                    uid = ''

                newNode = constructor(id, sort_id, meta_id, uid)
                self.oCurrNode._setObject(newNode.id, newNode)
                newNode = getattr(self.oCurrNode, newNode.id)
                if uid and not standard.pybool(self.REQUEST.get('ignore_uids', False)):
                    newNode.set_uid(uid)
                standard.writeLog(self, "[Builder.OnStartElement]: object with id " + str(newNode.id) + " of class " + str(newNode.__class__) + " created in " + str(self.oCurrNode.__class__))

            newNode.initializeWorkVersion()
            obj_attrs = newNode.getObjAttrs()
            langs = self.getLangIds()
            for lang in langs:
                req = {'lang': lang, 'preview': 'preview'}
                newNode.setObjStateNew(req)
                if 'active' in obj_attrs:
                    newNode.setObjProperty('active', 1, lang)
                if len(langs) == 1:
                    dt = time.time()
                    userid = self.REQUEST['AUTHENTICATED_USER'].getId()
                    newNode.setObjProperty('created_uid', userid, lang)
                    newNode.setObjProperty('created_dt', dt, lang)
                    newNode.setObjProperty('change_uid', userid, lang)
                    newNode.setObjProperty('change_dt', dt, lang)

            newNode.xmlOnStartElement(name, attrs, self.oCurrNode)
            self.oCurrNode = newNode
        else:
            if not self.oCurrNode.xmlOnUnknownStartTag(name, attrs):
                standard.writeLog(self, "[Builder.OnStartElement]: Unknown start-tag (" + name + "): current object did not accept tag!")

    def OnEndElement(self, name):
        """
        Handle the end of an XML element.

        Finalizes the current node or delegates unknown end tags to the
        current node.

        @param name: Element name
        @type name: C{str}
        @raise ParseError: If an unknown end tag cannot be handled
        """
        standard.writeLog(self, "[Builder.OnEndElement(" + str(name) + ")]")
        skip = self.oCurrNode is not None and len([x for x in self.oCurrNode.dTagStack if x.get('skip')]) > 0
        if not skip and name == self.oCurrNode.meta_id:
            standard.writeLog(self, "[Builder.OnEndElement]: object finished")
            self.oCurrNode.resetObjStates()
            self.oCurrNode.xmlOnEndElement()

            oLastNode = getattr(self.oCurrNode, 'oLastNode', self)
            try:
                delattr(self.oCurrNode, 'oLastNode')
            except:
                pass
            self.oLastNode = self.oCurrNode
            self.oCurrNode = self.oCurrNode.xmlGetParent()
        else:
            if not self.oCurrNode.xmlOnUnknownEndTag(name):
                standard.writeLog(self, "[Builder.OnEndElement]: Unknown end-tag (/" + name + ")")
                raise ParseError("Unknown end-tag (" + name + ")")

    def OnCharacterData(self, data):
        """
        Handle character data parsed by expat.

        @param data: Character data
        @type data: C{str}
        """
        self.oCurrNode.xmlOnCharacterData(data, self.bInCData)

    def OnStartCData(self):
        """Handle the start of a CDATA section."""
        self.bInCData = 1

    def OnEndCData(self):
        """Handle the end of a CDATA section."""
        self.bInCData = 0

    def OnProcessingInstruction(self, target, data):
        """
        Handle a processing instruction.

        Processing instructions are ignored by this builder.

        @param target: Processing instruction target
        @type target: C{str}
        @param data: Processing instruction data
        @type data: C{str}
        """
        pass

    def OnComment(self, data):
        """
        Handle an XML comment.

        Comments are ignored by this builder.

        @param data: Comment content
        @type data: C{str}
        """
        pass

    def OnStartNamespaceDecl(self, prefix, uri):
        """
        Handle the start of a namespace declaration.

        Namespace declarations are ignored by this builder.

        @param prefix: Namespace prefix
        @type prefix: C{str}
        @param uri: Namespace URI
        @type uri: C{str}
        """
        pass

    def OnEndNamespaceDecl(self, prefix):
        """
        Handle the end of a namespace declaration.

        Namespace declarations are ignored by this builder.

        @param prefix: Namespace prefix
        @type prefix: C{str}
        """
        pass
