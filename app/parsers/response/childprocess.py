import re

from objects.fact import *
from objects.relationship import *
from objects.base_parser import *


class Parser(BaseParser):

    def parse(self, blob):
        relationships = []
        all_facts = self.used_facts
        for mp in self.mappers:
            matches = self.parse_childid(blob)
            for match in matches:
                src_fact_value = [f.value for f in all_facts if f.trait == mp['source']].pop()
                r = Relationship(source=Fact(mp['source'], src_fact_value),
                                 edge=mp['edge'],
                                 target=Fact(mp['target'], match.strip()))
                relationships.append(r)
                all_facts.append(r.target)
        return relationships

    @staticmethod
    def parse_childid(blob):
        return re.findall(r'\bProcessId: (.*)', blob, re.IGNORECASE)
