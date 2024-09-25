import json

from objects.result import get_current_timestamp

class Attire:
    def __init__(self, agent):
        self.content = {
            "attire-version": "1.1",
            "execution-data": {
                "execution-command": "python calderalone.py",
                "execution-id": agent.paw,
                "execution-source": "Calder-alone",
                "execution-category": {
                    "name": "Calder-alone",
                    "abbreviation": "CDA"
                },
                "target": {
                    "host": "vcs",
                    "ip": "0.0.0.0",
                    "path": "PATH=C:",
                    "user": "vcs-purple-team"
                },
                "time-generated": get_current_timestamp().replace("Z", ".000Z")
            },
            "procedures": []
        }
    
    def add_procedure(self, steps, ability, order):
        procedure = {
            "procedure-name": ability['name'],
            "procedure-description": ability['description'],
            "procedure-id": {
                "type": "guid",
                "id": ability["ability_id"]
            },
            "mitre-technique-id": ability["technique_id"],
            "order": order,
            "steps": steps
        }
        self.content["procedures"].append(procedure)

    def create_attire_file(self):
        with open('attire.json', 'w') as f:
            json.dump(self.content, f, indent=4)
        return True