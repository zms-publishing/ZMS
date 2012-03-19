################################################################################
# _builder.py
#
# Implementation of class Builder (see below).
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

# Imports
import pyexpat
import time
import Globals
# Product Imports.
import _globals

################################################################################
# class ParseError(Exception):
#
# General exception class to indicate parsing errors.
################################################################################
class ParseError(Exception): pass


################################################################################
# class Builder
#
# Implements a builder class (cp. design pattern "BUILDER") to build a tree of ZOPE objects
# out of an XML formatted document. Uses the class "pyexpat" (cp. module "Shared.DC.xml") for
# parsing the XML document. The general approach of the XML parser "pyexpat" is event driven, 
# where handler methods are called on occurence of XML tags. Builder redirects these events to
# a set of own handler methods (see below). To build up the object tree, Builder provides the
# following functionality:
#
# 1. Usually, the occurence of a XML tag induces the instanciation of a new node object. Therefore,
#    Builder contains a mapping table ("dGlobalAttrs"), that maps XML tags to python classes. The
#    handler method "Builder.OnStartElement()" creates a node object of the corresponding class.
#    This node object is then made current.
#
# 2. In General, events are directed to the current node object. Therefore, they have to contain 
#    a set of interface methods (see below). The node objects are responsible for handling these 
#    events. This includes the insertion into the object tree as well as the interpretation of 
#    XML tag parameters.
#
# 3. A dedicated root object is managed by Builder. The root object may be predefined or created
#    during the parsing process.
#
# Builder is usually used as a mix-in base class for other classes. For usage, the following
# issues must be taken into consideration:
#
# 1. Overwrite "dGlobalAttrs" with a dictionary, that maps XML-Tags to python classes.
# 2. Call "Builder.parse()" to initiate the parsing and building process.
# 3. Equip all python classes with the following interface methods:
#
#    - xmlOnStartElement(self, dTagName, dTagAttrs, oParentNode, oRoot)
#    - xmlOnCharacterData(self, sData, bInCData)
#    - xmlOnEndElement(self)
#    - xmlOnUnknownStartTag(self, sTagName, dTagAttrs)
#    - xmlOnUnknownEndTag(self, sTagName)
#    - xmlGetTagName(self)
#    - xmlGetParent(self)
#
################################################################################
class Builder:
    """ Builder """
  
    ######## class variables ########
    iBufferSize=1028 * 32   # buffer size for XML file parsing
  
      
    ############################################################################
    # Builder.__init__(self):
    #
    # Constructor.
    ############################################################################
    def __init__(self):
        """ Builder.__init__ """
        self.oRoot      = None   # root node of object tree
        self.oCurrNode  = None   # current node
        self.bInRootTag = False  # inside root tag?
        self.bInCData   = False  # inside CDATA section?


    ############################################################################
    # Builder.parse(self, root, input):
    #
    # Parse a given XML document and build a recursive object tree via event handler.
    #
    # IN:  input = XML document as string
    #            = XML document as file object   
    #      root  = pre-set root node for object tree (prevents the creation of a root object, when
    #              the first root tag appears in XML-document)
    #            = None, if no root object is given (will be instanciated)
    #
    # OUT: root object 
    #      None, if nothing was parsed
    ############################################################################
    def parse(self, input, root=None, bInRootTag=0):
        """ Builder.parse """
        
        # prepare builder
        self._unknownTagName  = None
        self.oRoot            = root
        self.oRootNode        = None
        self.oCurrNode        = None
        self.bInRootTag       = bInRootTag
        self.bInCData         = False
        if bInRootTag:
          self.oCurrNode = root
        
        # create parser object
        p = pyexpat.ParserCreate()
        
        # connect parser object with handler methods
        p.StartElementHandler = self.OnStartElement
        p.EndElementHandler = self.OnEndElement
        p.CharacterDataHandler = self.OnCharacterData
        p.StartCdataSectionHandler = self.OnStartCData
        p.EndCdataSectionHandler = self.OnEndCData
        p.ProcessingInstructionHandler = self.OnProcessingInstruction
        p.CommentHandler = self.OnComment
        p.StartNamespaceDeclHandler = self.OnStartNamespaceDecl
        p.EndNamespaceDeclHandler = self.OnEndNamespaceDecl
        
        #### parsing ####
        _globals.writeLog( self, "#### parsing ####")
        if type(input) is str:
          # input is a string!
          rv = p.Parse(input, 1)
        else:
          # input is a file object!
          while True:
            
            v=input.read(self.iBufferSize)
            if v=="":
              rv = 1
              break
            
            rv = p.Parse(v, 0)
            if not rv:
              break 
        
        # raise parser exception
        if not rv:
            raise ParseError('%s at line %s' % (pyexpat.ErrorString(p.ErrorCode), p.ErrorLineNumber))
        ####
        
        return self.oRootNode


    ############################################################################
    # Builder.OnStartElement(self, name, attrs):
    #
    # Handler of XML-Parser: 
    # Called at the start of a XML element (resp. on occurence of a XML start tag).
    # Usually, the occurence of a XML tag induces the instanciation of a new node object. Therefore,
    # Builder contains a mapping table ("dGlobalAttrs"), that maps XML tags to python classes. The
    # newly created node object is then made current. If no matching class is found for a XML tag,
    # the event handler "xmlOnUnknownStart()" is called on the current object.
    #
    # IN: name  = element name (=tag name)
    #     attrs = dictionary of element attributes
    ############################################################################
    def OnStartElement(self, name, attrs):
        """ Builder.OnStartElement """
        _globals.writeLog( self, "[Builder.OnStartElement(" + str(name) + ")]")
        
        name = _globals.unencode( name)
        attrs = _globals.unencode( attrs)
        
        # handle alias
        if name in self.getMetaobjIds(sort=0) and not self.dGlobalAttrs.has_key(name):
          attrs['meta_id'] = name
          name = 'ZMSCustom'
        # handle alias for zms2go
        if name == 'ZMS' and self.oRootNode is not None:
          attrs['meta_id'] = name
          name = 'ZMSCustom'
        
        if self.bInRootTag or \
           self.oRoot == None or \
           (self.oRoot.id == self.getDocumentElement().id and \
            self.dGlobalAttrs.has_key(name) and \
            self.dGlobalAttrs[name]['obj_class'] is not None):
            
            _globals.writeLog( self, "[Builder.OnStartElement]: " + \
                "We are inside the XML root tag OR no root object is set" + \
                "-> instanciate node object in any case")
            
            if self.dGlobalAttrs.has_key(name) and \
               self.dGlobalAttrs[name]['obj_class'] is not None:
                
                # class defined for tag!
                if self.oCurrNode==None and self.oRoot!=None and self.oRoot.id==self.getDocumentElement().id:
                  self.oCurrNode = self.oRoot
                    
                # create node instance
                _globals.writeBlock( self, "[Builder.OnStartElement]: create new object <" + str(name) + "> in " + str(self.oCurrNode))
                newNode = None
                if 'id_fix' in attrs.keys():
                  id = attrs.get( 'id_fix')
                  newNode = getattr(self.oCurrNode,id,None)
                elif 'id_prefix' in attrs.keys():
                  prefix = attrs.get( 'id_prefix')
                  id = self.oCurrNode.getNewId(prefix)
                elif 'id' in attrs.keys():
                  id = attrs.get( 'id')
                  prefix = _globals.id_prefix(id)
                  id = self.oCurrNode.getNewId(prefix)
                else:
                  id = self.oCurrNode.getNewId()
                sort_id = self.oCurrNode.getNewSortId()
                
                ##### Create ####
                if newNode is None:
                  newNode = self.dGlobalAttrs[name]['obj_class'](id,sort_id)
                  self.oCurrNode._setObject(newNode.id, newNode)
                  newNode = getattr(self.oCurrNode,newNode.id)
                
                ##### Identify Content-Object ####
                if newNode.meta_type == 'ZMSCustom':
                  meta_id = attrs.get( 'meta_id')
                  if meta_id not in self.getMetaobjIds( sort=0):
                    _globals.writeError(newNode,'[_builder.OnStartElement]: no object-definition available ('+str(meta_id)+')!')
                  newNode.meta_id = meta_id
                
                ##### Object State ####
                newNode.initializeWorkVersion()
                obj_attrs = newNode.getObjAttrs()
                langs = self.getLangIds()
                for lang in langs:
                  req = {'lang':lang,'preview':'preview'}
                  ##### Object State ####
                  newNode.setObjStateNew(req)
                  ##### Init Properties ####
                  if 'active' in obj_attrs.keys():
                    newNode.setObjProperty('active',1,lang)
                  if len( langs) == 1:
                    newNode.setObjProperty('change_uid','xml',lang)
                    newNode.setObjProperty('change_dt',time.time(),lang)
                
                _globals.writeLog( self, "[Builder.OnStartElement]: object with id " + str(newNode.id) + " of class " + str(newNode.__class__) + " created in " + str(self.oCurrNode.__class__))
                
                if self.oRoot is None:   # root object set?
                    self.oRoot = newNode # -> set root node
                
                # notify new node
                newNode.xmlOnStartElement(name, attrs, self.oCurrNode, self.oRoot)
                
                # set new node as current node
                self.oCurrNode = newNode
            
            else:
                # no class defined for tag 
                # -> offer to current object
                if self.oCurrNode==None:
                    raise ParseError("Unknown tag (" + name + "): no current object available!")  # no current object available!
                
                if not self.oCurrNode.xmlOnUnknownStartTag(name, attrs):
                    if self._unknownTagName == None:
                        self._unknownTagName = name
                    _globals.writeLog( self, "[Builder.OnStartElement]: Unknown start-tag (" + name + "): current object did not accept tag!")  # current object did not accept tag!
                    # raise ParseError("Unknown start-tag (" + name + "): current object did not accept tag!")  # current object did not accept tag!
          
        else:
            _globals.writeLog( self, "[Builder.OnStartElement]: " + 
                "we have encountered the XML root tag and a root object is predefined" + \
                "-> simply notify root object")
            self.oRoot.xmlOnStartElement(name, attrs, None, self.oRoot)
            
            # set root node as current node
            self.oCurrNode = self.oRoot
        
        # we are inside the XML root now!
        self.bInRootTag=1
        if self.oRootNode is None:
          self.oRootNode = self.oCurrNode


    ############################################################################
    # Builder.OnEndElement(self, name):
    #
    # Handler of XML-Parser: 
    # Called at the end of a XML element (resp. on occurence of a XML end tag).
    #
    # IN: name  = element name (=tag name)
    ############################################################################
    def OnEndElement(self, name):
        """ Builder.OnEndElement """
        _globals.writeLog( self, "[Builder.OnEndElement(" + str(name) + ")]")
        
        # do we have a current node?
        if self.oCurrNode==None:
            raise ParseError("Unmatching end tag (" + name + ")")
        
        # is this the right tag name?
        if name==self.oCurrNode.xmlGetTagName() or name==self.oCurrNode.meta_type:
          
          ##### VersionManager ####
          self.oCurrNode.resetObjStates()
          
          # notify current node
          self.oCurrNode.xmlOnEndElement()
          
          parent = self.oCurrNode.xmlGetParent()
          
          # set parent node as current node
          self.oCurrNode = parent
          
        
        else:
            if self.dGlobalAttrs.has_key(name) and \
               self.dGlobalAttrs[name]['obj_class'] is not None:
                if self.dGlobalAttrs.has_key(self.oCurrNode.xmlGetTagName()) and \
                   self.dGlobalAttrs[self.oCurrNode.xmlGetTagName()]['obj_class'] is not None:
                    # tag name is known, but not valid at this place!
                    raise ParseError("Unmatching end tag (/" + name + "), expected(/" + self.oCurrNode.xmlGetTagName() + ")")
            
            else:
                # tag name is unknown -> offer it to current object
                if not self.oCurrNode.xmlOnUnknownEndTag(name):
                    if name == self._unknownTagName:
                      self._unknownTagName = None
                    _globals.writeLog( self, "[Builder.OnEndElement]: Unknown end-tag (/" + name + ")")  # current object did not accept tag!
                    # raise ParseError("Unknown end-tag (" + name + ")")  # current object did not accept tag!


    ############################################################################
    # Builder.OnCharacterData(self, data):
    #
    # Handler of XML-Parser:
    # Called after plain character data was parsed. Forwards the character data to the current 
    # node. The class attribute "bInCData" determines, wether the character data is nested in a 
    # CDATA block.
    #
    # IN: data = character data string
    ############################################################################
    def OnCharacterData(self, data):
        """ Builder.OnCharacterData """
        _globals.writeLog( self, "[Builder.OnCharacterData]")
        
        # do we have a current node?
        if self.oCurrNode==None:
           raise ParseError("Unexpected character data found")
           
        # notify current node
        self.oCurrNode.xmlOnCharacterData(data, self.bInCData)


    ############################################################################
    # Builder.OnStartCData(self):
    #
    # Handler of XML-Parser:
    # Called at the start of a CDATA block (resp. on occurence of the "CDATA[" tag).
    ############################################################################
    def OnStartCData(self):
        """ Builder.OnStartCData """
        self.bInCData=1


    ############################################################################
    # Builder.OnEndCData(self):
    #
    # Handler of XML-Parser:
    # Called at the end of a CDATA block (resp. on occurence of the "]" tag).
    ############################################################################
    def OnEndCData(self):
        """ Builder.OnEndCData """
        self.bInCData=0


    ############################################################################
    # Builder.OnProcessingInstruction(self, target, data):
    #
    # Handler of XML-Parser:
    # Called on occurence of a processing instruction.
    #
    # IN: target = target (processing instruction)
    #     data   = dictionary of data
    ############################################################################
    def OnProcessingInstruction(self, target, data):
        """ Builder.OnProcessingInstruction """
        pass  # ignored


    ############################################################################
    # Builder.OnComment(self, data):
    #
    # Handler of XML-Parser:
    # Called on occurence of a comment.
    #
    # IN: data = comment string
    ############################################################################
    def OnComment(self, data):
        """ Builder.OnComment """
        pass  # ignored


    ############################################################################
    # Builder.OnStartNamespaceDecl(self, prefix, uri):
    #
    # Handler of XML-Parser:
    # Called at the start of a namespace declaration.
    #
    # IN: prefix = prefix of namespace
    #     uri    = namespace identifier
    ############################################################################
    def OnStartNamespaceDecl(self, prefix, uri):
        """ Builder.OnStartNamespaceDecl """
        pass  # ignored


    ############################################################################
    # Builder.OnEndNamespaceDecl(self, prefix):
    #
    # Handler of XML-Parser:
    # Called at the end of a namespace declaration.
    #
    # IN: prefix = prefix of namespace
    ############################################################################
    def OnEndNamespaceDecl(self, prefix):
        """ Builder.OnEndNamespaceDecl """
        pass  # ignored

################################################################################
