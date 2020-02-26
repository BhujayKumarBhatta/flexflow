from  flexflow.exceptions.parent_exception import FlexFlowException

class InvalidInputDataList(FlexFlowException):
    status = "InvalidInputDataList"  
    message = "Data must be  list(json array) type"
    
class InvalidInputDataDict(FlexFlowException):
    status = "InvalidInputDataDict"  
    message = "Data must be  dictionary(json object) type" 
    
        
class InvalidDocCategory(FlexFlowException):
    status = "InvalidDocCategory"    
    def __init__(self, status_doc_category, list_doc_category):
        self.status_doc_category = status_doc_category
        self.list_doc_category = list_doc_category
        self.message = ("Cant add status for doctype  %s in the %s status list."
                        "" %(self.status_doc_category, self.list_doc_category))
        super().__init__(self.status, self.message)
        
class InvalidWorkflowObject(FlexFlowException):
    status = "InvalidWorkflowObject"    
    def __init__(self, objname, domain_obj_names):
        self.objname = objname
        self.domain_obj_names = domain_obj_names
        self.message = ("Invalid workflow object name: %s, it should be one from %s."
                        "" %(self.objname, self.domain_obj_names))
        super().__init__(self.status, self.message)
        
        
class InvalidKeysInData(FlexFlowException):
    status = "InvalidKeysInData"    
    def __init__(self, inputkey, object_attributes):
        self.inputkey = inputkey
        self.object_attributes = object_attributes
        self.message = ("The key name '%s' is Invalid in Input data, it should be one from %s."
                        "" %(self.inputkey, self.object_attributes))
        super().__init__(self.status, self.message)
        
class SearhKeyNotProvided(FlexFlowException):
    status = "SearhKeyNotProvided"  
    message = "Provide a search filter for the record you want to update"
    
class InvalidObjTypeInInputParam(FlexFlowException):
    status = "InvalidObjTypeInInputParam"    
    def __init__(self, param_name, required_value):
        self.param_name = param_name
        self.required_value = required_value.__name__
        
        
        self.message = ("value for %s parameter must be a class of %s"
                        "" %(self.param_name, self.required_value))
        super().__init__(self.status, self.message)
        
class PrimaryKeyNotPresentInSearch(FlexFlowException):
    status = "PrimaryKeyNotPresentInSearch"    
    def __init__(self, primary_key, supplied_value):
        self.primary_key = primary_key
        self.supplied_value = supplied_value
        
        
        self.message = ("primary key: '%s',   is absent in search dictionary  %s"
                        "" %(self.primary_key, self.supplied_value))
        super().__init__(self.status, self.message)
        
class PrimaryKeyNotPresentInDataDict(FlexFlowException):
    status = "PrimaryKeyNotPresentInDataDict"    
    def __init__(self, primary_key):
        self.primary_key = primary_key
        self.message = ("primary key: '%s',   is absent in input data dictionary"
                        "" %(self.primary_key))
        super().__init__(self.status, self.message)
        
class DuplicateDocumentExists(FlexFlowException):
    status = "DuplicateDocumentExists"    
    def __init__(self, primary_key):
        self.primary_key = primary_key
        self.message = ("document creation failed since duplicate document"
                        "by the id: '%s',   already exists"
                        "" %(self.primary_key))
        super().__init__(self.status, self.message)
        
class WorkflowActionRuleViolation(FlexFlowException):
    status = "WorkflowActionRuleViolation"    
    def __init__(self, intended_action, need_previous_status, need_current_status):
        self.need_previous_status = need_previous_status
        self.need_current_status = need_current_status
        self.intended_action = intended_action
        self.message = ("Action: %s need previous status to be: %s and current status to be: "
                        "%s " %(self.intended_action, self.need_previous_status,
                                self.need_current_status))
        super().__init__(self.status, self.message)
        
class NoWorkFlowRuleFound(FlexFlowException):
    status = "NoWorkFlowRuleFound"    
    message = "Check the document type associated with this doc and action rules defined for the doctype" 
        

class RoleNotPermittedForThisAction(FlexFlowException):
    status = "RoleNotPermittedForThisAction"    
    def __init__(self, your_role, permitted_roles):
        self.your_role = your_role
        for idx, item  in enumerate(permitted_roles):
            if item in [ None, "admin"]:
                permitted_roles.pop(idx)
        self.permitted_roles = permitted_roles
        self.message = ("Your role: %s has not been granted permission for this action."
                        " only follwoing roles have the "
                        "permission:%s " %(self.your_role, self.permitted_roles))
        super().__init__(self.status, self.message)
        
class UnknownFieldNameInDataDoc(FlexFlowException):
    status = "UnknownFieldNameInDataDoc"    
    def __init__(self, fname, supporetd_fields):
        self.fname = fname        
        self.supporetd_fields = supporetd_fields
        self.message = ("Unknown field name: %s in data doc, it should be one of"
                        ":%s " %(self.fname, self.supporetd_fields))
        super().__init__(self.status, self.message)
        
class DataTypeViolation(FlexFlowException):
    status = "DataTypeViolation"    
    def __init__(self, fname, supplied_type, supported_type):
        self.fname = fname        
        self.supplied_type = supplied_type
        self.supported_type = supported_type
        self.message = ("data type: %s for field: %s is invalid, supported "
                        "type is :%s " %(self.fname, self.supplied_type, self.supported_type))
        super().__init__(self.status, self.message)
        
class DataLengthViolation(FlexFlowException):
    status = "DataLengthViolation"    
    def __init__(self, fname, supplied_length, supported_length):
        self.fname = fname        
        self.supplied_type = supplied_length
        self.supported_type = supported_length
        self.message = ("data length: %s for field: %s is invalid, supported "
                        "length is :%s " %(self.fname, self.supplied_type, self.supported_type))
        super().__init__(self.status, self.message)
               
class NoDataInDocument(FlexFlowException):
    status = "NoDataInDocument"    
    message = "Any operation in the document must be accompanied by at least one data"
    
class EditNotAllowedForThisField(FlexFlowException):
    status = "EditNotAllowedForThisField"    
    def __init__(self, fname, supplied_role, supported_roles):
        self.fname = fname        
        self.supplied_role = supplied_role
        self.supported_roles = supported_roles
        self.message = ("Field : %s is not allowed to edited when current status is: %s, supported "
                        "status for edit are :%s " %(self.fname, self.supplied_role, self.supported_roles))
        super().__init__(self.status, self.message)
    
    
class NoActionRuleForCreate(FlexFlowException):
    status = "NoActionRuleForCreate"    
    message = "Ask admin to define a Action Rule (Wfaction) master  named as 'Create' with status leading to 'Created' and previous and current status as 'NewBorn' " 