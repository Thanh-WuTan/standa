import os
import yaml   
import json

from objects.source import *
from objects.fact import *
from objects.adversary import *
from objects.agent import *
from objects.operation import *
from objects.learner import *

ADV_ID = 'adversary_id'
PWD = os.path.dirname(__file__)
SOURCE_DIR = os.path.join(PWD, 'sources')
ABILTIY_DIR = os.path.join(PWD, 'abilities')
PAYLOAD_DIR = os.path.join(PWD, 'payloads')

def read_yaml(filepath):
    with open(filepath, 'r') as file:
        yaml_content = yaml.safe_load(file)
    return yaml_content
    

def Init_Source():
    source = Source()
    for filename in os.listdir(SOURCE_DIR): # one source file
        assert(filename.endswith('.yml'))
        filepath = os.path.join(SOURCE_DIR, filename)
        content = read_yaml(filepath)
        for fact in content['facts']:
            f = Fact(trait=fact['trait'], value=fact['value'])
            source.facts.add(f)
        source.relationships = content['relationships']
        source.rules = content['rules']
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

if __name__ == '__main__':
    adversary = Adversary(adversary_id = ADV_ID, abilities=Read_Abilities())
    uuid_mapper = json.load(open(os.path.join(PAYLOAD_DIR, 'uuid_mapper.json')))
    agent = Agent(platform='selected_platform', uuid_mapper=uuid_mapper) 
    source = Init_Source() 
    
    learner = Learner()
    learner.build_model(adversary.abilities)
    operation = Operation(adversary=adversary, agents=[agent], source=source, learner=learner)
    operation.run()