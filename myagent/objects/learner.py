import re
import glob

from importlib import import_module

class Learner:

    def __init__(self):
        self.re_variable = re.compile(r'#{(.*?)}', flags=re.DOTALL)
        self.model = set()
        self.parsers = self.add_parsers('learning') 
    
    @staticmethod
    def add_parsers(directory):
        parsers = []
        for filepath in glob.iglob('%s/**.py' % directory):
            module = import_module(filepath.replace('/', '.').replace('\\', '.').replace('.py', ''))
            print(module)
            parsers.append(module.Parser())
        return parsers
    
    def build_model(self, abilities = []):
        for ability in abilities:
            for executor in ability['executors']:
                if executor['command']:
                    variables = frozenset(re.findall(self.re_variable, executor['command']))
                    if len(variables) > 1:  # relationships require at least 2 variables
                        self.model.add(variables)
        self.model = set(self.model)

    def learn(source, link, result):
        pass