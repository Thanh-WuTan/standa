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