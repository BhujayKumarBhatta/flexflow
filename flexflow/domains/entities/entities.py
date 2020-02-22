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
    the Doctype category through their associated_doctype attribute.
    
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
        searh_filter = {"associated_doctype": {"name": self.name} }
        result = wfaction_repo.list_domain_obj(**searh_filter)
        return result
    
    @property
    def wfdocs(self):
        wfdoc_repo = repos.DomainRepo('Wfdoc')
        searh_filter = {"associated_doctype": {"name": self.name} }
        result = wfdoc_repo.list_domain_obj(**searh_filter)
        return result
    
    @property
    def datadocfields(self):
        datadocfields_repo = repos.DomainRepo("Datadocfield")
        searh_filter = {"associated_doctype": {"name": self.name} }
        result = datadocfields_repo.list_domain_obj(**searh_filter)
        return result
        

class Datadocfield(Entities):
    ''' field types to be entered as string e.g "str", "int" and not as python str, int objects.
    this will be mapped later in Wfdoc.docdata_field_type_map for checking the actual object type'''
    related_obj_map = {"associated_doctype": {"mapped_object": Doctype, 
                                             "primary_key": "name"},
                                             }
    def __init__(self, name, associated_doctype, ftype, flength, **kwargs):
        self.name = name
        self.associated_doctype = associated_doctype
        self.associated_doctype_name = self.associated_doctype.name   
        self.ftype = ftype
        self.flength = flength
        self._validate_relationship_param_values()
        super().__init__(**kwargs)


class Wfaction(Entities):
    '''every action will have relation to one doctype'''
    related_obj_map = {"associated_doctype": {"mapped_object": Doctype, 
                                             "primary_key": "name"},
                                             }
    
    def __init__(self, name:str, associated_doctype:Doctype,                 
                 need_prev_status:str, need_current_status:str,
                 leads_to_status:str, permitted_to_roles:list, **kwargs ):
        
        self.name = name        
        self.associated_doctype = associated_doctype
        self.associated_doctype_name = self.associated_doctype.name   
        self.need_prev_status = need_prev_status
        self.need_current_status = need_current_status
        self.leads_to_status = leads_to_status
#         if not isinstance(permitted_to_roles, list): 
#             raise rexc.InvalidObjTypeInInputParam("permitted_to_roles", list )
        self.permitted_to_roles = permitted_to_roles
        self._validate_relationship_param_values()
        super().__init__(**kwargs)
 
  
class Wfdoc(Entities):
    
    related_obj_map = {"associated_doctype": {"mapped_object": Doctype, 
                                             "primary_key": "name"},
                                             }
    docdata_field_type_map = {"str": str, "int": int}
    
    def __init__(self, name:str, associated_doctype:Doctype, 
                 prev_status:str, current_status:str, 
                 doc_data:dict, **kwargs):
        '''id should be one of the value from the doc_data e.g. invoice_number'''
        self.name = name
        #self.name = self.primvalue_of_docdata
        self.associated_doctype = associated_doctype
        self.associated_doctype_name = self.associated_doctype.name
        self.prev_status = prev_status
        self.current_status = current_status
        self.doc_data = doc_data
        self._validate_relationship_param_values()
        self._validate_docdata()
        super().__init__(**kwargs)
    
    @property
    def primvalue_of_docdata(self):
        return self.name
    
    @property
    def wfactions(self):
        wfaction_repo = repos.DomainRepo('Wfaction')
        searh_filter = {"associated_doctype": {"name": self.associated_doctype_name} }
        result = wfaction_repo.list_domain_obj(**searh_filter)
        return result
    
    @property
    def actions_for_current_status(self):
        actions_for_current_status = []
        for actionObj in self.wfactions:
            if self.current_status == actionObj.need_current_status:
                actions_for_current_status.append(actionObj.name)
        return actions_for_current_status
    
    def _validate_docdata(self):
        if  self.doc_data:
            conf_fieldobj_lst = self.associated_doctype.datadocfields
            conf_field_names = [item.name for item in conf_fieldobj_lst]
            for k, v in self.doc_data.items():
                if k not in conf_field_names:
                        raise rexc.UnknownFieldNameInDataDoc(k, conf_field_names)
                for fieldObj in conf_fieldobj_lst:
                    if k == fieldObj.name:                    
                        ctype = fieldObj.ftype
                        ctypeObj = self.docdata_field_type_map.get(ctype)
                        if not isinstance(v, ctypeObj):
                            raise rexc.DataTypeViolation(k, type(v), ctypeObj.__name__)
                        flength = fieldObj.flength
                        if not len(v) <= flength:
                            raise rexc.DataLengthViolation(k, len(v), flength)



 
###########AT TIMES THE SUPER CLASS TO_DICT IS NOT WOROKING
########POSSIBLY THE RELATED_OBJECT_MAP CLASS VARIABLE IS NOT GETTIGN
#REPLACED BY THE CHILD CLASS    
#     def to_dict(self):
#         return {"primvalue_of_docdata": self.primvalue_of_docdata,
#                 "name": self.name,
#                 "associated_doctype": self.associated_doctype.to_dict(),
#                 "associated_doctype_name": self.associated_doctype_name,
#                 "prev_status": self.prev_status,
#                 "current_status": self.current_status,
#                 "doc_data": self.doc_data}
    
        