from  flexflow.exceptions.parent_exception import FlexFlowException

class InvalidDocCategory(FlexFlowException):
    status = "InvalidDocCategory"    
    def __init__(self, status_doc_category, list_doc_category):
        self.status_doc_category = status_doc_category
        self.list_doc_category = list_doc_category
        self.message = ("Cant add status for doctype  %s in the %s status list."
                        "" %(self.status_doc_category, self.list_doc_category))
        super(InvalidDocCategory, self).__init__(self.status, self.message)
        
class InvalidWorkflowObject(FlexFlowException):
    status = "InvalidDocCategory"    
    def __init__(self, objname, domain_obj_names):
        self.objname = objname
        self.domain_obj_names = domain_obj_names
        self.message = ("Invalid workflow object name: %s , it should be one from %s."
                        "" %(self.objname, self.domain_obj_names))
        super(InvalidDocCategory, self).__init__(self.status, self.message)
        
        
class InvalidKeysInData(FlexFlowException):
    status = "InvalidDocCategory"    
    def __init__(self, inputkey, object_attributes):
        self.inputkey = inputkey
        self.object_attributes = object_attributes
        self.message = ("Invalid key in Input data: %s , it should be one from %s."
                        "" %(self.inputkey, self.object_attributes))
        super(InvalidDocCategory, self).__init__(self.status, self.message)   