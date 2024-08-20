################################################################################
# _daemon.py
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

# Imports.
from threading import *
import requests
import time
import uuid
# Product Imports.
from Products.zms import standard

stack = []
interval = 5

def process():
    while True:
        while stack:
            item = stack.pop()
            uid, url, kwargs = item[0], item[1], item[2]
            standard.writeInfo(None, '[_daemon.process.%s]: %s'%(uid, url+'?'+'&'.join(['%s=%s'%(x,str(kwargs[x])) for x in kwargs])))
            response = requests.get(url, kwargs)
            standard.writeInfo(None, '[_daemon.process.%s]: ==> %s'%(uid, str(response)))
        time.sleep(interval)

def push(self, name, **kwargs):
    uid = None
    instack = bool(self.getConfProperty('%s.%s.async'%(self.meta_type,name),1))
    if instack:
        uid = str(uuid.uuid4())
        url = '%s/%s'%(self.absolute_url(),name)
        standard.writeInfo(None, '[_daemon.push.%s]: %s'%(uid, url))
        stack.append((uid, url, kwargs))
    return uid

def start():
    thread = Thread(target=process)
    thread.start()
