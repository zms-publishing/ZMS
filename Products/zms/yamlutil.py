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

import json
import re

def parse_yaml(data):
    # Convert YAML-like data to JSON-like data
    def yaml_to_json(data):
        data = re.sub(r'(?m)^(\s*)([^:\s]+):', r'\1"\2":', data)  # Quote keys
        data = re.sub(r'(?m):\s*([^,\s]+)', r': "\1"', data)       # Quote values
        return data

    json_data = yaml_to_json(data)
    return json.loads(json_data)