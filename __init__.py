################################################################################
# Initialisation file for the ZMS Product for Zope
#
# $Id: __init__.py,v 1.3 2004/11/24 21:02:52 zmsdev Exp $
# $Name:$
# $Author: zmsdev $
# $Revision: 1.3 $
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
#
################################################################################

"""ZMS Product"""

# Documentation string.
__doc__ = """initialization module."""
# Version string.
__version__ = '0.1'

# Imports.
from App.Common import package_home
from App.ImageFile import ImageFile
import OFS.misc_
import os
import stat
# Product Imports.
import _globals
import zms
import zmscustom
import zmssqldb
import zmslinkcontainer
import zmslinkelement
import _mediadb
import _sequence
import _zmsattributecontainer
#import _deprecated
import zmsdocument
import zmsfile
import zmsfolder
import zmsgraphic
import zmsnote
import zmsrubrik
import zmssysfolder
import zmstable
import zmsteaserelement
import zmsteasercontainer
import zmstextarea


################################################################################
# Define the initialize() function.
################################################################################

def initialize(context): 
    """Initialize the product."""
    
    try: 
        """Try to register the product."""
        
        context.registerClass(
            zms.ZMS,
            permission = 'Add ZMSs',
            constructors = ( zms.manage_addZMSForm, zms.manage_addZMS),
            container_filter = zms.containerFilter,
            )
        context.registerClass(
            zmscustom.ZMSCustom,
            permission = 'Add ZMSs',
            constructors = (zmscustom.manage_addZMSCustomForm, zmscustom.manage_addZMSCustom),
            container_filter = zmscustom.containerFilter,
            )
        context.registerClass(
            zmssqldb.ZMSSqlDb,
            permission = 'Add ZMSs',
            constructors = (zmssqldb.manage_addZMSSqlDbForm, zmssqldb.manage_addZMSSqlDb),
            container_filter = zmscustom.containerFilter,
            )
        context.registerClass(
            zmslinkcontainer.ZMSLinkContainer,
            permission = 'Add ZMSs',
            constructors = (zmslinkcontainer.manage_addZMSLinkContainer, zmslinkcontainer.manage_addZMSLinkContainer),
            container_filter = zmscustom.containerFilter,
            )
        context.registerClass(
            zmslinkelement.ZMSLinkElement,
            permission = 'Add ZMSs',
            constructors = (zmslinkelement.manage_addZMSLinkElementForm, zmslinkelement.manage_addZMSLinkElement),
            container_filter = zmscustom.containerFilter,
            )
        context.registerClass(
            _mediadb.MediaDb,
            permission = 'Add ZMSs',
            constructors = (_mediadb.manage_addMediaDb, _mediadb.manage_addMediaDb),
            icon = 'www/acl_mediadb.gif',
            container_filter = _mediadb.containerFilter,
            )
        context.registerClass(
            _zmsattributecontainer.ZMSAttributeContainer,
            permission = 'Add ZMSs',
            constructors = (_zmsattributecontainer.manage_addZMSAttributeContainer, _zmsattributecontainer.manage_addZMSAttributeContainer),
            container_filter = _zmsattributecontainer.containerFilter,
            )
        
        # register deprecated classes
        dummy_constructors = (zmscustom.manage_addZMSCustomForm, zmscustom.manage_addZMSCustom,)
        context.registerClass(zmsdocument.ZMSDocument,constructors=dummy_constructors,container_filter=zmscustom.containerFilter,)
        context.registerClass(zmsfile.ZMSFile,constructors=dummy_constructors,container_filter=zmscustom.containerFilter,)
        context.registerClass(zmsfolder.ZMSFolder,constructors=dummy_constructors,container_filter=zmscustom.containerFilter,)
        context.registerClass(zmsgraphic.ZMSGraphic,constructors=dummy_constructors,container_filter=zmscustom.containerFilter,)
        context.registerClass(zmsnote.ZMSNote,constructors=dummy_constructors,container_filter=zmscustom.containerFilter,)
        context.registerClass(zmssysfolder.ZMSSysFolder,constructors=dummy_constructors,container_filter=zmscustom.containerFilter,)
        context.registerClass(zmstable.ZMSTable,constructors=dummy_constructors,container_filter=zmscustom.containerFilter,)
        context.registerClass(zmsteasercontainer.ZMSTeaserContainer,constructors=dummy_constructors,container_filter=zmscustom.containerFilter,)
        context.registerClass(zmsteaserelement.ZMSTeaserElement,constructors=dummy_constructors,container_filter=zmscustom.containerFilter,)
        context.registerClass(zmstextarea.ZMSTextarea,constructors=dummy_constructors,container_filter=zmscustom.containerFilter,)
        
        # automated registration for util
        OFS.misc_.misc_.zms['initutil']=_globals.initutil()
        
        # automated registration for other resources
        for img_path in ['www/','plugins/www/']:
          path = package_home(globals()) + os.sep + img_path
          for file in os.listdir(path):
            filepath = path + os.sep + file 
            mode = os.stat(filepath)[stat.ST_MODE]
            if not stat.S_ISDIR(mode):
              registerImage(filepath,file)
    
    except:
        """If you can't register the product, dump error. 
        
        Zope will sometimes provide you with access to "broken product" and
        a backtrace of what went wrong, but not always; I think that only 
        works for errors caught in your main product module. 
        
        This code provides traceback for anything that happened in 
        registerClass(), assuming you're running Zope in debug mode."""
        
        import sys, traceback, string
        type, val, tb = sys.exc_info()
        sys.stderr.write(string.join(traceback.format_exception(type, val, tb), ''))
        del type, val, tb

def registerImage(filepath,s):
  """
  manual icon registration
  """
  icon=ImageFile(filepath,globals())
  icon.__roles__ = None
  OFS.misc_.misc_.zms[s]=icon

################################################################################
