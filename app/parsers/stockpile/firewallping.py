from objects.fact import *
from objects.relationship import *
from objects.base_parser import *


class Parser(BaseParser):

    def parse(self, blob):
        relationships = []
        for match in self.line(blob):
            if match.startswith('    Packets'):
                if '(0%' in match:
                    for mp in self.mappers:
                        source = self.set_value(mp.source, match, self.used_facts)
                        relationships.append(
                            Relationship(source=Fact(mp.source, source),
                                         edge=mp.edge,
                                         target=Fact(mp.target, None))
                        )
        return relationships
