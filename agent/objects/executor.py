import os
import subprocess
from main import ADV_ID

from objects.result import Result, get_current_timestamp

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
        time_start = get_current_timestamp().replace("Z", ".000Z")
        try:
            if self.name == 'cmd' and self.platform == 'windows':
                res = subprocess.run(['cmd', '/c', self.command], capture_output=True, text=True, timeout=self.timeout)
            elif self.name == 'psh' and self.platform == 'windows':
                res = subprocess.run(['powershell', '-Command', self.command], capture_output=True, text=True, timeout=self.timeout)
            elif self.name == 'sh' and self.platform == 'linux':
                res = subprocess.run(['sh', '-c', self.command], capture_output=True, text=True, timeout=self.timeout)
            else:
                raise ValueError(f"Unsupported executor or platform: {self.name} on {self.platform}")
            result = Result(time_start=time_start, time_stop=get_current_timestamp().replace("Z", ".000Z"), 
                            stdout=res.stdout, stderr=res.stderr)
            return result
        except Exception as e:
            result = Result(time_start=time_start, time_stop=get_current_timestamp().replace("Z", ".000Z"), 
                            stdout="", stderr=str(e))
            return result