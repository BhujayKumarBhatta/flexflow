import json
from flexflow.exceptions import rules_exceptions  as rexc
from flexflow.domains import repos
from flexflow.domains.


class Wfstatus(Entities):
    '''workflow status master'''
    
    def __init__(self, name):
        self.name = name

class Doctype(Entities):
    
    def __init__(self, name):
        self.name = name 
        
class Wfaction(Entities):
    
    def __init__(self, name:str, assocated_doctype: Doctype,
                 need_prev_status:str, need_current_status:str,
                 leads_to_status:str, permitted_to_roles:list ):
        self.name = name
        self.assocated_doctype = assocated_doctype
        self.need_prev_status = need_prev_status
        self.need_current_status = need_current_status
        self.leads_to_status = leads_to_status
        self.permitted_to_roles = permitted_to_roles
        #self.repo = repos.DomainRepo(self.__class__.__name__)#ensure storage level class name is same as emtities class name
        
    @property
    def assocated_doctype_name(self):
        return self.assocated_doctype.name
     
    def to_dict(self):
        return {"name": self.name, 
                "assocated_doctype": self.assocated_doctype.name,
                "need_prev_status": self.need_prev_status,
                "need_current_status": self.need_current_status,
                "leads_to_status": self.leads_to_status,
                "permitted_to_roles": self.permitted_to_roles
                }
        
class Wfdoc(Entities):
    
    def __init__(self, assocated_doctype:Doctype, prev_status:str, current_status:str, doc_data:dict):
        self.assocated_doctype = assocated_doctype
        self.prev_status = prev_status
        self.current_status = current_status
        self.doc_data = doc_data
        
    @property
    def assocated_doctype_name(self):
        return self.assocated_doctype.name
    
    def to_dict(self):
        return {"assocated_doctype": self.assocated_doctype,
                "prev_status": self.prev_status,
                "current_status": self.current_status,
                "doc_data": self.doc_data}
        