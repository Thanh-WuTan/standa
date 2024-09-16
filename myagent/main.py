import os
import yaml  

from object.bps import *
from object.agent import *
from object.link import *
from object.source import *
from object.fact import *
from object.executor import *


ADV_ID = '4975696e-1d41-11eb-adc1-0242ac120002'
PWD = os.path.dirname(__file__)
ABILTIY_DIR = os.path.join(PWD, 'abilities')
SOURCE_DIR = os.path.join(PWD, 'sources')
PAYLOAD_DIR = os.path.join(PWD, 'payloads')

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

    source = Init_Source() 
    agent = Agent(platform="windows", username="Thanh", executors=["psh", "cmd"], privilege = 1) 
    bps = BasePlanningService()
    uuid_mapper = json.load(open(os.path.join(PAYLOAD_DIR, 'uuid_mapper.json')))
    cnt = 0
    for ability in Read_Abilities():
        cnt+= 1
        print("---------------")
        print(cnt)
        print("Ability: ", ability['name'])
        if not agent.is_capable_to_run(ability):
            continue
        
        # sorted executors by preference
        executors = agent.find_executors(ability)
        
        links = []

        for ex in executors:
            executor = Executor(name = ex['name'], platform = ex['platform'], command = ex['command'],
                           parsers = ex['parsers'], timeout = ex['timeout'], payloads = ex['payloads'])
            ex_link = Link(command=ex['command'], ability=ability, executor=executor)
            
            valid_links = bps.add_test_variants(links=[ex_link], agent=agent, facts=source.facts, trim_unset_variables=True, uuid_mapper=uuid_mapper)
            
            if valid_links:
                links = bps.sort_links(valid_links)
                print(links[0].command)
                break

        for link in links:
            ex = link.executor
            # ex.command = ex.replace_payload_dir(link.command, PAYLOAD_DIR)
            # stdout, stderr = ex.run_command()
            # print(link.command)
       

if __name__ == '__main__':
    
    main()