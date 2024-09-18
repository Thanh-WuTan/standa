from objects.base_parser import PARSER_SIGNALS_FAILURE
from importlib import import_module

class Link:
    def __init__(self, host = None, command = '', ability = None, executor = None, score = 0, relationships = [], used = None):
        self.host = host
        self.command = command
        self.ability = ability
        self.executor = executor
        self.score = score
        self.relationships = relationships
        self.used = used if used else []
        self.facts = []

    def _load_module(module_type, module_info):
        module = import_module(module_info['module'])
        return getattr(module, module_type)(module_info)

    def _parse_link_result(self, result, parser, source_facts):
        blob = result
        parser_info = dict(module=parser.module, used_facts=self.used, mappers=parser.parserconfigs,
                           source_facts=source_facts)
        p_inst = self._load_module('Parser', parser_info)
        return p_inst.parse(blob=blob)

    def parse(self, result, source_facts = []):
        for parser in self.executor.parsers:
            try:
                relationships = self._parse_link_result(result, parser, source_facts)
            #     if len(relationships) > 0 and relationships[0] == PARSER_SIGNALS_FAILURE:
            #         relationships = []  # Reset relationships if the parser signals failure
            #     else:
            #         pass
            #         self.create_relationships(relationships, operation)
            #     update_scores(operation, increment=len(relationships), used=self.used, facts=self.facts)
            except Exception as e:
                print("Error in %s while parsing ability %s: %s" % (parser.module, self.ability.ability_id, e))