import re
import glob
import itertools

from importlib import import_module
from objects.link import update_scores
from objects.relationship import *

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

    def learn(self, source, link, blob):
        facts = source.facts
        found_facts = []
        print("learn is called")
        for parser in self.parsers:
            try:
                for fact in parser.parse(blob):
                    found_facts.append(fact)
            except Exception as e:
                print("Error: ", e)
        update_scores(increment=len(found_facts), used=facts, source=source)
        self._store_results(link, found_facts, source)

    def _store_results(self, link, facts, source):
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
            link.save_fact(fact=f, score=1, relationship=[], source=source)
