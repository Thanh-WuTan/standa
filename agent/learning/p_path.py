import re

from objects.fact import Fact


class Parser:

    def __init__(self):
        self.trait = 'host.file.path'

    def parse(self, blob):
        for p in re.findall(r'(\/.*?\.[\w:]+[^\s]+)', blob):
            yield Fact(trait=self.trait, value=p)
        for p in re.findall(r'(C:\\.*?\.[\w:]+)', blob):
            yield Fact(trait=self.trait, value=p)
