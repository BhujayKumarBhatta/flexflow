import json

class Entities:
    def __repr__(self):
        return '<{}(name={})>'.format(self.__class__.__name__, self.name)
    
    def __str__(self):
        return self.name
        
    def to_dict(self):
        return self.__class__.__dict__
        
    def to_json(self):
        return  json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, adict):
        return cls(**adict) 