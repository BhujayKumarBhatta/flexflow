import json
from flexflow.exceptions import rules_exceptions  as rexc
#from flexflow.domains import repos 
#from flexflow.domains import repos #import DomainRepo

class Entities:
    related_obj_map = {}
    domrepoclass = None
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
    def from_dict(cls, data_dict, domrepoclass=None):
        ''' The trick  here how do we create the object from dict when one of the key has nested dict representing another object. 
        1. One rule can be don't accept nested dict for those  atrributes which expect object.
        2. Another possibility, we have to go to repo and retrieve the object from the repo by its primary key
        3. 3rd can be broken as two :
            a. within the dict the related objects are presented directly 
            b. within the dict realted onjects are presented as nested dict
        example as given below 
        #wfaction2_dict=  {"name": "wfaction2",
        #                 "associated_doctype": doctype2,    #related object provided directly in dict                     
        #                 "need_current_status": "s2",
        #                 "leads_to_status": "s3",
        #                 "permitted_to_roles": ["r2",],
        #                 "hide_to_roles": ["r5",],
        #                 "undo_prev_hide_for": [],
        #                 }
        #wfaction3_dict=  {"name": "wfaction3",
        #                 "associated_doctype": {"name": "doctype2"},       # related object represented as nested dict                  
        #                 "need_current_status": "s3",
        #                 "leads_to_status": "s4",
        #                 "permitted_to_roles": ["r3",],
        #                 "hide_to_roles": ["r5",],
        #                 "undo_prev_hide_for": [],
        #                 }
        #wfaction1 = ent.Wfaction(name="wfaction1",
        #                        associated_doctype=doctype1,        # object initialized with parameters               
        #                        need_current_status="s1",
        #                        leads_to_status="s2",
        #                        permitted_to_roles=["r1",],
        #                        hide_to_roles=["r5",],
        #                        undo_prev_hide_for=[])
       # 
        When using method 2 we are facing a circular dependency  since entity is importing DomainRepo and DominRepo is using entities
        Lets try with making DomainRepo as a class attribute which can be assigned  to the entities while initializing  the entity by 
        other classes which  imports DominRepo and is lower level than  the entity , for example  our Workflow class
        
        We also tried DominRepo as a parameter to from_dict method of the entity 
        
        Finally  ent.Entities.domrepoclass = DomainRepo  before initializing any entities  will handle all scnerios
        In this entities module will not import the DomainRepo class but entities will have a class attribute domrepoclass which 
        will be  assigned by workflow or test or any other lower level classes   '''
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
                    if  domrepoclass: DomaimRepo = domrepoclass
                    else: DomaimRepo = cls.domrepoclass
                    relobjrepo = DomaimRepo(relobjname)
                    result_list = relobjrepo.list_domain_obj(**v)
                    data_dict.update({k: result_list[0]})
                elif isinstance(v, related_class):
                    data_dict.update({k: v})
        return cls(**data_dict) 