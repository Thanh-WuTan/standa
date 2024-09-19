import zipfile
import os
import tempfile
import yaml
import pathlib
import json

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
        temp_dir = tempfile.mkdtemp(dir=tmp_parent_dir)
        return temp_dir
    
    async def get_atomic_ordering(self, adversary_id):
        adversary = await self.data_svc.locate('adversaries', match=dict(adversary_id=adversary_id))
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
            uuid_mapper = {}
            for payload in payloads:
                id, obfuscation_name = self.services.get('file_svc').get_payload_id_from_name(payload)
                uuid_mapper[id] = {"name": payload, "obfuscation": obfuscation_name}
            json.dump(uuid_mapper, uuid_mapper_file, indent=4)    
        return payloads_dir

    async def download_standalone_agent(self, adversary_id):
        temp_dir = await self.create_tmp_dir()
        abilities = await self.get_atomic_ordering(adversary_id)
        abilities_dir = await self.create_abilities_dir(temp_dir, abilities)
        payloads_dir = await self.create_payloads_dir(temp_dir, abilities)
        
        # Create the zip file
        zip_path = os.path.join(temp_dir, adversary_id + ".zip")
             
        with zipfile.ZipFile(zip_path, 'w') as zip_file:
            for root, _, files in os.walk(abilities_dir):
                for file in files:
                    zip_file.write(os.path.join(root, file), arcname=os.path.relpath(os.path.join(root, file), temp_dir))
            for root, _, files in os.walk(payloads_dir):
                for file in files:
                    zip_file.write(os.path.join(root, file), arcname=os.path.relpath(os.path.join(root, file), temp_dir))

        return zip_path
