from flexflow.domains.entities import entities as ent
from flexflow.domains.repos import DomainRepo
from flexflow.exceptions import rules_exceptions  as rexc
from backports.configparser.helpers import str
from flexflow.domains import utils

class Workflow:
    
    def __init__(self, doctype_name:str, role=None, wfc=None):
        self.doctype_name = doctype_name
        self.wfc = wfc
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
        self._check_role_for_create_action(doctyoeObj, roles) ## remeber fields validation is done during documents init method
        wfdocObj = ent.Wfdoc(name=docid,
                         associated_doctype=doctyoeObj,                         
                         prev_status="NewBorn",
                         current_status="Created",
                         doc_data=data) ###earlier we used to call the storage classes from sqlalchemy or mongoengine for creating the object, now we are using domain entities 
        self._validate_editable_fields(wfdocObj, data) #aprt from edit and length validtion, data type is converted as per the conf 
        wfdoc_repo = DomainRepo("Wfdoc")
        msg = wfdoc_repo.add_list_of_domain_obj([wfdocObj])
        return msg
    
    def get_full_wfdoc_as_dict(self, wfdoc_name, roles:list):
        '''in workflow role is avilable , hence , wfdocObj.actions_for_current_status gets further filtered by roles before presenting in dict format'''
        wfdocObj = self._get_wfdoc_by_name(wfdoc_name)
        current_actions = []
        for actionObj in wfdocObj.actions_for_current_status:
            for role in roles:
                if role in actionObj.permitted_to_roles:
                    current_actions.append(actionObj.name)
        current_edit_fields = [fObj.name.lower() for fObj in wfdocObj.editable_fields_at_current_status]
        wfdoc_dict = wfdocObj.to_dict()
        wfdoc_dict.update({"current_actions": current_actions,
                           "current_edit_fields": current_edit_fields})
        return wfdoc_dict
        
    
    def action_change_status(self, wfdoc_name, intended_action, roles:list, input_data=None):
        wfdocObj = self._get_wfdoc_by_name(wfdoc_name)
        wfactions_list = wfdocObj.wfactions
        wfactionObj = None
        for item in wfactions_list:
            if item.name == intended_action:
                wfactionObj = item
                break
        self._check_action_rules(wfdocObj, wfactionObj, intended_action, roles)
        self._validate_editable_fields(wfdocObj, input_data)
        #wfdocObj.current_status = wfactionObj.leads_to_status #TODO: it should be done this way
        wfdoc_repo = DomainRepo("Wfdoc")
        updated_data_dict = {"current_status": wfactionObj.leads_to_status,
                             "prev_status": wfdocObj.current_status}
        if input_data:
            existing_data = wfdocObj.doc_data
            existing_data.update(input_data)
            updated_data_dict.update({"doc_data": existing_data})
            
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
            if actionObj.name.lower() == "create":
                for  role in roles:
                    print("role checking before create", roles, actionObj.permitted_to_roles)
                    if role in actionObj.permitted_to_roles:
                        print('role matched, hence setitnf role_not_found as false')
                        role_not_found = False
                        break
                    else:
                        print('role not found is true')
                        role_not_found = True
                action_not_found = False
                break
            else:
                action_not_found = True
        print('status of role_not_found', role_not_found)         
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
        if not lst:
            conf_lst = doctype_repo.list_domain_obj()
            raise rexc.DocCategoryNotConfigured(self.doctype_name, conf_lst)
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
    
    def _check_action_rules(self, wfdocObj, wfactionObj, intended_action, roles:list):
        if not wfactionObj:
            raise rexc.NoWorkFlowRuleFound
        default_roles = [None, "admin",] 
        permitted_to_roles = default_roles + wfactionObj.permitted_to_roles
        for role in roles:
            if  role in permitted_to_roles: 
                role_matched = True
                break
            else:
                role_matched = False
        if role_matched is False:
                raise rexc.RoleNotPermittedForThisAction(roles, permitted_to_roles)
        if not ( wfactionObj.need_prev_status == wfdocObj.prev_status and 
                 wfactionObj.need_current_status == wfdocObj.current_status):
            raise rexc.WorkflowActionRuleViolation(intended_action, 
                                                   wfactionObj.need_prev_status,        
                                                 wfactionObj.need_current_status)
        
        
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
            efacs_list = wfdocObj.editable_fields_at_current_status
            efacs_names = [fObj.name.lower() for fObj in efacs_list]  
            for k, v in data.items():
                if k.lower() not in efacs_names:
                        raise rexc.EditNotAllowedForThisField(k, wfdocObj.current_status, efacs_names)
                for fieldObj in efacs_list:
                    if k.lower() == fieldObj.name.lower():
                        flength = fieldObj.flength
                        if not len(str(v)) <= flength:
                            raise rexc.DataLengthViolation(k, len(v), flength)
                        ctype = fieldObj.ftype.lower()
                        utils.convert_data_values_as_per_conf(ctype, data, k, v)
        return data
                        
    
    def _create_audit_record(self, wfdocObj, input_data:dict):
        WfdocauditObj = ent.Wfdocaudit(request_id=self.wfc.request_id,
                                       wfdoc=wfdocObj, 
                                       username=self.wfc.username, 
                                       email=self.wfc.email, 
                                       time_stamp=self.wfc.time_stamp, 
                                       client_address=self.wfc.client_address, 
                                       org=self.wfc.org, 
                                       orgunit=self.wfc.orgunit, 
                                       department=self.wfc.department, 
                                       roles=self.wfc.roles, 
                                       data=input_data,)
        wfdocaudit_repo = DomainRepo('Wfdocaudit')
        wfdocaudit_repo.add_list_of_domain_obj(list_of_domain_obj)
        
                    
                            
#     def _validate_editable_fields(self, wfdocObj, data:dict):
#         if data:
#             for k in data.keys():
#                 efac = [fObj.name for fObj in wfdocObj.editable_fields_at_current_status]
#                 if not k in efac:
#                     raise rexc.EditNotAllowedForThisField(k, 
#                                                           wfdocObj.current_status,
#                                                           efac)
                    
    
        
                
        
            
    
        