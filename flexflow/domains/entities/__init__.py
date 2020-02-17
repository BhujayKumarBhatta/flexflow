import json
from flexflow.exceptions import rules_exceptions  as rexc
from flexflow.domains import repos 

class Entities:
    related_obj_map = {}
    
    def __repr__(self):
        return '<{}(name={})>'.format(self.__class__.__name__, self.name)
    
    def __str__(self):
        return self.name
        
    def to_dict(self):
        new_dict = self.__dict__.copy()
        for k, v in  self.__dict__.items():
            if k in self.related_obj_map.keys():
                new_dict.update({k: v.to_dict()})
        return new_dict
        
    def to_json(self):
        return  json.dumps(self.to_dict())
    
    def _validate_param_values(self):
        for  k,v in self.__dict__.items():
            if k in self.related_obj_map.keys() and \
             not isinstance(v, self.related_obj_map.get(k).get('mapped_object')):
                raise rexc.InvalidObjTypeInInputParam(k, self.related_obj_map.get(k).get('mapped_object'))
    
    @classmethod
    def from_dict(cls, data_dict):
        for k,v in data_dict.items():            
            if k in cls.related_obj_map.keys():                
                if not isinstance(v, dict ) :
                    raise rexc.InvalidObjTypeInInputParam(k, dict)
                primary_key = cls.related_obj_map.get(k).get('primary_key') 
                if not primary_key in v:
                    raise rexc.PrimaryKeyNotPresentInSearch(primary_key, v)                
                relobjname = cls.related_obj_map.get(k).get('mapped_object').__name__
                relobjrepo = repos.DomainRepo(relobjname)
                result_list = relobjrepo.list_domain_obj(**v)
                data_dict.update({k: result_list[0]})        
        return cls(**data_dict) 