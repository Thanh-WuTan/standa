from objects.fact import *
from objects.relationship import *
from objects.base_parser import *


class Parser(BaseParser):

    def parse(self, blob):
        relationships = []
        for match in self.line(blob.strip()):
            for mp in self.mappers:
                source = self.set_value(mp['source'], match.strip(), self.used_facts)
                target = self.set_value(mp['target'], match.strip(), self.used_facts)
                relationships.append(
                    Relationship(source=Fact(mp['source'], source),
                                 edge=mp['edge'],
                                 target=Fact(mp['target'], target))
                )
        return relationships
