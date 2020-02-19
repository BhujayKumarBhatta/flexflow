import json
from flexflow.exceptions import rules_exceptions  as rexc
from flexflow.domains import repos 
from flexflow.domains.entities import Entities
from sqlalchemy.orm.relationships import RelationshipProperty

class Wfstatus(Entities):
    '''workflow status master'''
    
    def __init__(self, name, **kwargs):
        self.name = name
        super().__init__(**kwargs)


class Doctype(Entities):
    '''Doctype defines what type of data and what are the workflow
     action rules which are  applicable to  a category of documents.
         
    Workflow documents(a.k.a. Wfdoc) will have to belong to one of 
    the Doctype category through their assocated_doctype attribute.
    
    Wfdoc can store only those type of data in its doc_data attribute 
    which are defined in the Doctype.
    
    One such condition is:  the data should have a key whose name 
    is same as primkey_in_datadoc defined in Doctyoe
    '''
    def __init__(self, name, primkey_in_datadoc, **kwargs):
        self.name = name
        self.primkey_in_datadoc = primkey_in_datadoc
        super().__init__(**kwargs)
        
    @property
    def wfactions(self):
        wfaction_repo = repos.DomainRepo('Wfaction')
        searh_filter = {"assocated_doctype": {"name": self.name} }
        result = wfaction_repo.list_domain_obj(**searh_filter)
        return result
    
    @property
    def wfdocs(self):
        wfdoc_repo = repos.DomainRepo('Wfdoc')
        searh_filter = {"assocated_doctype": {"name": self.name} }
        result = wfdoc_repo.list_domain_obj(**searh_filter)
        return result
        

class Wfaction(Entities):
    '''every action will have relation to one doctype'''
    related_obj_map = {"assocated_doctype": {"mapped_object": Doctype, 
                                             "primary_key": "name"},
                                             }
    
    def __init__(self, name:str, assocated_doctype:Doctype,                 
                 need_prev_status:str, need_current_status:str,
                 leads_to_status:str, permitted_to_roles:list, **kwargs ):
        
        self.name = name        
        self.assocated_doctype = assocated_doctype
        self.assocated_doctype_name = self.assocated_doctype.name   
        self.need_prev_status = need_prev_status
        self.need_current_status = need_current_status
        self.leads_to_status = leads_to_status
#         if not isinstance(permitted_to_roles, list): 
#             raise rexc.InvalidObjTypeInInputParam("permitted_to_roles", list )
        self.permitted_to_roles = permitted_to_roles
        self._validate_relationship_param_values()
        super().__init__(**kwargs)
        
  
  
class Wfdoc(Entities):
    
    related_obj_map = {"assocated_doctype": {"mapped_object": Doctype, 
                                             "primary_key": "name"},
                                             }
    
    def __init__(self, id:str, assocated_doctype:Doctype, 
                 prev_status:str, current_status:str, 
                 doc_data:dict, **kwargs):
        '''id should be one of the value from the doc_data e.g. invoice_number'''
        self.id = id
        #self.name = self.primvalue_of_docdata
        self.assocated_doctype = assocated_doctype
        self.assocated_doctype_name = self.assocated_doctype.name
        self.prev_status = prev_status
        self.current_status = current_status
        self.doc_data = doc_data
        self._validate_relationship_param_values()
        super().__init__(**kwargs)
    
    @property
    def primvalue_of_docdata(self):
        return self.id
    
    @property
    def wfactions(self):
        wfaction_repo = repos.DomainRepo('Wfaction')
        searh_filter = {"assocated_doctype": {"name": self.assocated_doctype_name} }
        result = wfaction_repo.list_domain_obj(**searh_filter)
        return result
###########AT TIMES THE SUPER CLASS TO_DICT IS NOT WOROKING
########POSSIBLY THE RELATED_OBJECT_MAP CLASS VARIABLE IS NOT GETTIGN
#REPLACED BY THE CHILD CLASS    
#     def to_dict(self):
#         return {"primvalue_of_docdata": self.primvalue_of_docdata,
#                 "name": self.name,
#                 "assocated_doctype": self.assocated_doctype.to_dict(),
#                 "assocated_doctype_name": self.assocated_doctype_name,
#                 "prev_status": self.prev_status,
#                 "current_status": self.current_status,
#                 "doc_data": self.doc_data}
    
        