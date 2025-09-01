################################################################################
# yamlutil.py
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


def dump(data, clean=True):
    from yaml import dump
    if clean:
        data = __cleanup(data)
    return dump(data)

def parse(data):
    from yaml import safe_load
    return safe_load(data)

def __cleanup(v):
    """
    Recursively cleans up a dictionary by removing keys with falsy values.

    Args:
        v (dict or any): The input value, which can be a dictionary or any other type.

    Returns:
        dict or any: If the input is a dictionary, returns a new dictionary with keys
        whose values are falsy removed. If the input is not a dictionary, returns the
        input value unchanged.
    """
    if isinstance(v, dict):
        nd = {}
        for k in list(v.keys()):
            nv = __cleanup(v[k])
            if nv:
                nd[k] = nv
        return nd
    elif isinstance(v, list):
        nl = []
        for i in v:
            nv = __cleanup(i)
            if nv:
                nl.append(nv)
        return nl
    return v
