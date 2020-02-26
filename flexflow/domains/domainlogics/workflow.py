from flexflow.domains.entities import entities as ent
from flexflow.domains.repos import DomainRepo
from flexflow.exceptions import rules_exceptions  as rexc

class Workflow:
    
    def __init__(self, doctype_name:str, role=None):
        self.doctype_name = doctype_name
        self.role = role
    
    def create_doc(self, data:dict, roles):
        ''' a key from the data is treated as the primary key for the 
        document. The key name is defined in the doctype.
        for creation of the doc the condition is no such doc by the id(primary key)
        exists in the repo.
        
        Also see wfdocObj initialization. Earlier we used to call the storage classes from sqlalchemy or mongoengine for creating the object, now we are using domain entities 
        '''
        doctyoeObj = self._get_doctype_obj_from_name()
        docid = self._get_primary_key_from_data_doc(doctyoeObj, data)
        self._check_role_for_create_action(doctyoeObj, roles) ## remeber fields validation in done during documents init method
        wfdocObj = ent.Wfdoc(name=docid,
                         associated_doctype=doctyoeObj,
                         prev_status="",
                         current_status="Created",
                         doc_data=data) ###earlier we used to call the storage classes from sqlalchemy or mongoengine for creating the object, now we are using domain entities 
        wfdoc_repo = DomainRepo("Wfdoc")
        msg = wfdoc_repo.add_list_of_domain_obj([wfdocObj])
        return msg
    
    def action_change_status(self, wfdoc_name, intended_action, data=None):
        wfdocObj = self._get_wfdoc_by_name(wfdoc_name)
        wfactions_list = wfdocObj.wfactions
        wfactionObj = None
        for item in wfactions_list:
            if item.name == intended_action:
                wfactionObj = item
                break
        self._check_action_rules(wfdocObj, wfactionObj, intended_action)
        self._validate_editable_fields(wfdocObj, data)
        #wfdocObj.current_status = wfactionObj.leads_to_status #TODO: it should be done this way
        wfdoc_repo = DomainRepo("Wfdoc")
        updated_data_dict = {"current_status": wfactionObj.leads_to_status,
                             "prev_status": wfdocObj.current_status}
        target_doc_name = {"name": wfdocObj.name}
        msg = wfdoc_repo.update_from_dict(updated_data_dict, **target_doc_name)
        return msg
    
    def _get_primary_key_from_data_doc(self, doctyoeObj, data_doc):
        docid = None
        primkey_in_datadoc = doctyoeObj.primkey_in_datadoc
        if not data_doc.get(primkey_in_datadoc):
            raise rexc.PrimaryKeyNotPresentInDataDict(primkey_in_datadoc)
        docid = data_doc.get(primkey_in_datadoc)
        if self._get_wfdoc_by_name(docid):
            raise rexc.DuplicateDocumentExists(docid)
        return docid
    
    def _check_role_for_create_action(self, doctyoeObj, roles):
        for actionObj in doctyoeObj.wfactions:           
            if actionObj.name == "Create":
                for  role in roles:
                    if role in actionObj.permitted_to_roles:
                        role_not_found = False
                        break
                    else: 
                        role_not_found = True                       
                action_not_found = False
                break
            else:
                action_not_found = True                
        if action_not_found is True: raise rexc.NoActionRuleForCreate
        if role_not_found is True:
            raise rexc.RoleNotPermittedForThisAction(role, 
                                                      actionObj.permitted_to_roles)
        
   
    def _get_doctype_obj_from_name(self):
        '''search by primary key name, hence expected to get one object'''
        result = None
        search_dict = {"name": self.doctype_name}
        doctype_repo = DomainRepo("Doctype")
        lst = doctype_repo.list_domain_obj(**search_dict)
        if  len(lst) == 1 : result = lst[0]              
        return result
    
#     def _validate_fields_during_create(self, doctypeObj, data:dict):
#         if data:
#             for k in data.keys():
#                 efac = doctypeObj.datadocfields
#                 if not k in efac:
#                     raise rexc.EditNotAllowedForThisField(k, 
#                                                           doctypeObj.current_status,
#                                                           efac)
    
    def _get_wfdoc_by_name(self, wfdoc_name):
        '''search by primary key id, hence expected to get one object'''
        result = None
        search_dict = {"name": wfdoc_name}
        wfdoc_repo = DomainRepo("Wfdoc")
        lst = wfdoc_repo.list_domain_obj(**search_dict)
        if  len(lst) == 1 : result = lst[0]              
        return result
    
    def _check_action_rules(self, wfdocObj,  wfactionObj, intended_action):
        if not wfactionObj:
            raise rexc.NoWorkFlowRuleFound
        if not ( wfactionObj.need_prev_status == wfdocObj.prev_status and 
                 wfactionObj.need_current_status == wfdocObj.current_status):
            raise rexc.WorkflowActionRuleViolation(intended_action, 
                                                   wfactionObj.need_prev_status,        
                                                 wfactionObj.need_current_status)
        default_roles = [None, "admin",] 
        permitted_to_roles = default_roles + wfactionObj.permitted_to_roles
        if  self.role  not in permitted_to_roles :
            raise rexc.RoleNotPermittedForThisAction(self.role, permitted_to_roles)
        
    def _check_editiable_fields(self, wfdocObj):
        '''this is not required , just keeping in for future purpose sincee the logic is correctly developed'''
        conf_fieldobj_lst = wfdocObj.associated_doctype.datadocfields
        for k, v in wfdocObj.doc_data.items():
            for confObj in conf_fieldobj_lst:
                if confObj.name == k and \
                wfdocObj.current_status not in confObj.status_needed_edit:
                    raise rexc.EditNotAllowedForThisField(k, 
                                                          wfdocObj.current_status,
                                                          confObj.status_needed_edit)
                    
    def _validate_editable_fields(self, wfdocObj, data:dict):
        if data:
            for k in data.keys():
                efac = wfdocObj.editable_fields_at_current_status
                if not k in efac:
                    raise rexc.EditNotAllowedForThisField(k, 
                                                          wfdocObj.current_status,
                                                          efac)
                    
    
        
                
        
            
    
        