
from flexflow.exceptions.parent_exception import FlexFlowException


# class XLUploaderException(Exception):
#     status = "UNKNOWN_STATUS"
#     message = "Unknown status"
# 
#     def __init__(self, status=None, message=None):
#         if status:  self.status = status
#         if message: self.message = message
#         self.ret_val = {"status": self.status, "message": self.message }
#         super(XLUploaderException, self).__init__(self.status, self.message)
# 
#     def __str__(self):
#         return json.dumps(self.ret_val)
# 
# 
#     def __repr__(self):
#         return self.ret_val
    
class NoDataExtractedFromExcel(FlexFlowException):
    status = "NoDataExtractedFromExcel"  
    message = "Conversion from Excel data to a 'None' or Blank  data dictionary " 
    
class MissingExcelConfig(FlexFlowException):
    status = "MissingExcelConfig" 
    message = "'upload_excel' key and related configs are missing from the config file "

        
        
class ExcelCheckFailed(FlexFlowException):
    status = "ExcelCheckFailed"    
    def __init__(self, excel_check_result):
        self.excel_check_result = excel_check_result       
        self.message = ("Note the failed test and rectify. The test result is :  %s "
                        "" %(self.excel_check_result))
        super().__init__(self.status, self.message)
        
    
