escape_ref = {
    'sh': {
        'special': ['\\', ' ', '$', '#', '^', '&', '*', '|', '`', '>',
                    '<', '"', '\'', '[', ']', '{', '}', '?', '~', '%'],
        'escape_prefix': '\\'
    },
    'psh': {
        'special': ['`', '^', '(', ')', '[', ']', '|', '+', '%',
                    '?', '$', '#', '&', '@', '>', '<', '\'', '"', ' '],
        'escape_prefix': '`'
    },
    'cmd': {
        'special': ['^', '&', '<', '>', '|', ' ', '?', '\'', '"'],
        'escape_prefix': '^'
    }
}

class Fact:
    def __init__(self, trait, value = None, score = 1, relationships = [], collected_by = [], technique = None):
        self.trait = trait
        self.value = value
        self.score = score
        self.relationships = relationships  
        self.collected_by = collected_by
        self.technique = technique

    @staticmethod
    def hash(s):
        return s 
     
    @property
    def unique(self):
        return self.hash('%s%s' % (self.trait, self.value))


    def escaped(self, executor):
        if executor not in escape_ref:
            return self.value
        escaped_value = str(self.value)
        for char in escape_ref[executor]['special']:
            escaped_value = escaped_value.replace(char, (escape_ref[executor]['escape_prefix'] + char))
        return escaped_value
    
