#!/usr/bin/python
# -*- coding: utf-8 -*-

################################################################################
# _globals.py
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

################################################################################
# Define MyClass.
################################################################################
class MyClass:

  # ----------------------------------------------------------------------------
  #  MyClass.keys:
  # ----------------------------------------------------------------------------
  def keys(self):
    return self.__dict__.keys()


################################################################################
# Define MySectionizer.
################################################################################
class MySectionizer:

    # --------------------------------------------------------------------------
    #  MySectionizer.__init__:
    #
    #  Constructor.
    # --------------------------------------------------------------------------
    def __init__(self, levelnfc='0'):
      self.levelnfc = levelnfc
      self.sections = []

    # --------------------------------------------------------------------------
    #  MySectionizer.__str__:
    #
    #  Returns a string representation of the object.
    # --------------------------------------------------------------------------
    def __str__(self):
      s = ''
      for i in range(len(self.sections)):
        if self.levelnfc == '0':
          s += str(self.sections[i]) + '.'
        elif self.levelnfc == '1':
          s += chr(self.sections[i] - 1 + ord('A')) + '.'
        elif self.levelnfc == '2':
          s += chr(self.sections[i] - 1 + ord('a')) + '.'
      return s

    # --------------------------------------------------------------------------
    #  MySectionizer.clone:
    #
    #  Creates and returns a copy of this object.
    # --------------------------------------------------------------------------
    def clone(self):
      ob = MySectionizer(self.levelnfc)
      ob.sections = copy.deepcopy(self.sections)
      return ob

    # --------------------------------------------------------------------------
    #  MySectionizer.getLevel:
    # --------------------------------------------------------------------------
    def getLevel(self):
      return len(self.sections)

    # --------------------------------------------------------------------------
    #  MySectionizer.processLevel:
    # --------------------------------------------------------------------------
    def processLevel(self, level):
      # Increase section counter on this level.
      if level > 0:
        if level == len(self.sections):
          self.sections[level-1] = self.sections[level-1] + 1
        elif level > len(self.sections):
          for i in range(len(self.sections),level):
            self.sections.append(1)
        elif level < len(self.sections):
          for i in range(level,len(self.sections)):
            del self.sections[len(self.sections)-1]
          self.sections[level-1] = self.sections[level-1] + 1


################################################################################
# Define MyStack.
################################################################################
class MyStack:

    # --------------------------------------------------------------------------
    #  MyStack.__init__:
    #
    #  Constructor.
    # --------------------------------------------------------------------------
    def __init__(self):
      self.clear()

    # --------------------------------------------------------------------------
    #  MyStack.__str__:
    #
    #  Returns a string representation of the object.
    # --------------------------------------------------------------------------
    def __str__(self):
      s = ''
      for el in self._stack:
        s += str(el) + ';'
      return s[:-1]

    def size(self):
      return len(self._stack)

    def clear(self):
      self._stack = []

    def push(self, x):
      self._stack.append(x)

    def pop(self):
      if len(self._stack) > 0:
        return self._stack.pop()
      else:
        return None

    def get_all(self):
      return self._stack

    def get(self, i=0):
      if len(self._stack) > 0 and abs(i) < len(self._stack):
        if i < 0:
          return self._stack[len(self._stack)+i-1]
        else:
          return self._stack[i]
      else:
        return None

    def top(self):
      if len(self._stack) > 0:
        return self._stack[len(self._stack)-1]
      else:
        return None

################################################################################
