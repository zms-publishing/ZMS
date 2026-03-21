"""
yamlutil.py

Provides dump, parse helper functions for general-purpose ZMS utilities and shared helper functions.
It provides common patterns like type checking, data transformation, and error handling.

License: GNU General Public License v2 or later,
Organization: ZMS Publishing
"""

# Imports.
import io
import time

def dump(data):
    from ruamel.yaml import YAML

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


def parse(data):
    from ruamel.yaml import YAML

    # Custom constructor for struct_time
    def construct_struct_time(loader, node):
        value = loader.construct_scalar(node)
        return time.strptime(value, '%Y-%m-%d %H:%M:%S')

    yaml=YAML(typ="safe")
    yaml.constructor.add_constructor('!struct_time', construct_struct_time)
    return yaml.load(data)


def __cleanup(v):
    from ruamel.yaml.scalarstring import LiteralScalarString    
    """
    Recursively cleans up a dictionary by removing keys with falsy values.
    @param v: Input value, typically a dictionary, list, or scalar.
    @type v: C{object}
    @return: Cleaned value with empty entries removed while preserving numeric
        zero and boolean false semantics used by the repository format.
    @rtype: C{object}
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