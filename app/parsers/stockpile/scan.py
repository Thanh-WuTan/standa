from objects.fact import *
from objects.relationship import *
from objects.base_parser import *


class Parser(BaseParser):

    def parse(self, blob):
        relationships = []
        for match in self.line(blob):
            values = match.split(':')
            for mp in self.mappers:
                relationships.append(
                    Relationship(source=Fact(mp.source, values[0]),
                                 edge=mp.edge,
                                 target=Fact(mp.target, values[1]))
                )
        return relationships
