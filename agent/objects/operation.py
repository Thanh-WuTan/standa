import time

from main import PAYLOAD_DIR
from objects.base_planning import *
from objects.executor import *
from objects.link import * 


class Operation:
    def __init__(self, adversary=None, agents=None, source=None, learner=None, rules=[]):
        self.adversary = adversary
        self.agents = agents if agents else []
        self.source = source
        self.learner = learner  
        self.rules = rules
        if source:
            self.rules = source.rules
    
    def all_facts(self):
        return self.source.facts

    def all_relationships(self):
        return self.source.relationships

    def run(self):
        procedures = []
        bps = BasePlanningService()
        agent = self.agents[0]
        source = self.source
        learner = self.learner 
        for order, ability in enumerate(self.adversary.abilities, start=1):
            if not agent.is_capable_to_run(ability):
                continue
            executors = agent.find_executors(ability)
            links = []  
            for ex in executors:
                executor = Executor(name = ex['name'], platform = ex['platform'], command = ex['command'],
                                    parsers = ex['parsers'], timeout = ex['timeout'], payloads = ex['payloads'])
                ex_link = Link(command=ex['command'], ability=ability, executor=executor, paw=agent.paw)
                valid_links = bps.add_test_variants(links=[ex_link], agent=agent, facts=source.facts, rules=self.rules,
                                                    trim_unset_variables=True, trim_missing_requirements=True,
                                                    operation=self)
                if valid_links:
                    links = bps.sort_links(valid_links)
                    break
            ran_command = set()
            procedure = []
            for step_order, link in enumerate(links, start=1):
                ex = link.executor
                ex.command = ex.replace_payload_dir(link.command, PAYLOAD_DIR)
                if ex.command in ran_command:
                    continue
                ran_command.add(ex.command)
                result = ex.run_command()
                learner._save(link, result, self)
            
            procedures.append(procedure)