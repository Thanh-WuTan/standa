import re
import string

from random import randint, choice


class Agent: 

    re_base64 = re.compile('[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', flags=re.DOTALL)

    RESERVED = dict(server='#{server}', group='#{group}', agent_paw='#{paw}', location='#{location}',
                    exe_name='#{exe_name}', upstream_dest='#{upstream_dest}',
                    payload=re.compile('#{payload:(.*?)}', flags=re.DOTALL))
    
    def __init__(self, platform = "unknown", server = "unknown", privilege = 0, uuid_mapper = None):
        self.platform = platform.lower()
        self.executors = ['sh'] if self.platform == 'linux' else ['psh', 'cmd']
        self.privilege = privilege
        self.paw = self.generate_name(size=6)
        self.server = server
        self.uuid_mapper = uuid_mapper

    @staticmethod
    def generate_name(size=16):
        return ''.join(choice(string.ascii_lowercase) for _ in range(size))
    
    def find_executors(self, ability):
        executors = []
        for executor in ability['executors']:
            if executor['platform'] == self.platform and executor['name'] in self.executors:
                executors.append(executor)
        return executors

    def is_capable_to_run(self, ability):
        if ability['privilege'] == 'Elevated' and self.privilege == 0:
            return False
        for executor in ability['executors']:
            if executor['platform'] == self.platform and executor['name'] in self.executors:
                return True
        return False
     
    def is_uuid4(self, s):
        if self.re_base64.match(s):
            return True
        return False
    

    def get_payload_name_from_uuid(self, uuid):
        if uuid in self.uuid_mapper:
            if self.uuid_mapper[uuid]['obfuscation']:
                return uuid, self.uuid_mapper[uuid]['obfuscation']
            return uuid, self.uuid_mapper[uuid]['name'] 
        return uuid, uuid

    def _replace_payload_data(self, command):
        for uuid in re.findall(self.RESERVED['payload'], command):
            if self.is_uuid4(uuid):
                _, display_name = self.get_payload_name_from_uuid(uuid)
                command = command.replace('#{payload:%s}' % uuid, display_name)
        return command


    def replace(self, command):
        command = command.replace(self.RESERVED['server'], self.server)
        command = command.replace(self.RESERVED['agent_paw'], self.paw)
        # command = command.replace(self.RESERVED['group'], self.group)
        # command = command.replace(self.RESERVED['location'], self.location)
        # command = command.replace(self.RESERVED['exe_name'], self.exe_name)
        # command = command.replace(self.RESERVED['upstream_dest'], self.upstream_dest)
        command = self._replace_payload_data(command) 
        return command
    