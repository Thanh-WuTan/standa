import re

class Agent: 

    re_base64 = re.compile('[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', flags=re.DOTALL)

    RESERVED = dict(server='#{server}', group='#{group}', agent_paw='#{paw}', location='#{location}',
                    exe_name='#{exe_name}', upstream_dest='#{upstream_dest}',
                    payload=re.compile('#{payload:(.*?)}', flags=re.DOTALL))
    
    def __init__(self, platform = "unknown", privilege = 0):
        self.platform = platform
        self.executors = ['sh'] if platform == 'linux' else ['psh', 'cmd']
        self.privilege = privilege
  
    
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
    

    def get_payload_name_from_uuid(self, uuid, uuid_mapper):
        if uuid in uuid_mapper:
            if uuid_mapper[uuid]['obfuscation']:
                return uuid, uuid_mapper[uuid]['obfuscation']
            return uuid, uuid_mapper[uuid]['name'] 
        return uuid, uuid

    def _replace_payload_data(self, command, uuid_mapper):
        for uuid in re.findall(self.RESERVED['payload'], command):
            if self.is_uuid4(uuid):
                _, display_name = self.get_payload_name_from_uuid(uuid, uuid_mapper)
                command = command.replace('#{payload:%s}' % uuid, display_name)
        return command


    def replace(self, command, uuid_mapper):
        # command = command.replace(self.RESERVED['server'], self.server)
        # command = command.replace(self.RESERVED['group'], self.group)
        # command = command.replace(self.RESERVED['agent_paw'], self.paw)
        # command = command.replace(self.RESERVED['location'], self.location)
        # command = command.replace(self.RESERVED['exe_name'], self.exe_name)
        # command = command.replace(self.RESERVED['upstream_dest'], self.upstream_dest)
        command = self._replace_payload_data(command, uuid_mapper) 
        return command
    