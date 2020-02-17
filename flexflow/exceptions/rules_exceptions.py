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
        
        
        self.message = ("primary key  %s  is absent in search dictionary  %s"
                        "" %(self.primary_key, self.supplied_value))
        super().__init__(self.status, self.message)
        
        