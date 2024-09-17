import re

from objects.fact import *
from objects.relationship import *
from objects.base_parser import *


class Parser(BaseParser):
    def parse(self, blob):
        relationships = []
        name = self._get_volume_name(blob)
        if name:
            for mp in self.mappers:
                source = self.set_value(mp.source, name, self.used_facts)
                target = self.set_value(mp.target, name, self.used_facts)
                relationships.append(
                    Relationship(source=Fact(mp.source, source),
                                 edge=mp.edge,
                                 target=Fact(mp.target, target))
                )
        return relationships

    @staticmethod
    def _get_volume_name(blob):
        results = re.findall(r'^\s*Shadow Copy Volume Name: (\S+)', blob, re.MULTILINE)
        if results:
            return results[0]
