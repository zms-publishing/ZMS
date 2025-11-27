"""Version information for ZMS package."""
import os
import re

def _read_version():
    """Read and parse version from version.txt file."""
    version_file = os.path.join(os.path.dirname(__file__), 'version.txt')
    with open(version_file, 'r') as f:
        raw_version = f.read()
    # Remove text from version for PyPI
    cleaned_version = re.sub(r'ZMS\d*-', '', raw_version).replace('.REV', '')
    version_list = cleaned_version.strip().split('.')
    # Remove revision too
    if len(version_list) == 4:
        version_list.pop()
    return '.'.join(version_list)

__version__ = _read_version()
