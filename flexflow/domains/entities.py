import json
from flexflow.exceptions import rules_exceptions  as exc

class Wfstatus:
    '''workflow status master'''
    
    def __init__(self, name):
        self.name = name
        
    def __repr__(self):
        return '<{}(name={})>'.format(self.__class__.__name__, self.name)
    
    def __str__(self):
        return self.name
        
    def to_dict(self):
        return {"name": self.name}
        
    def to_json(self):
        return  json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, adict):
        return cls(name=adict.get('name'),)
        
        
