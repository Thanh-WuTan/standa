import os

class Executor:
    def __init__(self, name = 'unknown', platform = 'unknown', command = '', parsers = [], timeout = 10, payloads = []):
        self.name = name
        self.platform = platform
        self.command = command
        self.parser = parsers
        self.timeout = timeout
        self.payloads = payloads

    def replace_payload_dir(self, command, payload_dir):
        # for payload in self.payloads:
        #     command = command.replace(payload, os.path.join(payload_dir, payload))
        print("---------------")
        print("Command: ", command)
        print("Payloads: ", self.payloads)
        return command

    def run_command(self):
       
        return None, None