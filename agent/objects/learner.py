import re
import glob
import itertools

from importlib import import_module
from objects.link import update_scores
from objects.relationship import Relationship

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

    def learn(self, operation, link, blob):
        facts = operation.all_facts()
        found_facts = [] 
        for parser in self.parsers:
            try:
                for fact in parser.parse(blob):
                    found_facts.append(fact)
            except Exception as e:
                print("Error while parsing: %s" % (e))
        update_scores(increment=len(found_facts), used=facts, operation=operation)
        self._store_results(link, found_facts, operation)

    def _save(self, link, result, operation, executor, step_order):
        if link.executor.parsers:
            link.parse(result.stdout, operation)
        else: 
            self.learn(operation, link, result.stdout)
        
        step = {
            "command": executor.command,
            "executor": executor.name,
            "order": step_order,
            "time-start": result.time_start,
            "time-stop": result.time_stop,
            "output": [
                {
                    "content": result.stdout,
                    "level": "STDOUT",
                    "type": "console"
                },
                {
                    "content": result.stderr,
                    "level": "STDERR",
                    "type": "console"
                }
            ]
        }
        return step


    def _store_results(self, link, facts, operation):
        facts_covered = []
        for relationship in self.model:
            matches = []
            for fact in facts:
                if fact.trait in relationship:
                    matches.append(fact)
                    facts_covered.append(fact)
            for pair in itertools.combinations(matches, r=2):
                if pair[0].trait != pair[1].trait:
                    link.create_relationships([Relationship(source=pair[0], edge='has', target=pair[1])])
        for f in [x for x in facts if x not in facts_covered]:
            link.save_fact(fact=f, score=1, relationship=[], operation=operation)
