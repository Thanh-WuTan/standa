import zipfile
import os
import tempfile
import yaml
import aiohttp
import pathlib
import re
from aiohttp import web

class StandaService:
    def __init__(self, services):
        self.services = services
        self.data_svc = services.get('data_svc')

    async def get_adversary_profile(self, adversary_id):
        adversary = await self.data_svc.locate('adversaries', match=dict(adversary_id=adversary_id))
        if not adversary:
            return None
        profile = adversary[0].display
        return profile
    
    async def get_atomic_ordering(self, adversary_id):
        adversary = await self.data_svc.locate('adversaries', match=dict(adversary_id=adversary_id))
        if not adversary:
            return None
        profile = adversary[0].display
        return profile['atomic_ordering']
    
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

    async def create_zip_containing_abilities(self, atomic_ordering):
        current_dir = os.path.dirname(__file__)
        tmp_parent_dir = os.path.join(current_dir, '..', 'tmp')
        temp_dir = tempfile.mkdtemp(dir=tmp_parent_dir)

        # Create subdirectories for abilities and payloads
        abilities_dir = os.path.join(temp_dir, 'abilities')
        os.makedirs(abilities_dir, exist_ok=True)
        
        payloads_dir = os.path.join(temp_dir, 'payloads')
        os.makedirs(payloads_dir, exist_ok=True)

        try:
            payloads = []
            for position, ability_id in enumerate(atomic_ordering, start=1):
                ability = await self.data_svc.locate('abilities', match=dict(ability_id=ability_id))
                
                if ability:
                    ability_data = ability[0].display
                    for exc in ability_data['executors']:
                        for payload in exc['payloads']:
                            payloads.append(payload)

                    yml_filename = f'{position}.yml'
                    yml_path = os.path.join(abilities_dir, yml_filename)
                     
                    with open(yml_path, 'w') as yml_file:
                        yaml.dump(ability_data, yml_file)

            payloads = set(payloads)
            print("Payloads:", payloads)
            
            # Find and save payloads
            for payload in payloads:
                payload_path = await self.find_payload(payload)
                if payload_path:
                    payload_save_path = os.path.join(payloads_dir, payload)
                    # Copy the payload file to the 'payloads' directory
                    with open(payload_save_path, 'wb') as dest_file:
                        with open(payload_path, 'rb') as src_file:
                            dest_file.write(src_file.read())
                else:
                    print(f"Payload '{payload}' not found.")

            # Create the zip file
            zip_path = os.path.join(temp_dir, 'abilities.zip')
             
            with zipfile.ZipFile(zip_path, 'w') as zip_file:
                for root, _, files in os.walk(abilities_dir):
                    for file in files:
                        zip_file.write(os.path.join(root, file), arcname=os.path.relpath(os.path.join(root, file), temp_dir))
                for root, _, files in os.walk(payloads_dir):
                    for file in files:
                        zip_file.write(os.path.join(root, file), arcname=os.path.relpath(os.path.join(root, file), temp_dir))

            return zip_path

        except Exception as e:
            print("Error: ", e)
            return None
     

    @staticmethod
    def is_uuid4(s):
        re_base64 = re.compile('[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', flags=re.DOTALL)
        if re_base64.match(s):
            return True
        return False
    
    async def get_all_payloads(self):
        file_svc= self.services.get('file_svc')
        payloads = file_svc.get_all_payloads()
        res = {}
        for pl in payloads:
            uuid = pl['id']
            res[uuid] = {
                'name': pl['name'],
                'obfuscation': pl['obfuscation']
            }
        return res

    async def do_something(self):
        RESERVED = dict(server='#{server}', group='#{group}', agent_paw='#{paw}', location='#{location}',
                    exe_name='#{exe_name}', upstream_dest='#{upstream_dest}',
                    payload=re.compile('#{payload:(.*?)}', flags=re.DOTALL))
        adversaries = await self.data_svc.locate('adversaries')
        res = []
        file_svc= self.services.get('file_svc')
        for adversary in adversaries:
            adv = adversary.display
            flag = False

            atomic_ordering = adv['atomic_ordering']
            payload_json = {}
            for ability_id in atomic_ordering:
                ability = await self.data_svc.locate('abilities', match=dict(ability_id=ability_id))
                if ability:
                    ab = ability[0].display
                    for exc in ab['executors']:
                        command = exc['command']
                        if command:
                            if "#{payload" in command:
                                flag = True
                                print("--------")
                                print("adv:", adv['name'])
                                cmd = command
                                for uuid in re.findall(RESERVED['payload'], cmd):
                                    if self.is_uuid4(uuid):
                                        try:
                                                
                                            _, display_name = file_svc.get_payload_name_from_uuid(uuid)
                                            cmd = cmd.replace('#{payload:%s}' % uuid, display_name)
                                            print(uuid, display_name)
                                            payload_json[uuid] = display_name
                                        except Exception as e:
                                            print("Error: ", e)
                                print(cmd)

            if flag:
                add = {
                    "name": adv['name'],
                    "plugn": adv['plugin']
                }
                res.append(add)
           
        return payload_json