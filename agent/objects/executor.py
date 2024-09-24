import os
import subprocess
from main import ADV_ID

class Executor:
    def __init__(self, name = 'unknown', platform = 'unknown', command = '', parsers = [], timeout = 10, payloads = []):
        self.name = name
        self.platform = platform
        self.command = command
        self.parsers = self._prepare_parsers(parsers)
        self.timeout = timeout
        self.payloads = payloads

    def _prepare_parsers(self, parsers):
        for parser in parsers:
            module = parser['module'].split('.') 
            plugin = module[1]
            parser_name = module[-1]   
            parser['module'] = "parsers.{plugin}.{parser_name}".format(adversary_id = ADV_ID, plugin=plugin, parser_name=parser_name)    
        return parsers


    def replace_payload_dir(self, command, payload_dir):
        for payload in self.payloads:
            command = command.replace(payload, os.path.join(payload_dir, payload))
        return command

    def run_command(self):
        try:
            if self.name == 'cmd' and self.platform == 'windows':
                result = subprocess.run(['cmd', '/c', self.command], capture_output=True, text=True, timeout=self.timeout)
            elif self.name == 'psh' and self.platform == 'windows':
                result = subprocess.run(['powershell', '-Command', self.command], capture_output=True, text=True, timeout=self.timeout)
            elif self.name == 'sh' and self.platform == 'linux':
                result = subprocess.run(['sh', '-c', self.command], capture_output=True, text=True, timeout=self.timeout)
            else:
                raise ValueError(f"Unsupported executor or platform: {self.name} on {self.platform}")
            return result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return "", 'Command execution timed out'
        else:
            return "", 'Command execution failed'