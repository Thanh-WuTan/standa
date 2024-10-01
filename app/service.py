import zipfile
import os
import tempfile
import yaml
import pathlib
import json

PWD = os.path.dirname(__file__)
MYAGENT_DIR = os.path.join(PWD, '..', 'agent')

class StandaService:
    def __init__(self, services):
        self.services = services
        self.data_svc = services.get('data_svc')

    async def find_payload(self, payload_name):
        cwd = pathlib.Path.cwd()
        payload_dirs = [cwd / 'data' / 'payloads']
        payload_dirs.extend(cwd / 'plugins' / plugin.name / 'payloads'
                            for plugin in await self.data_svc.locate('plugins') if plugin.enabled)

        # Search for the payload file in the specified directories
        for payload_dir in payload_dirs:
            payload_path = payload_dir / payload_name
            if payload_path.exists() and payload_path.is_file():
                return payload_path
        return None

    async def create_tmp_dir(self):
        current_dir = os.path.dirname(__file__)
        tmp_parent_dir = os.path.join(current_dir, '..', 'tmp')
        os.makedirs(tmp_parent_dir, exist_ok=True)
        temp_dir = tempfile.mkdtemp(dir=tmp_parent_dir)
        return temp_dir
    
    async def get_atomic_ordering(self, adversary_id):
        try:
            adversary = await self.data_svc.locate('adversaries', match=dict(adversary_id=adversary_id))
        except Exception as e:
            print(f"Error locating adversary '{adversary_id}': {e}")
            return None
        if not adversary:
            return None
        profile = adversary[0].display
        atomic_ordering = profile['atomic_ordering']
        abilities = []
        for ability_id in atomic_ordering:
            ability = await self.data_svc.locate('abilities', match=dict(ability_id=ability_id))
            abilities.append(ability[0].display)
        return abilities

    async def create_abilities_dir(self, temp_dir, abilities):
        abilities_dir = os.path.join(temp_dir, 'abilities')
        os.makedirs(abilities_dir, exist_ok=True)
        for position, ability in enumerate(abilities, start=1):
            try:
                yml_filename = f'{position}.yml'
                yml_path = os.path.join(abilities_dir, yml_filename)
                with open(yml_path, 'w') as yml_file:
                    yaml.dump(ability, yml_file)
            except Exception as e:
                print(f"Error creating ability file for '{ability['name']}': {e}")
        return abilities_dir

    async def create_payloads_dir(self, temp_dir, abilities): 

        def get_payloads(file_svc):
            payloads = {}
            for t in ['standard_payloads', 'special_payloads']:
                for k, v in file_svc.get_config(prop=t, name='payloads').items():
                    obfuscation_name = ''
                    if v.get('obfuscation_name'):
                        obfuscation_name = v['obfuscation_name'][0]
                    id = v['id']   
                    payloads[id] = {
                        'name': k,
                        'obfuscation': obfuscation_name,
                    }
            return payloads
        payloads_dir = os.path.join(temp_dir, 'payloads')
        os.makedirs(payloads_dir, exist_ok=True)
        
        payloads = set()
        for ability in abilities:
            for exc in ability['executors']:
                for payload in exc['payloads']:
                    payloads.add(payload)
        for payload in payloads:
            try: 
                payload_path = await self.find_payload(payload)
                if payload_path:
                    os.makedirs(payloads_dir, exist_ok=True)
                    payload_save_path = os.path.join(payloads_dir, payload)
                    with open(payload_save_path, 'wb') as dest_file:
                        with open(payload_path, 'rb') as src_file:
                            dest_file.write(src_file.read())
                else:
                    print(f"Payload '{payload}' not found.")
            except Exception as e:
                print(f"Error creating payload file for '{ability['name']}': {e}")

        # Create uuid_mapper file
        uuid_mapper_path = os.path.join(payloads_dir, 'uuid_mapper.json')
        with open(uuid_mapper_path, 'w') as uuid_mapper_file:
            uuid_mapper = get_payloads(self.services.get('file_svc'))
            json.dump(uuid_mapper, uuid_mapper_file, indent=4)
        return payloads_dir
    
    async def create_parsers_dir(self, temp_dir, abilities):
        parsers_dir = os.path.join(temp_dir, 'parsers')
        os.makedirs(parsers_dir, exist_ok=True)
        for ability in abilities:
            for exc in ability['executors']:
                for parser in exc['parsers']:
                    module = parser['module'].split('.')
                    plugin = module[1]
                    parser_name = module[-1] + '.py'
                    os.makedirs(os.path.join(parsers_dir, plugin), exist_ok=True)
                    await self.copy_file(os.path.join(PWD, 'parsers', plugin, parser_name),
                                   os.path.join(parsers_dir, plugin, parser_name))
        return parsers_dir
    
    async def create_requirements_dir(self, temp_dir, abilities):
        requirements_dir = os.path.join(temp_dir, 'requirements')
        os.makedirs(requirements_dir, exist_ok=True)
        
        os.makedirs(os.path.join(requirements_dir, 'response'), exist_ok=True) 
        await self.copy_file(os.path.join(PWD, 'requirements', 'response', 'base_requirement.py'),
                             os.path.join(requirements_dir, 'response', 'base_requirement.py'))
       
        os.makedirs(os.path.join(requirements_dir, 'stockpile'), exist_ok=True)       
        await self.copy_file(os.path.join(PWD, 'requirements', 'stockpile', 'base_requirement.py'),
                             os.path.join(requirements_dir, 'stockpile', 'base_requirement.py'))

        for ability in abilities:
            for requirement in ability['requirements']:
                module = requirement['module'].split('.')
                plugin = module[1]
                requirement_name = module[-1] + '.py'
                os.makedirs(os.path.join(requirements_dir, plugin), exist_ok=True)
                await self.copy_file(os.path.join(PWD, 'requirements', plugin, requirement_name),
                                     os.path.join(requirements_dir, plugin, requirement_name))
        return requirements_dir

    async def create_sources_dir(self, temp_dir, source_id):
        sources_dir = os.path.join(temp_dir, 'sources')
        os.makedirs(sources_dir, exist_ok=True)
        try:
            sources = [s.display for s in await self.data_svc.locate('sources')]
            source = None
            for s in sources:
                if s['id'] == source_id:
                    source = s
                    break
            if source is None:
                print(f"Source '{source_id}' not found.")
                return None
            source_file = os.path.join(sources_dir, '{source_id}.yml'.format(source_id=source_id))
            with open(source_file, 'w') as f:
                yaml.dump(source, f)
        except Exception as e:
            print(f"Error locating source '{source_id}': {e}")
            return None
        return sources_dir

    async def copy_file(self, source, destination):
        try:
            with open(destination, 'wb') as dest_file:
                with open(source, 'rb') as src_file:
                    dest_file.write(src_file.read())
        except Exception as e:
            print(f"Error copying {source}: {e}")
        return destination
    
    async def copy_folder(self, temp_dir, target):
        destination_dir = os.path.join(temp_dir, target)
        os.makedirs(destination_dir, exist_ok=True)

        source_dir = os.path.join(MYAGENT_DIR, target) 
        for file_name in os.listdir(source_dir):
            source_file = os.path.join(source_dir, file_name)
            destination_file = os.path.join(destination_dir, file_name)
            if os.path.isfile(source_file):
                await self.copy_file(source_file, destination_file)
        return destination_dir

    async def download_standalone_agent(self, adversary_id, source_id, platform):
        temp_dir = await self.create_tmp_dir()
        abilities = await self.get_atomic_ordering(adversary_id)
        abilities_dir = await self.create_abilities_dir(temp_dir, abilities)
        payloads_dir = await self.create_payloads_dir(temp_dir, abilities)
        parsers_dir = await self.create_parsers_dir(temp_dir, abilities)
        requirements_dir = await self.create_requirements_dir(temp_dir, abilities)
        sources_dir = await self.create_sources_dir(temp_dir, source_id)
        objects_dir = await self.copy_folder(temp_dir, 'objects')
        learning_dir = await self.copy_folder(temp_dir, 'learning')
        
        main_agent_file = await self.copy_file(os.path.join(MYAGENT_DIR, 'main.py'), os.path.join(temp_dir, 'main.py'))

        with open(main_agent_file, 'r') as f:
            content = f.read() 
        content = content.replace("ADV_ID = 'adversary_id'", f"ADV_ID = '{adversary_id}'")
        content = content.replace("platform='selected_platform'", f"platform='{platform}'")
        with open(main_agent_file, 'w') as f:
            f.write(content)
        
        requirements_file = await self.copy_file(os.path.join(MYAGENT_DIR, 'requirements.txt'), os.path.join(temp_dir, 'requirements.txt'))
        
        directories = [abilities_dir, payloads_dir, objects_dir, parsers_dir, requirements_dir, learning_dir, sources_dir]
        
        # Create the zip file
        zip_path = os.path.join(temp_dir, adversary_id + ".zip")
             
        with zipfile.ZipFile(zip_path, 'w') as zip_file:
            for dir in directories:
                for root, _, files in os.walk(dir):
                    for file in files:
                        zip_file.write(os.path.join(root, file), arcname=os.path.relpath(os.path.join(root, file), temp_dir))
            zip_file.write(main_agent_file, arcname=os.path.relpath(main_agent_file, temp_dir))
            zip_file.write(requirements_file, arcname=os.path.relpath(requirements_file, temp_dir))
        return zip_path

    async def get_parser_modules(self):
        app_svc = self.services.get('app_svc')
        plugins_directory = os.path.join(PWD, '..', '..')
        standa_parsers_directory = os.path.join(plugins_directory, 'standa', 'app', 'parsers')
        os.makedirs(standa_parsers_directory, exist_ok=True)
        for plugin in app_svc.get_config('plugins'):
            if plugin == 'standa':
                continue
            plugin_parsers_dir = os.path.join(plugins_directory, plugin, 'app', 'parsers')
            if not os.path.isdir(plugin_parsers_dir):
                continue
            os.makedirs(os.path.join(standa_parsers_directory, plugin), exist_ok=True)  
            for filename in os.listdir(plugin_parsers_dir):
                source_file = os.path.join(plugin_parsers_dir, filename)
                destination_file = os.path.join(standa_parsers_directory, plugin, filename)
                if os.path.isfile(source_file):  # Ensure it's a file
                    with open(source_file, 'r') as src:
                        content = src.read()
                    # Perform replacements
                    content = content.replace(
                        'from app.objects.secondclass.c_fact import Fact',
                        'from objects.fact import *'
                    ).replace(
                        'from app.objects.secondclass.c_relationship import Relationship',
                        'from objects.relationship import *'
                    ).replace(
                        'from app.utility.base_parser import BaseParser',
                        'from objects.base_parser import *'
                    ).replace(
                        'mp.source', "mp['source']"
                    ).replace(
                        'mp.target', "mp['target']"
                    ).replace(
                        'mp.edge', "mp['edge']"
                    )
                    with open(destination_file, 'w') as dst:
                        dst.write(content)
                        
    async def get_requirements_modules(self):
        app_svc = self.services.get('app_svc')
        plugins_directory = os.path.join(PWD, '..', '..')
        standa_requirements_directory = os.path.join(plugins_directory, 'standa', 'app', 'requirements')
        os.makedirs(standa_requirements_directory, exist_ok=True)
        for plugin in app_svc.get_config('plugins'):
            if plugin == 'standa':
                continue
            plugin_requirements_dir = os.path.join(plugins_directory, plugin, 'app', 'requirements')
            if not os.path.isdir(plugin_requirements_dir):
                continue
            os.makedirs(os.path.join(standa_requirements_directory, plugin), exist_ok=True)  
            for filename in os.listdir(plugin_requirements_dir):
                source_file = os.path.join(plugin_requirements_dir, filename)
                destination_file = os.path.join(standa_requirements_directory, plugin, filename)
                if os.path.isfile(source_file):
                    with open(source_file, 'r') as src:
                        content = src.read()
                    content = content.replace(
                        'from plugins.stockpile.app.requirements.base_requirement import BaseRequirement',
                        'from requirements.stockpile.base_requirement import BaseRequirement'
                    ).replace(
                        'from plugins.response.app.requirements.base_requirement import BaseRequirement',
                        'from requirements.response.base_requirement import BaseRequirement'
                    ).replace(
                        'from app.objects.c_operation import Operation',
                        'from objects.operation import *'
                    ).replace(
                        'from app.objects.secondclass.c_link import Link',
                        'from objects.link import *'
                    ).replace(
                        'async ', ''  # Remove the 'async' keyword
                    ).replace(
                        'await ', ''  # Remove the 'await' keyword
                    )
                    with open(destination_file, 'w') as dst:
                        dst.write(content)
