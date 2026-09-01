#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This script extracts schema definitions from a TAL file and saves them to a new file.
# Make sure to adjust the paths as needed.
# extract_schema('path/to/your/tal_file.zpt', 'path/to/output/tal_file.json')

# #####################################################################################
# IMPORTANT NOTE: Define the input and output file paths
# #####################################################################################
source_dir = '/home/zope/src/zms-publishing/ZMS5/Products/zms/skins/storybook/'
package_name = 'com.zms.custom'
datakey = 'schema'
# #####################################################################################

# Imports
import os
import re
import json
import yaml
from bs4 import BeautifulSoup as bs
from Products.zms import standard
from chameleon import PageTemplate

# #####################################################################################
# Function: Guess the data type based on the HTML tag name
# #####################################################################################
def guess_data_type(html_tag_name):
    """
    Guess the ZMS data type based on the HTML tag name.
    """
    if html_tag_name in ['textarea']:
        return 'text'
    elif html_tag_name in ['select']:
        return 'select'
    elif html_tag_name in ['img']:
        return 'image'
    elif html_tag_name in ['a']:
        return 'url'
    else:
        return 'string'

# #####################################################################################
# Function: Extract Schema from a TAL File as a Dictionary
# #####################################################################################
def extract_schema(classname, tal_file_path, output_file_path):
    """
    Extract schema definitions from a TAL file and save them to a JSON file.
    :param classname: The name of the class to be used in the schema.
    :param tal_file_path: The path to the TAL file.
    :param output_file_path: The path where the schema JSON file will be saved.
    """
    with open(tal_file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Parse the content with BeautifulSoup
    soup = bs(content, 'html.parser')

    # List all html elements that have a data-schema attribute
    schema_elements = soup.find_all(lambda tag: any(attr.startswith(f'data-{datakey}-') for attr in tag.attrs))
    matches = []

    # Iterate over the schema elements and extract the attributes
    for element in schema_elements:
        # Get the kinds of available schema definitions 
        # according to the pattern data-{datakey}-* and data-{datakey}-attr-{attrname}-*
        schema_sets = list(set([a.split('-')[3] for a in element.attrs if a.startswith(f'data-{datakey}-attr-')]))
        schema_sets.extend(list(set([a.split('-')[0] for a in element.attrs if a.startswith(f'data-{datakey}-') and not a.startswith(f'data-{datakey}-attr-')])))

        for schema_set in schema_sets:
            attr_prefix = schema_set=='data' and f'data-{datakey}' or f'data-{datakey}-attr-{schema_set}'

            # Create Default values for id, type, name, etc.
            default_type = guess_data_type(element.name)
            default_id = f'{element.name}_'
            if 'class' in element.attrs:
                default_id += '_'.join(element['class'])
            default_id = default_id.lower()
            default_name = element.get(f'{attr_prefix}-id', default_id).capitalize()

            # Collect schema set data
            matches.append((element.get(f'{attr_prefix}-id', default_id), {
                'id': element.get(f'{attr_prefix}-id', default_id),
                'type': element.get(f'{attr_prefix}-type', default_type),
                'name': element.get(f'{attr_prefix}-name', default_name),
                'mandatory': element.get(f'{attr_prefix}-mandatory', 0),
                'multilang': element.get(f'{attr_prefix}-multilang', 1),
                'repetitive': element.get(f'{attr_prefix}-repetitive', 0),
                'default': element.get(f'{attr_prefix}-default', ''),
                'keys': [],
                'sort_id': int(element.get(f'{attr_prefix}-sort_id', 0)),
            }))

    # If no schema elements found, print a message and exit
    if not matches:
        print(f'No schema elements found.')
        return False

    # Create a Dictionary to hold the Schema
    schema = { 'class': {
                    'id':classname,
                    'type':'ZMSObject',
                    'name':classname.capitalize(),
                    'package':package_name,
                    'revision':'0.0.1',
                    'enabled':1,
                    'access': {
                        'delete_custom':'',
                        'delete_deny':[],
                        'insert_custom':'{$}',
                        'insert_deny':[],
                        'delete_deny':[]
                    },
                    'Attrs': { }
                }
            }

    # Sort the matches by sort_id and then by id
    matches.sort(key=lambda x: (x[1]['sort_id'], x[0]))
    # Remove the sort_id from the schema attributes
    for match in matches:
        key, value = match
        if 'sort_id' in value:
            del value['sort_id']
        # Ensure the keys are sorted alphabetically
        value['keys'] = sorted(value.get('keys', []))

    # Add the schema attributes to the schema dictionary
    for match in matches:
        key, value = match
        if 'sort_id' in value:
            del value['sort_id']
        schema['class']['Attrs'][key] = value

    # Add fontawesome icon
    schema['class']['Attrs']['icon_clazz'] = {
        'id': 'icon_clazz',
        'type': 'constant',
        'name': 'Icon Class',
        'mandatory': 0,
        'multilang': 0,
        'repetitive': 0,
        'custom': 'fa fa-puzzle-piece',
        'keys': []
    }

    # Finally add the standard_html attribute to the schema dictionary
    schema['class']['Attrs']['standard_html'] = {
        'id': 'standard_html',
        'type': 'zpt',
        'name': 'Standard-Template (ZPT)',
        'mandatory': 0,
        'multilang': 0,
        'repetitive': 0,
        'default': '',
        'keys': []
    }

    return schema

# #####################################################################################
# Function: Save the Schema as a JSON File
# #####################################################################################
def save_schema_as_json(schema, output_file_path):
    """
    Save the schema dictionary to a JSON file.
    :param schema: The schema dictionary to be saved.
    :param output_file_path: The path where the JSON file will be saved.
    """
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        # Write the schema-dict as a JSON-like format
        output_file.write(json.dumps(schema, indent=4, ensure_ascii=False))
    return True

# #####################################################################################
# Function: Save the Schema as a Python File
# #####################################################################################
def save_schema_as_python(schema, output_file_path):
    """
    Save the schema dictionary to a Python file.
    :param schema: The schema dictionary to be saved.
    :param output_file_path: The path where the Python file will be saved.
    """
    python_file = os.path.join(output_file_path, '__init__.py')
    with open(python_file, 'w', encoding='utf-8') as output_file:
        output_file.write('class %s:\n'% schema['class']['id'])
        output_file.write(f'\t"""\n\tpython-representation of {schema['class']['id']}\n\t"""\n\n')
        # Sort keys alphabetically
        for key, value in sorted(schema['class'].items()):
            # Skip the 'Attrs' dictionary, as it will be handled separately
            if key != 'Attrs':
                value = standard.str_json(value, encoding="utf-8", formatted=True, level=2, allow_booleans=False)
                output_file.write(f'\t# {key.capitalize()}\n')
                output_file.write(f'\t{key} = {value}\n\n')
        # Write the 'Attr' dictionary
        output_file.write('\t# Attrs\n\tclass Attrs:\n')
        for key, value in schema['class']['Attrs'].items():
            value = standard.str_json(value, encoding="utf-8", formatted=True, level=3, allow_booleans=False)
            output_file.write(f'\t\t{key} = {value}\n\n')
    return True


# #####################################################################################
# Function to Save the Schema as a YAML File
# #####################################################################################
def save_schema_as_yaml(schema, output_file_path):
    """
    Save the schema dictionary to a YAML file.
    :param schema: The schema dictionary to be saved.
    :param output_file_path: The path where the YAML file will be saved.
    """

    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        class CustomDumper(yaml.Dumper):
            pass
        # Preserve the order of elements in the dictionary when dumping to YAML
        CustomDumper.add_representer(dict, lambda dumper, data: dumper.represent_dict(data.items()))
        yaml.dump(schema, output_file, allow_unicode=True, default_flow_style=False, Dumper=CustomDumper)
    return True


# #####################################################################################
# Function to save the standard HTML file after preprocessing
# #####################################################################################
def save_standard_html(classname, tal_file_path, output_file_path):
    """
    Preprocess TAL file for utilizing it as metaobj.standard_hml.zpt in ZMS.
    :param classname: The name of the class to be used in the schema.
    :param tal_file_path: The path to the TAL file.
    :param output_file_path: The path where the schema JSON file will be saved.
    """
    with open(tal_file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Remove all data-schema attributes using the datakey variable and regex
    # content = re.sub(r'\s*data-{}-[^=]+="[^"]*"\s*'.format(datakey), ' ', content)
    # This regex will remove multiple all unneccessary spaces 
    # between html-attributes within a  html element
    content = re.sub(r'(?<=[\w"]) +', ' ', content)
    # Remove the link elements with the tal:condition attribute
    content = re.sub(r'<link[^>]*tal:condition="[^"]*"[^>]*>\n', '', content)
    # Make HTML comments filtered by Zope
    content = re.sub(r'<!--(.*?)-->', r'<!--!\1-->', content, flags=re.DOTALL)

    # Save the modified content to the output folder as standard_html.zpt
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        output_file.write(content)
    return True

def save_zpt_as_html(tal_file_path, output_file_path):
    """
    Convert a TAL file to a standard HTML file.
    :param tal_file_path: The path to the TAL file.
    :param output_file_path: The path where the HTML file will be saved.
    """
    with open(tal_file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Remove all data-schema attributes using the datakey variable and regex
    content = re.sub(r'\s*data-{}-[^=]+="[^"]*"\s*'.format(datakey), ' ', content)

    ### Simulate ZMS context
    # ---
    # class zmscontext:
    #     @staticmethod
    #     def attr(key):
    #         return 'fnord'
    # ---
    # Use namedtuple to create a simple class-like structure
    from collections import namedtuple
    zmscontext = namedtuple('zmscontext', ['attr','langmap'])
    # Create a mock zmscontext
    zmscontext.attr = lambda key: None
    zmscontext.langmap = {'ger':'de', 'eng':'en', 'fre':'fr', 'ita':'it', 'spa':'es'}

    # Prepare a minimum parameter-dict for rendering
    template_params = {
        'options': {
            'zmscontext': zmscontext,
        },
        'request': { 'lang': 'ger' },
    }

    # Convert TAL to HTML using Chameleon, render with **kwargs
    template = PageTemplate(content)
    html_content = template.render(**template_params)

    # Save the rendered HTML content to the output file
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        output_file.write(html_content)
    return True

# #####################################################################################
# Main function to iterate over the source directory and process each .zpt file
# #####################################################################################
if __name__ == "__main__":
    print('-' * 40)
    # Iterate over the source directory to find all .zpt files
    for f in os.listdir(source_dir):
        if f.endswith('.zpt'):
            f0 = f.replace('.zpt', '')
            f_schema = f.replace('.zpt', '.json')
            tal_file_path = os.path.join(source_dir, f)
            # Make sure the schema directory exists
            os.makedirs(os.path.join(source_dir, 'schema', package_name, f0), exist_ok=True)
            # Define the output file path
            output_file_path = os.path.join(source_dir, 'schema', f0, '__init__.json')
            print(f'Processing {tal_file_path}...')
            # Call function to extract schema
            extracted_schema = extract_schema(f0, tal_file_path, output_file_path)
            if extracted_schema:
                ### Save the schema as a Python file
                save_schema_as_yaml(extracted_schema, os.path.join(source_dir, 'schema', package_name, f0, '__init__.yaml'))
                ### Save the schema as a Python file
                save_schema_as_python(extracted_schema, os.path.join(source_dir, 'schema', package_name, f0))
                print(f'Schema for {f0} saved as Python to {os.path.join(source_dir, "schema", package_name, f0, "__init__.py")}')
                ### Save the standard HTML file
                save_standard_html(f0, tal_file_path, os.path.join(source_dir, 'schema', package_name, f0, 'standard_html.zpt'))
                print(f'Standard HTML for {f0} saved as TAL to {os.path.join(source_dir, "schema", package_name, f0, "standard_html.zpt")}')
                ### Save the ZPT-template as HTML file
                save_zpt_as_html(tal_file_path, os.path.join(source_dir, 'schema', package_name, f0, 'index.html'))

            else:
                print(f'No schema found for {f0}, skipping...')
            print('-' * 40)
