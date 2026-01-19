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

# Imports.
import io
import time

try:
    from ruamel.yaml import YAML
    _USE_RUAMEL = True
except ImportError:
    import yaml as _pyyaml
    _USE_RUAMEL = False

def dump(data):
    if _USE_RUAMEL:
        # Custom representer for struct_time
        def represent_struct_time(dumper, data):
            return dumper.represent_scalar('!struct_time', time.strftime('%Y-%m-%d %H:%M:%S', data))
        yaml = YAML()
        yaml.representer.add_representer(time.struct_time, represent_struct_time)
        yaml.preserve_quotes = True
        yaml.indent(mapping=2, sequence=4, offset=2)
        stream = io.StringIO()
        yaml.dump(data, stream)
        return stream.getvalue()
    else:
        # PyYAML fallback
        def struct_time_representer(dumper, data):
            return dumper.represent_scalar('!struct_time', time.strftime('%Y-%m-%d %H:%M:%S', data))
        _pyyaml.add_representer(time.struct_time, struct_time_representer)
        return _pyyaml.dump(data, default_flow_style=False)


def parse(data): 
    if _USE_RUAMEL:
        # Custom constructor for struct_time
        def construct_struct_time(loader, node):
            value = loader.construct_scalar(node)
            return time.strptime(value, '%Y-%m-%d %H:%M:%S')
        yaml=YAML(typ="safe")
        yaml.constructor.add_constructor('!struct_time', construct_struct_time)
        return yaml.load(data)
    else:
        # PyYAML fallback
        def struct_time_constructor(loader, node):
            value = loader.construct_scalar(node)
            return time.strptime(value, '%Y-%m-%d %H:%M:%S')
        _pyyaml.SafeLoader.add_constructor('!struct_time', struct_time_constructor)
        return _pyyaml.safe_load(data)


def __cleanup(v):
    if _USE_RUAMEL:
        from ruamel.yaml.scalarstring import LiteralScalarString    
    else:
        LiteralScalarString = str
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
                elif nv in ['0', 0, False]:
                    nd[k] = 0
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