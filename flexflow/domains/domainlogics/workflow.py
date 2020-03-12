import itertools
from flexflow.domains.entities import entities as ent
from flexflow.domains.repos import DomainRepo
from flexflow.exceptions import rules_exceptions  as rexc
from backports.configparser.helpers import str
from flexflow.domains import utils
from alembic.command import current




class Workflow:
    
    def __init__(self, doctype_name:str, wfc=None):
        self.doctype_name = doctype_name
        self.wfc = wfc
    
    def create_doc(self, input_data:dict):
        ''' a key from the data is treated as the primary key for the 
        document. The key name is defined in the doctype.
        for creation of the doc the condition is no such doc by the id(primary key)
        exists in the repo.
        
        Also see wfdocObj initialization. Earlier we used to call the storage classes from sqlalchemy or mongoengine for creating the object, now we are using domain entities 
        '''
        doctyoeObj = self._get_doctype_obj_from_name()
        docid = self._get_primary_key_from_data_doc(doctyoeObj, input_data)
        lead_to_status, create_action_name = \
        self._check_role_for_create_action(doctyoeObj, self.wfc.roles) ## remeber fields validation is done during documents init method
        print('got the lead to status ', lead_to_status )
        wfdocObj = ent.Wfdoc(name=docid,
                         associated_doctype=doctyoeObj,                         
                         prev_status="NewBorn",
                         current_status=lead_to_status,
                         doc_data=input_data) ###earlier we used to call the storage classes from sqlalchemy or mongoengine for creating the object, now we are using domain entities 
        self._validate_editable_fields(wfdocObj, input_data, new_born=True) #Bypasss edit control checking during creation. aprt from  length validtion, data type is converted as per the conf 
        result = self._create_with_audit(wfdocObj, docid, input_data)
        #push it to hold doc for create action
        #during listing from hold doc since the "reason' is create , during super impose pop it from the list
        self._unhide_or_hide_action_to_roles(wfdocObj, create_action_name, new_born=True ) #intended_action=create
        return result    
    
    def list_wfdoc(self):
        wfc_filter = self._get_list_filter_fm_wfc_to_field_map()
        wfdoc_list = self._list_from_wfdoc(wfc_filter)
        holddoc_lis = self._list_from_holddoc_filtered_by_logged_in_user_roles(wfc_filter)
        list_with_hold = self._superimpose_holddoc_on_wfdoc(wfdoc_list, holddoc_lis)
        return list_with_hold
    
    def _get_list_filter_fm_wfc_to_field_map(self):
        doctypeObj = self._get_doctype_obj_from_name()
        org = None,
        ou = None, 
        dept = None, 
        searchf = {}
        for ddf in doctypeObj.datadocfields:
            fwfc = ddf.wfc_filter.lower().strip()
            f_wfc_roles = ddf.wfc_filter_to_roles         
            if fwfc == "org" and self._comp_conf_roles_with_login_role(f_wfc_roles):
                searchf = {ddf.name: self.wfc.org}
            if fwfc == "ou" and  self._comp_conf_roles_with_login_role(f_wfc_roles):
                #ou = ddf.wfc_filter
                searchf.update({ddf.name: self.wfc.orgunit})
            if fwfc == "dept" and self._comp_conf_roles_with_login_role(f_wfc_roles):
                #dept = ddf.wfc_filter
                searchf.update({ddf.name: self.wfc.department})
        if searchf: searchf = {'doc_data' : searchf }
        return searchf
    
    def _comp_conf_roles_with_login_role(self, conf_roles):
        role_comp_result = False        
        login_roles_in_lower = [role.strip().lower() for role in self.wfc.roles]        
        f_wfc_roles = [role.strip().lower() for role in conf_roles]
        cartesian_product = itertools.product(login_roles_in_lower, f_wfc_roles)
        role_comp_result = any(list(map(lambda x: x[0] == x[1], cartesian_product)))
        return role_comp_result
        
    
    def get_full_wfdoc_as_dict(self, wfdoc_name):
        '''in workflow role is avilable , hence 
        wfdocObj.actions_for_current_status gets further filtered by 
        roles before presenting in dict format'''
        wfdocObj = self._get_wfdoc_by_name(wfdoc_name)
        current_actions = self._get_current_actions_for_the_doc(wfdocObj)
        current_edit_fields = [fObj.name.lower().strip() for fObj in 
                               wfdocObj.editable_fields_at_current_status]
        roles_to_view_audit = wfdocObj.roles_to_view_audit
        audittrails = self._get_audit_trails_for_allowed_roles(wfdocObj, roles_to_view_audit)
        wfdoc_dict = wfdocObj.to_dict()
        hodl_doc_dict = self._get_detail_holddoc_for_a_wfdoc(wfdoc_dict)
        if hodl_doc_dict and isinstance(hodl_doc_dict, dict): wfdoc_dict.update(hodl_doc_dict)
        wfdoc_dict.update({"current_actions": current_actions,
                           "current_edit_fields": current_edit_fields,
                           "audittrails": audittrails,
                           "roles_to_view_audit": roles_to_view_audit })
        return wfdoc_dict
    
    def _get_detail_holddoc_for_a_wfdoc(self, wfdoc_dict):
        hodl_doc_dict = None
        holddoc_repo = DomainRepo('Holddoc')
        for urole in self.wfc.roles: #for multiple roles, only the first match is considered
            search_f = {#"associated_doctype_name": self.doctype_name, #TODO: reinforce once update restapi takes <doctype> as param
                    "wfdoc_name": wfdoc_dict.get('name'),
                    "target_role": urole, 
                    "name": urole+wfdoc_dict.get('name')}
            print('serach string ...........', search_f)
            result = holddoc_repo.list_dict(**search_f)
            if result: 
                hodl_doc_dict = result[0]
                print('got result from holddoc...........', hodl_doc_dict)
                break
        return hodl_doc_dict
    
    def _get_audit_trails_for_allowed_roles(self, wfdocObj, roles_to_view_audit):
        audittrails = []
        for auditObj in wfdocObj.wfdocaudits:
            d1 = auditObj.to_dict()
            d1.pop('wfdoc')
            for role in self.wfc.roles:
                if role in roles_to_view_audit:
                    audittrails.append(d1)
        return audittrails
    
    def _get_current_actions_for_the_doc(self, wfdocObj):
        current_actions = []
        for actionObj in wfdocObj.actions_for_current_status:
            permitted_to_roles = [prole.lower().strip() for prole in actionObj.permitted_to_roles]
            for role in self.wfc.roles:
                print('login role and permitted roles', role, actionObj.permitted_to_roles)
                if role.strip().lower() in permitted_to_roles:
                    current_actions.append(actionObj.name)
        print('current actions', current_actions)
        return current_actions        
        
    def get_full_wfdoctype_as_dict(self):
        wfdoctypeObj = None
        wfdoctype_repo = DomainRepo('Doctype')
        wfdoctypeObj = wfdoctype_repo.list_domain_obj(**{"name": self.doctype_name})       
        if wfdoctypeObj: wfdoctypeObj = wfdoctypeObj[0]
        datadocfields = []
        for fObj in wfdoctypeObj.datadocfields:
            fdict = fObj.to_dict()
            fdict.pop('associated_doctype')
            fdict.pop('associated_doctype_name')            
            datadocfields.append(fdict)
        wfdoctype_dict = wfdoctypeObj.to_dict()
        wfdoctype_dict.update({"datadocfields": datadocfields})
        return utils.lower_case_keys(wfdoctype_dict)
        
    def _list_from_wfdoc(self, wfc_filter:dict=None):
        wfdoc_repo = DomainRepo('Wfdoc')
        search_f = {"associated_doctype_name": self.doctype_name}
        #if wfc_filter: search_f.update(wfc_filter)
        lst = wfdoc_repo.list_dict(**search_f)
        if wfc_filter: lst = self._filter_by_wfc_on_doc_data(lst, wfc_filter)
        return lst
    
    def _filter_by_wfc_on_doc_data(self, original_list, wfc_filter):
        list_with_wfc_filter_on_doc_data = []
        for doc in original_list:
            for k, v in wfc_filter.get('doc_data').items():
                if doc.get('doc_data').get(k) == v:list_with_wfc_filter_on_doc_data.append(doc)
        return list_with_wfc_filter_on_doc_data
        
    
    def _list_from_holddoc_filtered_by_logged_in_user_roles(self, wfc_filter=None):
        wfdoctype_repo = DomainRepo('Holddoc')
        search_f = {"associated_doctype_name": self.doctype_name}
        if wfc_filter: search_f.update(wfc_filter)
        lst = wfdoctype_repo.list_dict(**search_f)
        if wfc_filter: lst = self._filter_by_wfc_on_doc_data(lst, wfc_filter)
        holddocs_filter_by_role = []
        for urole in self.wfc.roles:
            for hold_doc in lst:
                if urole == hold_doc.get('target_role'):
                    holddocs_filter_by_role.append(hold_doc)                
        return holddocs_filter_by_role
    
    def _superimpose_holddoc_on_wfdoc(self, wfdoc_list, holddoc_lis):
        for i, wfd in enumerate(wfdoc_list):
            for hld in holddoc_lis:
                if wfd.get('name') == hld.get('wfdoc_name'):                    
                    hld['name'] = wfd.get('name')#othewise it will show holddoc name = role+docname and fail to retrive it during detial view
                    wfd.update(hld)
                    if hld.get('current_status').lower().strip() in  [ "", "newborn"]:
                        print('hold exixists for newly creatd doc for' , hld.get('current_status').lower().strip())
                        wfdoc_list.pop(i)
        return wfdoc_list
    
    def action_change_status(self, wfdoc_name, intended_action, input_data=None):
        wfdocObj = self._get_wfdoc_by_name(wfdoc_name)
        wfactionObj = self._get_wfactionObj(wfdocObj, intended_action)        
        self._check_action_rules(wfdocObj, wfactionObj, intended_action, self.wfc.roles)
        self._validate_editable_fields(wfdocObj, input_data)
        self._unhide_or_hide_action_to_roles(wfdocObj, intended_action, new_born=False)
        changed_data = self._create_changed_data(input_data, wfdocObj, wfactionObj)
        result = self._updadate_with_audit(wfdocObj, intended_action, changed_data)
        return result
    
    def _get_roles_for_undo_prev_hide(self, wfdocObj, intended_action):
        undo_prev_hide_for = []
        for actionObj in wfdocObj.wfactions:
            if actionObj.name == intended_action:
                undo_prev_hide_for = actionObj.undo_prev_hide_for
                break
        return undo_prev_hide_for 
    
    def _delete_prev_holddoc_by_unhide_roles(self, wfdocObj, intended_action, holddoc_repo):        
        unhide_to_roles = self._get_roles_for_undo_prev_hide(wfdocObj, intended_action)
        for unh_role in unhide_to_roles:
            search_string = {"wfdoc_name": wfdocObj.name,
                             "target_role": unh_role,
                             "name": unh_role+wfdocObj.name}
            msg = holddoc_repo.delete(**search_string)#TODO: should be no doc found when not present
            print('deleting holddoc .....................',msg)
            
    def _unhide_or_hide_action_to_roles(self, wfdocObj, intended_action, new_born):
        holddoc_repo = DomainRepo("Holddoc")
        self._delete_prev_holddoc_by_unhide_roles(wfdocObj, intended_action, holddoc_repo)
        hide_to_roles = self._get_hide_to_roles_from_wfdoc(wfdocObj, intended_action)        
        if isinstance(hide_to_roles, list) and len(hide_to_roles) > 0:
            for urole in hide_to_roles:           
                self._create_holddoc_for_current_role(urole, intended_action, wfdocObj, holddoc_repo, new_born)
    
    def _get_holddoc_by_role(self, wfdocObj, role, holddoc_repo):
        search_string = {"wfdoc_name": wfdocObj.name,
                         "target_role": role,
                         "name": role+wfdocObj.name}
        holddoc = holddoc_repo.list_dict(**search_string)
        return holddoc
      
    def _create_holddoc_for_current_role(self, urole, intended_action, wfdocObj, holddoc_repo, new_born=False):
        result = None
        unique_id = urole+wfdocObj.name
        print('hoding with name....................', unique_id)
        holddoc_list = self._get_holddoc_by_role(wfdocObj, urole, holddoc_repo)
        cstatus = wfdocObj.current_status
        if new_born == True: cstatus = ""
        if isinstance(holddoc_list, list) and len(holddoc_list) == 0:
            holddocObj = ent.Holddoc(name=unique_id,
                                     target_role=urole,
                                     reason=intended_action,
                                     wfdoc=wfdocObj,
                                     associated_doctype = wfdocObj.associated_doctype,
                                     prev_status=wfdocObj.prev_status,
                                     current_status=cstatus,
                                     doc_data=wfdocObj.doc_data)
            result = holddoc_repo.add_list_of_domain_obj([holddocObj])
        return result
    
    def _get_hide_to_roles_from_wfdoc(self, wfdocObj, intended_action):
        hide_to_roles = []
        for actionObj in wfdocObj.wfactions:
            if actionObj.name == intended_action:
                hide_to_roles = actionObj.hide_to_roles
                break
        return hide_to_roles            
     
    def _create_with_audit(self, wfdocObj, docid, input_data):
        wfdoc_repo = DomainRepo("Wfdoc")
        msg = wfdoc_repo.add_list_of_domain_obj([wfdocObj])
        try:
            audit_msg = self._create_audit_record(wfdocObj, 'Create', input_data)
            msg.update({"audit_msg": audit_msg})
        except (rexc.FlexFlowException, Exception)  as e:
            status = wfdoc_repo.delete(**{"name": docid})
            #status_roll_back_holddoc = holddoc_repo.delete(**search_filter)
            rollback_msg = {"status": status, "message": str(e) }
            msg.update({"rollback_msg": rollback_msg})
            raise rexc.FlexFlowException
        return msg
        
    def _updadate_with_audit(self, wfdocObj, intended_action, changed_data ):
        wfdoc_repo = DomainRepo("Wfdoc")
        target_doc_name = {"name": wfdocObj.name}
        msg = wfdoc_repo.update_from_dict(changed_data, **target_doc_name)
        try:
            audit_msg = self._create_audit_record(wfdocObj, intended_action,  changed_data)
            msg.update({"audit_msg": audit_msg})
        except Exception:
            updated_data_dict = {"current_status": wfdocObj.current_status,
                                 "prev_status": wfdocObj.prev_status,
                                 "doc_data": wfdocObj.doc_data}
            rollback_msg = wfdoc_repo.update_from_dict(updated_data_dict, **target_doc_name)
            msg.update({"rollback_msg": rollback_msg})
            raise Exception
        return msg    
    
    def _create_changed_data(self, input_data, wfdocObj, wfactionObj):
        #wfdocObj.current_status = wfactionObj.leads_to_status #TODO: it should be done this way
        updated_data_dict = {"current_status": wfactionObj.leads_to_status,
                             "prev_status": wfdocObj.current_status}
        if input_data:
            existing_data = wfdocObj.doc_data
            existing_data.update(input_data)
            updated_data_dict.update({"doc_data": existing_data})
        return updated_data_dict
    
    def _get_wfactionObj(self, wfdocObj, intended_action):
        wfactionObj = None
        wfactions_list = wfdocObj.wfactions
        if wfactions_list:  
            for item in wfactions_list:
                if item.name == intended_action:
                    wfactionObj = item
                    break
        return wfactionObj
       
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
        role_not_found = False
        lead_to_status = None
        create_action_name = "Create"
        for actionObj in doctyoeObj.wfactions:
            acptstatus = ["newborn", ""]  
            striped_roles = [ role.strip() for role in actionObj.permitted_to_roles]        
