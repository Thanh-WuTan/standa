import time

from main import PAYLOAD_DIR
from objects.base_planning import BasePlanningService
from objects.executor import Executor
from objects.link import Link
from objects.attire_logging import Attire


class Operation:
    def __init__(self, adversary=None, agents=None, source=None, learner=None, rules=[]):
        self.adversary = adversary
        self.agents = agents if agents else []
        self.source = source
        self.learner = learner  
        self.rules = rules
        if source:
            self.rules = source.rules
    
    def active_agents(self):
        return self.agents

    def all_facts(self):
        return self.source.facts

    def all_relationships(self):
        return self.source.relationships

    def run(self):
        attire = Attire(agent=self.agents[0])
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
            steps = []
            for step_order, link in enumerate(links, start=1):
                ex = link.executor
                ex.command = ex.replace_payload_dir(link.command, PAYLOAD_DIR)
                if ex.command in ran_command:
                    continue
                ran_command.add(ex.command)
                result = ex.run_command()
                steps.append(learner._save(link=link, result=result, operation=self, executor=ex, step_order=step_order))
            attire.add_procedure(steps, ability, order)
        attire.create_attire_file()