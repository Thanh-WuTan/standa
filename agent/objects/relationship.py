class Relationship:
    def __init__(self, source, edge = None, target = None, score = 1):
            self.source = source
            self.edge = edge
            self.target = target
            self.score = score
    @property
    def shorthand(self):
        # compute a visual representation of a relationship for recording purposes
        stub = f"{self.source.trait}({self.source.value})"
        if self.edge:
            stub += f" : {self.edge}"
            if self.target and self.target.trait:
                stub += f" : {self.target.trait}({self.target.value})"
        return stub