#             if ( actionObj.need_current_status.lower() in acptstatus  and 
#                  actionObj.need_prev_status.lower() in acptstatus):
            need_current_status_list = \
                [ncs.lower().strip() for ncs in actionObj.need_current_status]
            cartesian_product = itertools.product(acptstatus,need_current_status_list)
            comp_result = list(map(lambda x: x[0] == x[1], cartesian_product))
            if any(comp_result):
                lead_to_status = actionObj.leads_to_status.lower()
                print('got the initial stauts..................', lead_to_status)
                for role in roles:
                    print("after removing whitesace , role checking before create", roles, actionObj.permitted_to_roles)
                    if role.strip() in striped_roles:
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
                create_action_name = actionObj.name.strip()
        print('status of role_not_found', role_not_found)         
        if action_not_found is True: raise rexc.NoActionRuleForCreate
        if role_not_found is True:
            raise rexc.RoleNotPermittedForThisAction(role,
                                                      actionObj.permitted_to_roles)
        return lead_to_status, create_action_name
    
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
        permitted_to_roles = default_roles + [prole.lower().strip() for prole 
                                              in wfactionObj.permitted_to_roles]
        luser_role = [role.lower().strip() for role in roles]
        cartesian_product = itertools.product(permitted_to_roles, luser_role)
        role_matched_result = list(map(lambda x: x[0] == x[1], cartesian_product))
        if not any(role_matched_result):
                raise rexc.RoleNotPermittedForThisAction(roles, permitted_to_roles)
