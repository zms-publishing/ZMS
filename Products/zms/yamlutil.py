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


def dump(data):
    from ruamel.yaml import YAML
    import io
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.indent(mapping=2, sequence=4, offset=2)
    stream = io.StringIO()
    yaml.dump(data, stream)
    return stream.getvalue()


def parse(data):
    from ruamel.yaml import YAML
    yaml=YAML(typ="safe")
    return yaml.load(data)


def __cleanup(v):
    from ruamel.yaml.scalarstring import LiteralScalarString    
    """
    Recursively cleans up a dictionary by removing keys with falsy values.
    Args:
        v (dict or any): The input value, which can be a dictionary or any other type.
    Returns:
        dict or any: If the input is a dictionary, returns a new dictionary with keys
        whose values are falsy removed. If the input is not a dictionary, returns the
        input value unchanged.
    """
    if v:
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
        elif isinstance(v, str) and (v.find('\n') >= 0 or v.find('\r') >= 0):
            return LiteralScalarString(str(v))
    return v