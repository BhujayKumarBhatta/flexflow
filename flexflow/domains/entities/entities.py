import json
from flexflow.exceptions import rules_exceptions  as rexc
#from flexflow.domains import repos 
from flexflow.domains.entities import Entities



'''
Checks within Entities
-------------------------------------------
_validate_relationship_param_values
1. InvalidObjTypeInInputParam

from_dict method: 
1. InvalidObjTypeInInputParam  - For related objects 
2. PrimaryKeyNotPresentInSearch - Related object

_validate_docdata  in wfdoc

1.UnknownFieldNameInDataDoc
2.KeyIsMissingInData
3. DataLengthViolation
For data type instead of giving error, we convert it to desired format
'''

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
    def __init__(self, name, primkey_in_datadoc, roles_to_view_audit, **kwargs):
        self.name = name
        self.primkey_in_datadoc = primkey_in_datadoc
        self.roles_to_view_audit = roles_to_view_audit
        #self.domrepoclass = kwargs.get('domain_repo')  #should come from super
        super().__init__(**kwargs)
        
    @property
    def wfactions(self):
        wfaction_repo = self.domrepoclass('Wfaction')
        searh_filter = {"associated_doctype": {"name": self.name} }
        result = wfaction_repo.list_domain_obj(**searh_filter)
        return result
    
    @property
    def wfdocs(self):
        wfdoc_repo = self.domrepoclass('Wfdoc')
        searh_filter = {"associated_doctype": {"name": self.name} }
        result = wfdoc_repo.list_domain_obj(**searh_filter)
        return result
    
    @property
    def datadocfields(self):
        datadocfields_repo = self.domrepoclass("Datadocfield")
        #datadocfields_repo = self.domrepoclass("Datadocfield")
        searh_filter = {"associated_doctype": {"name": self.name} }
        result = datadocfields_repo.list_domain_obj(**searh_filter)
        return result
        

class Datadocfield(Entities):
    '''Doctype a.k.a document category defines what all fields will be present in the data
    portion of the document e.g name of the field , type and length of the data each field can store.
    Field types to be entered as string e.g "str", "int" 
    For developers:
    ==================
    and not as python str, int objects.
    this will be mapped later in Wfdoc.docdata_field_type_map for checking the actual object type'''
    related_obj_map = {"associated_doctype": {"mapped_object": Doctype, 
                                             "primary_key": "name"},
                                             }
    def __init__(self, name, associated_doctype, ftype:str, 
                 flength:int, status_needed_edit:list,
                  wfc_filter, wfc_filter_to_roles, 
                  retro:str='False', internaluse:str='False', **kwargs):
        self.name = name
        self.associated_doctype = associated_doctype
        self.associated_doctype_name = self.associated_doctype.name   
        self.ftype = ftype
        self.flength = flength
        self.status_needed_edit = status_needed_edit
        self.wfc_filter = wfc_filter
        self.wfc_filter_to_roles = wfc_filter_to_roles
        self.retro = retro
        self.internaluse = internaluse
        self._validate_relationship_param_values()
        super().__init__(**kwargs)


class Wfaction(Entities):
    '''every action will have relation to one doctype. Here we define the workflow action
    and status changing rules for a document type. 
    1. For an action to be performed,  the document must satisfy  previous_status and current_status 
    as defined here 
    2. Upon performing the action, the status of the doc will be changed as per "leads_to_status" definition
    '''
    related_obj_map = {"associated_doctype": {"mapped_object": Doctype, 
                                             "primary_key": "name"},
                                             }
    
    def __init__(self, name:str, associated_doctype:Doctype,                 
                 #need_prev_status:str, 
                 need_current_status:list,
                 leads_to_status:str, permitted_to_roles:list, hide_to_roles:list, 
                 undo_prev_hide_for:list, **kwargs ):
        
        self.name = name        
        self.associated_doctype = associated_doctype
        self.associated_doctype_name = self.associated_doctype.name   
        #self.need_prev_status = need_prev_status
        self.need_current_status = need_current_status
        self.leads_to_status = leads_to_status
#         if not isinstance(permitted_to_roles, list): 
#             raise rexc.InvalidObjTypeInInputParam("permitted_to_roles", list )
        self.permitted_to_roles = permitted_to_roles
        self.hide_to_roles = hide_to_roles
        self.undo_prev_hide_for = undo_prev_hide_for
        
        self._validate_relationship_param_values()
        super().__init__(**kwargs)

  
