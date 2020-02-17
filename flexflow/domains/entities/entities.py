import json
from flexflow.exceptions import rules_exceptions  as rexc
from flexflow.domains import repos 
from flexflow.domains.entities import Entities
from sqlalchemy.orm.relationships import RelationshipProperty

class Wfstatus(Entities):
    '''workflow status master'''
    
    def __init__(self, name):
        self.name = name

class Doctype(Entities):
    
    def __init__(self, name, **kwargs):
        self.name = name
        for k, v in kwargs.items():
            if k not in self.__dict__.keys():
                setattr(self, k, v)
        #self.wfactions = self._get_related_wfactions_from_repo()
        
#     @property
#     def wfactions(self):
#         doctype_repo = repos.DomainRepo('Doctype')
#         doctype_obj_from_repo = doctype_repo.list_obj(name=self.name)
#         wfaction_repo = repos.DomainRepo('Wfaction')
#         searf = {"assocated_doctype": doctype_obj_from_repo}
#         result = wfaction_repo.list_domain_obj(**searf)
#         return result
        
class Wfaction(Entities):
    
    related_obj_map = {"assocated_doctype": {"mapped_object": Doctype, "primary_key": "name"},
                             }
    
    def __init__(self, name:str, assocated_doctype:Doctype,                 
                 need_prev_status:str, need_current_status:str,
                 leads_to_status:str, permitted_to_roles:list, **kwargs ):
        
        self.name = name        
        self.assocated_doctype = assocated_doctype        
        self.need_prev_status = need_prev_status
        self.need_current_status = need_current_status
        self.leads_to_status = leads_to_status
#         if not isinstance(assocated_doctype, Doctype): 
#             raise rexc.InvalidObjTypeInInputParam("permitted_to_roles", list )
        self.permitted_to_roles = permitted_to_roles
        #self.repo = repos.DomainRepo(self.__class__.__name__)#ensure storage level class name is same as emtities class name
        self._validate_param_values()
        for k, v in kwargs.items():
            if k not in self.__dict__.keys():
                setattr(self, k, v)
        
#     @property
#     def assocated_doctype_name(self):
#         return self.assocated_doctype.name
  
class Wfdoc(Entities):
    
    related_obj_map = {"assocated_doctype": {"mapped_object": Doctype, "primary_key": "name"},
                             }
    
    def __init__(self, assocated_doctype:Doctype, 
                 prev_status:str, current_status:str, 
                 doc_data:dict, **kwargs):
        self.assocated_doctype = assocated_doctype
        self.prev_status = prev_status
        self.current_status = current_status
        self.doc_data = doc_data
        for k, v in kwargs.items():
            if k not in self.__dict__.keys():
                setattr(self, k, v)
        
    @property
    def assocated_doctype_name(self):
        return self.assocated_doctype.name
    
    
        