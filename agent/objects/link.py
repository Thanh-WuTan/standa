from objects.base_parser import PARSER_SIGNALS_FAILURE
from importlib import import_module
from objects.fact import *

class Link:
    def __init__(self, host = None, command = '', ability = None, executor = None, score = 0, relationships = [], used = None, paw = ''):
        self.host = host
        self.command = command
        self.ability = ability
        self.executor = executor
        self.score = score
        self.relationships = relationships
        self.used = used if used else []
        self.facts = []
        self.paw = paw

    @staticmethod
    def _load_module(module_type, module_info):
        module = import_module(module_info['module'])
        return getattr(module, module_type)(module_info)

    def _parse_link_result(self, result, parser, source_facts):
        blob = result
        parser_info = dict(module=parser['module'], used_facts=self.used, mappers=parser['parserconfigs'],
                           source_facts=source_facts)
        p_inst = self._load_module('Parser', parser_info)
        return p_inst.parse(blob=blob)

    def parse(self, result, source = None):
        source_facts = list(source.facts) if source else self.facts
        for parser in self.executor.parsers:
            try:
                relationships = self._parse_link_result(result, parser, source_facts)
                if len(relationships) > 0 and relationships[0] == PARSER_SIGNALS_FAILURE:
                    relationships = []  # Reset relationships if the parser signals failure
                else:
                    self.create_relationships(relationships, source)
                update_scores(increment=len(relationships), used=self.used, source = source)
            except Exception as e:
                print("Error in %s while parsing ability %s: %s" % (parser['module'], self.ability['ability_id'], e))

    def create_relationships(self, relationships, source):
        for relationship in relationships:
            self.save_fact(relationship.source, relationship.score, relationship.shorthand, source)
            self.save_fact(relationship.target, relationship.score, relationship.shorthand, source)
            if all((relationship.source.trait, relationship.edge)):
                self.relationships.append(relationship)

    def save_fact(self, fact, score, relationship, source):
        all_facts = source.facts if source else self.facts
        rl = [relationship] if relationship else []
        if all([fact.trait, fact.value]):
            existing_fact = None
            for f in all_facts:
                if f.trait == fact.trait and f.value == fact.value:
                    existing_fact = f
                    break
            if not existing_fact:
                f_gen = Fact(trait = fact.trait, value = fact.value, score = score, relationships = rl)
                self.facts.append(f_gen)
                all_facts.add(f_gen)
            else:
                if relationship not in existing_fact.relationships:
                    existing_fact.relationships.append(relationship)
                all_facts.remove(existing_fact) 
                all_facts.add(existing_fact)

                existing_local_record = [x for x in self.facts if x.trait == fact.trait and x.value == fact.value]
                if not existing_local_record:
                    self.facts.append(existing_fact)
        if source:
            source.facts = all_facts


def update_scores(increment, used, source):
    for uf in used:
        for found_fact in source.facts:
            if found_fact.unique == uf.unique:
                found_fact.score += increment
                break 

                
