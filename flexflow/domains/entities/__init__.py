import json
from flexflow.exceptions import rules_exceptions  as rexc
#from flexflow.domains import repos 
from flexflow.domains import repos #import DomainRepo

class Entities:
    related_obj_map = {}
    
    def __init__(self, **kwargs):       
        for k, v in kwargs.items():
            if k not in self.__dict__.keys():
                setattr(self, k, v)
    
    def __repr__(self):
        if hasattr(self, "name"):
            identifier = str(self.name)
            repr = '<{}(name={})>'.format(self.__class__.__name__, identifier)
        else:
            identifier = self.id
            repr = '<{}(id={})>'.format(self.__class__.__name__, identifier)
        return repr
    
    def __str__(self):
        if hasattr(self, "name"):
            identifier = self.name
        else:
            identifier = self.id
        return str(identifier)
        
    def to_dict(self):
        new_dict = self.__dict__.copy()
        for k, v in  self.__dict__.items():
            if k in self.related_obj_map.keys():
                new_dict.update({k: v.to_dict()})
        return new_dict
        
    def to_json(self):
        return  json.dumps(self.to_dict())
    
    def _validate_relationship_param_values(self):
        for  k,v in self.__dict__.items():
            if k in self.related_obj_map.keys() and \
             not isinstance(v, self.related_obj_map.get(k).get('mapped_object')):
                raise rexc.InvalidObjTypeInInputParam(k, self.related_obj_map.get(k).get('mapped_object'))
    
    @classmethod
    def from_dict(cls, data_dict):
        for k,v in data_dict.items():            
            if k in cls.related_obj_map.keys():
                related_class = cls.related_obj_map.get(k).get('mapped_object')              
                if not (isinstance(v, dict ) or  isinstance(v, related_class)):
                    raise rexc.InvalidObjTypeInInputParam(k, dict)
                if isinstance(v, dict ):
                    primary_key = cls.related_obj_map.get(k).get('primary_key') 
                    if not primary_key in v:
                        raise rexc.PrimaryKeyNotPresentInSearch(primary_key, v)                
                    relobjname = cls.related_obj_map.get(k).get('mapped_object').__name__
                    relobjrepo = repos.DomainRepo(relobjname)
                    result_list = relobjrepo.list_domain_obj(**v)
                    data_dict.update({k: result_list[0]})
                elif isinstance(v, related_class):
                    data_dict.update({k: v})
        return cls(**data_dict) 