class Wfdoc(Entities):
    
    related_obj_map = {"associated_doctype": {"mapped_object": Doctype, 
                                             "primary_key": "name"},
                                             }
    docdata_field_type_map = {"str": str, "int": int}
    
    def __init__(self, name:str, associated_doctype:Doctype, 
                 prev_status:str, current_status:str,
                 doc_data:dict, has_draft_for_roles=[], **kwargs):
        '''id should be one of the value from the doc_data e.g. invoice_number'''
        self.name = name
        #self.name = self.primvalue_of_docdata
        self.associated_doctype = associated_doctype
        self.associated_doctype_name = self.associated_doctype.name
        self.prev_status = prev_status
        self.current_status = current_status        
        self.doc_data = doc_data
        self.has_draft_for_roles = has_draft_for_roles
        self._validate_relationship_param_values()
        self._validate_docdata()        
        super().__init__(**kwargs)
    
    @property
    def primvalue_of_docdata(self):
        return self.name
    
    @property
    def wfactions(self):
        wfaction_repo = self.domrepoclass('Wfaction')
        searh_filter = {"associated_doctype": {"name": self.associated_doctype_name} }
        result = wfaction_repo.list_domain_obj(**searh_filter)
        return result
    
    @property
    def actions_for_current_status(self):
        actions_for_current_status = []
        for actionObj in self.wfactions:
            need_current_status_list = \
                [ncs.lower().strip() for ncs in actionObj.need_current_status]
            if self.current_status.lower().strip() in need_current_status_list:
                actions_for_current_status.append(actionObj)
        return actions_for_current_status
    
    @property
    def editable_fields_at_current_status(self):
        return  self._validate_docdata()
    
    @property
    def wfdocaudits(self):
        wfdocaudit_repo = self.domrepoclass('Wfdocaudit')
        searh_filter = {"wfdoc": {"name": self.name} }
        result = wfdocaudit_repo.list_domain_obj(**searh_filter)
        return result
    
    @property
    def roles_to_view_audit(self):
        roles_to_view_audit = self.associated_doctype.roles_to_view_audit
        return roles_to_view_audit
    
    @property
    def draftdata(self):
        draft_data = None
        draft_repo = self.domrepoclass("Draftdata")
        search_f = {"name": self.name}
        draft_data_lst = draft_repo.list_dict(**search_f)
        if draft_data_lst and len(draft_data_lst) > 0:
            draft_data = draft_data_lst[0]
        return draft_data
        
    def _validate_docdata(self):
        editable_fields_at_this_status = []
        if  self.doc_data:
            conf_fieldobj_lst = self.associated_doctype.datadocfields
            conf_field_names = [item.name.lower().strip() for item in conf_fieldobj_lst]            
            for k, v in self.doc_data.items():
                if k.lower().strip() not in conf_field_names:
                        raise rexc.UnknownFieldNameInDataDoc(k, conf_field_names)
                for fieldObj in conf_fieldobj_lst:
                    ##TODO: fieldObj should be checked to see it has all the attributes, otherwise exception that field is not configured properly
                    print('retro status ..............................', fieldObj.retro)
                    if fieldObj.name.lower() not in self.doc_data.keys() and fieldObj.retro in [False, "", None]:
                        raise rexc.KeyIsMissingInData(fieldObj.name, fieldObj.name.lower())
                    if k.lower().strip() == fieldObj.name.lower().strip():                    
                        ctype = fieldObj.ftype.lower().strip()
                        ctypeObj = self.docdata_field_type_map.get(ctype)
                        #data type is getting converted by the workflow, hence no need to validate and raise exception
#                         if not isinstance(v, ctypeObj):
#                             raise rexc.DataTypeViolation(k, type(v), ctypeObj.__name__)
                        flength = fieldObj.flength
                        if not len(str(v)) <= flength:
                            raise rexc.DataLengthViolation(k, len(str(v)), flength)
                        if self.current_status and \
                        self.current_status.lower().strip() in [sne.lower().strip() for sne in fieldObj.status_needed_edit]:                            
                            editable_fields_at_this_status.append(fieldObj)
        return editable_fields_at_this_status
                            
                        


class Wfdocaudit(Entities):
    ''' a record here should be reated by the workflow whenever wfdoc is created or changed'''
    related_obj_map = {"wfdoc": {"mapped_object": Wfdoc, 
                                             "primary_key": "name"},
                                             }
    
    def __init__(self, name, wfdoc:Wfdoc, username, email, time_stamp, client_address, org, orgunit, department, roles, action, data, **kwargs):
        self.name = name
        self.wfdoc = wfdoc
        self.username = username
        self.email = email
        self.time_stamp = time_stamp
        self.client_address = client_address
        self.org = org
        self.orgunit = orgunit
        self.department = department
        self.roles = roles
        self.action = action
        self.data = data
        super().__init__(**kwargs)
        
 
class Holddoc(Entities):
    related_obj_map = {"wfdoc": {"mapped_object": Wfdoc, 
                                 "primary_key": "name"}, 
                       "associated_doctype": {"mapped_object": Doctype, 
                                             "primary_key": "name"},
                       }
    def __init__(self, name, target_role, reason, wfdoc, associated_doctype:Doctype, 
                 prev_status, current_status, doc_data):
        self.name = name
        self.target_role = target_role
        self.reason = reason
        self.wfdoc = wfdoc
        self.wfdoc_name = self.wfdoc.name
        self.associated_doctype = associated_doctype
        self.associated_doctype_name = self.associated_doctype.name        
        self.prev_status = prev_status
        self.current_status = current_status
        self.doc_data = doc_data
        
class Draftdata(Entities):
    related_obj_map = {"wfdoc": {"mapped_object": Wfdoc, 
                                 "primary_key": "name"}, 
                       "associated_doctype": {"mapped_object": Doctype, 
                                             "primary_key": "name"},
                       }
    
    def __init__(self, name, drafted_by, target_role, wfdoc,  doc_data, **kwargs):
        self.name = name
        self.drafted_by = drafted_by
        self.target_role = target_role        
        self.wfdoc = wfdoc
        self.wfdoc_name = self.wfdoc.name
        self.doc_data = doc_data
               
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
    
        