#         for role in roles:
#             if  role.strip().lower() in permitted_to_roles: 
#                 role_matched = True
#                 break
#             else:
#                 role_matched = False
#         if role_matched is False:
#                 raise rexc.RoleNotPermittedForThisAction(roles, permitted_to_roles)
#         if not ( wfactionObj.need_prev_status.lower().strip() == wfdocObj.prev_status.lower().strip() and 
#                  wfactionObj.need_current_status.lower().strip() == wfdocObj.current_status.lower().strip()):
        need_current_status_list = \
                [ncs.lower().strip() for ncs in wfactionObj.need_current_status]
        if not wfdocObj.current_status.lower().strip() in need_current_status_list:    
            raise rexc.WorkflowActionRuleViolation(intended_action, 
                                                   #wfactionObj.need_prev_status,        
                                                   wfactionObj.need_current_status)
                 
    def _validate_editable_fields(self, wfdocObj, data:dict, new_born=False):
        if data:
            efacs_list = wfdocObj.editable_fields_at_current_status
            efacs_names = [fObj.name.lower().strip() for fObj in efacs_list]  
            for k, v in data.items():
                if k.lower().strip() not in efacs_names and new_born is False :
                        raise rexc.EditNotAllowedForThisField(k, wfdocObj.current_status, efacs_names)
                for fieldObj in efacs_list:
                    if k.lower() == fieldObj.name.lower():
                        flength = fieldObj.flength
                        if not len(str(v)) <= flength:
                            raise rexc.DataLengthViolation(k, len(v), flength)
                        ctype = fieldObj.ftype.lower()
                        utils.convert_data_values_as_per_conf(ctype, data, k, v)
        return data
    
    def _create_audit_record(self, wfdocObj, intended_action, input_data:dict):
        WfdocauditObj = ent.Wfdocaudit(name=self.wfc.request_id,
                                       wfdoc=wfdocObj, 
                                       username=self.wfc.username, 
                                       email=self.wfc.email, 
                                       time_stamp=self.wfc.time_stamp, 
                                       client_address=self.wfc.client_address, 
                                       org=self.wfc.org, 
                                       orgunit=self.wfc.orgunit, 
                                       department=self.wfc.department,                                       
                                       roles=self.wfc.roles, 
                                       action=intended_action,
                                       data=input_data)
        wfdocaudit_repo = DomainRepo('Wfdocaudit')
        msg = wfdocaudit_repo.add_list_of_domain_obj([WfdocauditObj])
        #print(msg)
        return msg
        
                    
                            
#     def _validate_editable_fields(self, wfdocObj, data:dict):
#         if data:
#             for k in data.keys():
#                 efac = [fObj.name for fObj in wfdocObj.editable_fields_at_current_status]
#                 if not k in efac:
#                     raise rexc.EditNotAllowedForThisField(k, 
#                                                           wfdocObj.current_status,
#                                                           efac)
                    
    def _delete_all_holddoc_for_a_wfdoc(self, wfdocObj):
        '''may not be required any more '''
        search_string = {"wfdoc_name": wfdocObj.name}
        holddoc_repo = DomainRepo("Holddoc")
        result = holddoc_repo.delete(**search_string)#TODO: should be no doc found when not present
        return result
        
                
        
            
    
        