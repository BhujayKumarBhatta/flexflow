import json
from flexflow.dbengines.sqlchemy import models as sqlm
from flexflow.exceptions import rules_exceptions  as exc

class Wfstatus:
    '''Name of workflow status each has an associaltion with a doc_category
    which means the status is meant for a particular document type'''
    
    def __init__(self, name):
        self.name = name
        
    def to_dict(self):
        return {"name": self.name}
        
    def to_json(self):
        return  json.dumps(self.to_dict())
    
    def __repr__(self):
        return '<{}(name={})>'.format(self.__class__.__name__, self.name)
    
    def __str__(self):
        return self.name
    
    @classmethod
    def from_dict(cls, adict):
        return cls(
            name = adict.get('name'),  )
        
        
