import os
import yaml  

from objects.base_parser import *
from objects.base_planning import *
from objects.agent import *
from objects.link import *
from objects.source import *
from objects.fact import *
from objects.executor import *
from objects.learner import * 

# 4975696e-1d41-11eb-adc1-0242ac120002
# 1a98b8e6-18ce-4617-8cc5-e65a1a9d490e
ADV_ID = '1a98b8e6-18ce-4617-8cc5-e65a1a9d490e'
PWD = os.path.dirname(__file__)
DIR = os.path.join(PWD, ADV_ID)
SOURCE_DIR = os.path.join(DIR, 'sources')
ABILTIY_DIR = os.path.join(DIR, 'abilities')
PAYLOAD_DIR = os.path.join(DIR, 'payloads')

def read_yaml(filepath):
    with open(filepath, 'r') as file:
        yaml_content = yaml.safe_load(file)
    return yaml_content
    

def Init_Source():
    source = Source()
    for filename in os.listdir(SOURCE_DIR):
        assert(filename.endswith('.yml'))
        filepath = os.path.join(SOURCE_DIR, filename)
        content = read_yaml(filepath)
        for fact in content['facts']:
            f = Fact(trait=fact['trait'], value=fact['value'])
            source.facts.add(f)
    return source

def Read_Abilities():
    abilities = []
    assert(os.path.exists(ABILTIY_DIR))
    for id in range(len(os.listdir(ABILTIY_DIR))):
        filename = str(id + 1) + '.yml'
        filepath = os.path.join(ABILTIY_DIR, filename)  
        ability = read_yaml(filepath)
        abilities.append(ability)
    return abilities



def main():
    agent = Agent(platform="linux", username="wutan", executors=["sh"], privilege = 1) 
    uuid_mapper = json.load(open(os.path.join(PAYLOAD_DIR, 'uuid_mapper.json')))
    bps = BasePlanningService()
    source = Init_Source() 
    abilities = Read_Abilities()
    learner = Learner()
    learner.build_model(abilities)
 
    cnt = 0
    for ability in abilities:
        if not agent.is_capable_to_run(ability):
            continue        
        cnt+= 1
        executors = agent.find_executors(ability)
        links = []
        for ex in executors:
            executor = Executor(name = ex['name'], platform = ex['platform'], command = ex['command'],
                           parsers = ex['parsers'], timeout = ex['timeout'], payloads = ex['payloads'])
            
            ex_link = Link(command=ex['command'], ability=ability, executor=executor)
            
            valid_links = bps.add_test_variants(links=[ex_link], agent=agent, facts=source.facts, trim_unset_variables=True, uuid_mapper=uuid_mapper)
            
            if valid_links:
                links = bps.sort_links(valid_links)
                break

        ran_command = set()
        for link in links:
            ex = link.executor
            ex.command = ex.replace_payload_dir(link.command, PAYLOAD_DIR)
            if ex.command in ran_command:
                continue
            ran_command.add(ex.command)
            
            stdout, stderr = ex.run_command()
            if link.executor.parsers:
                link.parse(result = stdout, source = source)
            else:
                learner.learn(source, link, stdout)
            # print("----------------")
            # print("cnt = ", cnt)
            # print("Ability: ", ability['name'])
            # print("Executed command: ", ex.command)
            # print("stdout: ", stdout)
if __name__ == '__main__':

    main()