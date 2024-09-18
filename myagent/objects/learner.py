import re

from importlib import import_module

class Learner:

    def __init__(self):
        self.re_variable = re.compile(r'#{(.*?)}', flags=re.DOTALL)
        self.model = set()
    
    def build_model(self, abilities = []):
        for ability in abilities:
            for executor in ability['executors']:
                if executor['command']:
                    variables = frozenset(re.findall(self.re_variable, executor['command']))
                    if len(variables) > 1:  # relationships require at least 2 variables
                        self.model.add(variables)
        self.model = set(self.model)
