import json


class XLUploaderException(Exception):
    status = "UNKNOWN_STATUS"
    message = "Unknown status"

    def __init__(self, status=None, message=None):
        if status:  self.status = status
        if message: self.message = message
        self.ret_val = {"status": self.status, "message": self.message }
        super(XLUploaderException, self).__init__(self.status, self.message)

    def __str__(self):
        return json.dumps(self.ret_val)


    def __repr__(self):
        return self.ret_val
    
class NoDataExtractedFromExcel(XLUploaderException):
    status = "NoDataExtractedFromExcel"  
    message = "Conversion from Excel data to a 'None' or Blank  data dictionary " 
    
class InvalidDocCategory(XLUploaderException):
    status = "InvalidDocCategory"    
    def __init__(self, status_doc_category, list_doc_category):
        self.status_doc_category = status_doc_category
        self.list_doc_category = list_doc_category
        self.message = ("Cant add status for doctype  %s in the %s status list."
                        "" %(self.status_doc_category, self.list_doc_category))
        super().__init__(self.status, self.message)
        
    
