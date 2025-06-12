# -*- coding: utf-8 -*-
# This script extracts schema definitions from a TAL file and saves them to a new file.
# Make sure to adjust the paths as needed.
# extract_schema('path/to/your/tal_file.zpt', 'path/to/output/tal_file.json')

# #####################################################################################
# IMPORTANT NOTE: Define the input and output file paths
# #####################################################################################
source_dir = '/home/zope/src/zms-publishing/ZMS5/Products/zms/skins/storybook/'

import os
import re
import json
from bs4 import BeautifulSoup as bs

def extract_schema(tal_file_path, output_file_path):
    with open(tal_file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Parse the content with BeautifulSoup
    soup = bs(content, 'html.parser')

    # Find all html elements that have a data-schema attribute
    # This will match attributes like data-schema-id, data-schema-type, etc.
    schema_elements = soup.find_all(lambda tag: any(attr.startswith('data-schema-') for attr in tag.attrs))
    schema_pattern = re.compile(r'data-schema-.*')
    # List to hold the schema matches
    matches = []
    # Iterate over the schema elements and extract the attributes
    for element in schema_elements:
        # Find all attributes that match the schema pattern
        for attr in element.attrs:
            match = schema_pattern.match(attr)
            if match:
                # Store the schema information as a tuple
                matches.append((element.get('data-schema-id', ''), {
                    'id': element.get('data-schema-id', ''),
                    'type': element.get('data-schema-type', ''),
                    'name': element.get('data-schema-name', ''),
                    'mandatory': element.get('data-schema-mandatory', '0'),
                    'multilang': element.get('data-schema-multilang', '0'),
                    'repetitive': element.get('data-schema-repetitive', '0'),
                    'default': element.get('data-schema-default', '')
                }))
    # If no schema elements found, print a message and exit
    if not matches:
        print(f'No schema elements found in {tal_file_path}')
        return

    # Create a dictionary to hold the schema
    schema = {}
    for match in matches:
        key, value = match
        schema[key] = value

    # Write the schema to the output file
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        # Write the schema-dict as a JSON-like format
        output_file.write(json.dumps(schema, indent=4, ensure_ascii=False))
    print(f'Schema extracted to {output_file_path}')


if __name__ == "__main__":
    # Iterate over the source directory to find all .zpt files
    for f in os.listdir(source_dir):
        if f.endswith('.zpt'):
            f_zpt = f
            f_schema = f_zpt.replace('.zpt', '.json')
            tal_file_path = os.path.join(source_dir, f_zpt)
            output_file_path = os.path.join(source_dir, 'schema/', f_schema)
            print(f'Processing {tal_file_path}...')
            # Call the function to extract schema
            extract_schema(tal_file_path, output_file_path)
            # If you want to extract schema from all .zpt files, you can uncomment the following line

    # Call the function to extract schema
    extract_schema(tal_file_path, output_file_path)

