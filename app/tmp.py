import os

PWD = os.path.dirname(__file__)
DIR = os.path.join(PWD, 'parsers')

# Define the old and new imports
old_imports = {
    'from app.objects.secondclass.c_fact import Fact': 'from objects.fact import *',
    'from app.objects.secondclass.c_relationship import Relationship': 'from objects.relationship import *',
    'from app.utility.base_parser import BaseParser': 'from objects.base_parser import *'
}

for plugin in os.listdir(DIR):
    if plugin != '__pycache__':
        print(f"Processing plugin: {plugin}")
        for parser in os.listdir(os.path.join(DIR, plugin)):
            if parser.endswith('.py'):
                parser_path = os.path.join(DIR, plugin, parser)
                
                # Read the content of the file
                with open(parser_path, 'r') as f:
                    content = f.read()

                # Replace the old import statements with the new ones
                for old_import, new_import in old_imports.items():
                    content = content.replace(old_import, new_import)
                
                # Write the modified content back to the file
                with open(parser_path, 'w') as f:
                    f.write(content)
                
                print(f"Updated imports in: {parser}")
