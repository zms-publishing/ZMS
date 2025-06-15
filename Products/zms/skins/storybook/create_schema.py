#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This script extracts schema definitions from a TAL file and saves them to a new file.
# Make sure to adjust the paths as needed.
# extract_schema('path/to/your/tal_file.zpt', 'path/to/output/tal_file.json')

# #####################################################################################
# IMPORTANT NOTE: Define the input and output file paths
# #####################################################################################
source_dir = '/home/zope/src/zms-publishing/ZMS5/Products/zms/skins/storybook/'
datakey = 'schema'
# #####################################################################################

# Imports
import os
import re
import json
from bs4 import BeautifulSoup as bs

# #####################################################################################
# Function to guess the data type based on the HTML tag name
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
# Function to extract schema from a TAL file
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
                'mandatory': element.get(f'{attr_prefix}-mandatory', '0'),
                'multilang': element.get(f'{attr_prefix}-multilang', '1'),
                'repetitive': element.get(f'{attr_prefix}-repetitive', '0'),
                'default': element.get(f'{attr_prefix}-default', '')
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
                    'package':f'com.zms.{classname.lower()}',
                    'revision':'0.0.1',
                    'enabled':1,
                    'insert_custom':'{$}',
                    'insert_deny':[],
                    'delete_deny':[],
                    'attrs': { }
                }
            }
    # Add the schema attributes to the schema dictionary
    for match in matches:
        key, value = match
        schema['class']['attrs'][key] = value

    # Write the schema to the output file
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        # Write the schema-dict as a JSON-like format
        output_file.write(json.dumps(schema, indent=4, ensure_ascii=False))
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
    content = re.sub(r'\s*data-{}-[^=]+="[^"]*"\s*'.format(datakey), ' ', content)
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
            os.makedirs(os.path.join(source_dir, 'schema', f0), exist_ok=True)
            # Define the output file path
            output_file_path = os.path.join(source_dir, 'schema', f0, 'init.json')
            print(f'Processing {tal_file_path}...')
            # Call function to extract schema
            has_extracted = extract_schema(f0, tal_file_path, output_file_path)
            if has_extracted:
                print(f'Schema for {f0} saved to {output_file_path}')
                save_standard_html(f0, tal_file_path, os.path.join(source_dir, 'schema', f0, 'standard_html.zpt'))
                print(f'Standard HTML for {f0} saved to {os.path.join(source_dir, "schema", f0, "standard_html.zpt")}')
            else:
                print(f'No schema found for {f0}, skipping...')
            print('-' * 40)
