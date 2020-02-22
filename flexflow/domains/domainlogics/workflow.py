from flexflow.domains.entities import entities as ent
from flexflow.domains.repos import DomainRepo
from flexflow.exceptions import rules_exceptions  as rexc

class Workflow:
    
    def __init__(self, doctype_name:str, role=None):
        self.doctype_name = doctype_name
        self.role = role
    
    def create_doc(self, data:dict):
        ''' a key from the data is treated as the primary key for the 
        document. The key name is defined in the doctype.
        for creation of the doc the condition is no such doc by the id(primary key)
        exists in the repo.
        
        Also see wfdocObj initialization. Earlier we used to call the storage classes from sqlalchemy or mongoengine for creating the object, now we are using domain entities 
        '''
        doctyoeObj = self._get_doctype_obj_from_name()
        primkey_in_datadoc = doctyoeObj.primkey_in_datadoc
        if not data.get(primkey_in_datadoc):
            raise rexc.PrimaryKeyNotPresentInDataDict(primkey_in_datadoc)
        docid = data.get(primkey_in_datadoc)
        if self._get_wfdoc_by_name(docid):
            raise rexc.DuplicateDocumentExists(docid)
        ##TODO: check if the role permits for doc creation
        ###earlier we used to call the storage classes from sqlalchemy or mongoengine for creating the object, now we are using domain entities 
        wfdocObj = ent.Wfdoc(name=docid,
                         associated_doctype=doctyoeObj,
                         prev_status="",
                         current_status="Created",
                         doc_data=data)
        wfdoc_repo = DomainRepo("Wfdoc")
        msg = wfdoc_repo.add_list_of_domain_obj([wfdocObj])
        return msg
    
    def action_change_status(self, wfdoc_name, intended_action):
        wfdocObj = self._get_wfdoc_by_name(wfdoc_name)
        wfactions_list = wfdocObj.wfactions
        wfactionObj = None
        for item in wfactions_list:
            if item.name == intended_action:
                wfactionObj = item
                break
        self._check_action_rules(wfdocObj, wfactionObj, intended_action)
        self._check_editiable_fields(wfdocObj)
        #wfdocObj.current_status = wfactionObj.leads_to_status #TODO: it should be done this way
        wfdoc_repo = DomainRepo("Wfdoc")
        updated_data_dict = {"current_status": wfactionObj.leads_to_status,
                             "prev_status": wfdocObj.current_status}
        target_doc_name = {"name": wfdocObj.name}
        msg = wfdoc_repo.update_from_dict(updated_data_dict, **target_doc_name)
        return msg
        
        
      
    def _get_doctype_obj_from_name(self):
        '''search by primary key name, hence expected to get one object'''
        result = None
        search_dict = {"name": self.doctype_name}
        doctype_repo = DomainRepo("Doctype")
        lst = doctype_repo.list_domain_obj(**search_dict)
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
        conf_fieldobj_lst = self.associated_doctype.datadocfields
        for k, v in wfdocObj.doc_data.items():
            for confObj in conf_fieldobj_lst:
                if confObj.status_needed_edit == k and \
                self.role not in confObj.status_needed_edit:
                    raise rexc.EditNotAllowedForThisField(k, 
                                                          self.role,
                                                          confObj.status_needed_edit)
                     
                
        
            
    
        