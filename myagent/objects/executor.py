import os
import subprocess


class Executor:
    def __init__(self, name = 'unknown', platform = 'unknown', command = '', parsers = [], timeout = 10, payloads = []):
        self.name = name
        self.platform = platform
        self.command = command
        self.parser = parsers
        self.timeout = timeout
        self.payloads = payloads

    def replace_payload_dir(self, command, payload_dir):
        for payload in self.payloads:
            command = command.replace(payload, os.path.join(payload_dir, payload))
        return command

    def run_command(self):
        if self.name == 'cmd' and self.platform == 'windows':
            result = subprocess.run(['cmd', '/c', self.command], capture_output=True, text=True)
        elif self.name == 'psh' and self.platform == 'windows':
            result = subprocess.run(['powershell', '-Command', self.command], capture_output=True, text=True)
        elif self.name == 'sh' and self.platform == 'linux':
            result = subprocess.run(['sh', '-c', self.command], capture_output=True, text=True)
        else:
            raise ValueError(f"Unsupported executor or platform: {self.name} on {self.platform}")
        return result.stdout, result.stderr