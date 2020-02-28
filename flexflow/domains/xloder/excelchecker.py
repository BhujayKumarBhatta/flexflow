import os
import logging
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import pandas as pd
from pandas.api import types as ptypes
import deepdiff
import re
from flexflow.domains.xloder import xluploader_exceptions as xlexc


logger = logging.getLogger(__name__)

class ExcelChecker():
    
    ALLOWED_EXTENSIONS = set(['xlsx', 'xls'])
    UPLOAD_FOLDER = '/tmp/fileupload'   
    
    
    def __init__(self, yml, rcvd_file, wfc=None):
        '''wfc=None is just for backword compatibility'''
        self.wfc = wfc
        self.check_result_list = []
        self.message_list = []        
        self.rcvd_file = rcvd_file
#         print(type(self.rcvd_file))
        self.yml = yml
        if not self.yml.get('upload_excel'): raise xlexc.MissingExcelConfig
        self.excel_configs = self.yml.get('upload_excel')
        self.df = self.convert_excel_to_dataframe()
        
#     def __del__(self):
#         print('Destructor called, ExcelChecker deleted.')

    
    def check_file_extension(self):
        
        if isinstance(self.rcvd_file, FileStorage):
            fname = self.rcvd_file.filename
        else:
            fname = self.rcvd_file
            
        file_extension = '.' in fname and \
               fname.rsplit('.', 1)[1].lower()    
       
        if file_extension in self.ALLOWED_EXTENSIONS:
            result = True
            message = "file extention check passed"
                                  
        else:
            message = "only follwoing format can be uploaded {}".format(
                self.ALLOWED_EXTENSIONS)  
            result = False              
        #print(self.check_result_list)
        self.check_result_list.append(result)
        self.message_list.append(message)        
        return result    
    
    
    def convert_excel_to_dataframe(self):
        if self.check_file_extension():
            try:
                #print('trying to read the xl', self.rcvd_file ) 
                df = pd.read_excel(self.rcvd_file, sheet_name='Sheet1')
                #print('read excel of', df) 
                df.rename(columns=lambda x: x.strip(), inplace=True)                
                #print('renaming columns done',df.columns)            
                df = self.convert_to_proper_data_types(df)
                #print('converting proper data type')               
                return df             
            except Exception as e:
                self.message_list.append("the file doesn't look like excel  or may be corrupted {} "
                                         "the actual error is {}".format(
               self.rcvd_file.filename, str(e)))
                self.check_result = False
        else:
#             self.message_list.append("failed to upload the data in memory for file {}".format(
#                secure_filename(self.rcvd_file.filename)))
            self.message_list.append("failed to upload the data in memory for file {}".format(
               (self.rcvd_file.filename)))
            self.check_result = False
            
            
    def convert_to_proper_data_types(self, df):         
        str_columns = [x.strip() for x in self.excel_configs.get('str_columns')]        
        int_columns = self.excel_configs.get('int_columns')        
        #print('got str column configurations as %s , and int column as'
        #      '  %s' % (str_columns, int_columns))
        try:            
            df.rename(columns=lambda x: x.strip(), inplace=True)                                       
            df[str_columns] = df[str_columns].astype(str)             
            df[int_columns] = df[int_columns].astype(int)            
            df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)           
            return df
        except Exception as e:
            print(e)
            msg = ("excel data type conversion failed. "
                    "check that following columns are text type {}"
                    " and following are integer type {} and "
                     "note the error {}" .format(
                                         str_columns, int_columns, e))
            self.message_list.append(msg) 
            #print(msg)              
            self.check_result = False
            
          
    def check_all_checks(self):        
        if self.df is not None:
            self.check_no_empty_cell_within_data_area()
            self.check_within_max_row()
            #self.check_date_format()
            self.check_cloumn_heading()
            self.check_no_duplicate_invoice_no()
            if self.wfc:            
                self.check_tsp_name_matches_user_org_name()
            #self.check_field_length()
        else:
            return self.check_result
        
    
    def check_no_empty_cell_within_data_area(self):
        if not self.df.isnull().values.any():
            result = True
            message = "check_no_empty_cell_within_data_area=passed"                             
        else:
            result = False
            message = ("blank value is not accepted in the column")                     
            #print(message)
                                
        self.check_result_list.append(result)
        self.message_list.append(message)        
        return result
     
     
    def check_within_max_row(self):
        if len(self.df) > self.excel_configs.get('max_row'):
            message = ("excel format not correct, number of rows must be within {}".format(
               self.excel_configs.get('max_row')))
            #print(message)
            result = False
        else:
            result = True   
            message = "check_within_max_row=passed" 
            
        self.check_result_list.append(result)
        self.message_list.append(message)        
        return result
     
     
    def check_date_format(self):
#         ptypes.is_datetime64_dtype(df['Invoice Date'])        
        pass
        if  ptypes.is_datetime64_any_dtype(self.df['InvoiceDate']):
            message = "Invoice Date column is not date type and data not in dd-mm-yyyy format"
            #print(message)
            result = False
        else:
            result = True   
            message = "check_date_format=passed" 
            
        self.check_result_list.append(result)
        self.message_list.append(message)        
        return result
    
     
    def check_cloumn_heading(self):
        column_headers = self.df.columns.to_list()
        shd_format = self.excel_configs.get('excel_headers')
        shd_format_strip = [i.strip() for i in shd_format]
        
        DIFF = deepdiff.DeepDiff(shd_format_strip, column_headers)
        result_diff = []            
        if DIFF:
            r1=DIFF.get('values_changed')
            pat = "^root\[\'*([^\'\]]+)"            
            for k, v in r1.items():
               k1 = re.search(pat, k)
               k2 = k1.group(1)
               d = {  "suggested_value": v.get('old_value'),
                      "excel_value": v.get('new_value')}
               result_diff.append(d)
               message = ("excel headers are not OK. check the suggested values: "
                          "{}".format(result_diff))            
            result = False        
        else:
            message = "check_cloumn_heading=passed"
            result = True
            
        self.check_result_list.append(result)
        self.message_list.append(message)        
        return result   
     
     
    def check_no_duplicate_invoice_no(self):
        if True in self.df.duplicated().values:
            l=self.df.index[self.df.duplicated('Invoice No')].to_list()
            nl = [str(i) for i in l]
            positions = ",".join(nl)
            result = False
            message = ("Duplicate rows not allowed, check row {}".format(positions))
            #print(message)
            
        else:
            message = "check_no_duplicate_invoice_no=passed"
            result = True
            
        self.check_result_list.append(result)
        self.message_list.append(message)        
        return result   
             
             
    def check_tsp_name_matches_user_org_name(self):        
        valid_tsp_names = self.df["TSP"] == self.wfc.org
        if all(valid_tsp_names) or self.wfc.org is None :
            message = "check_tsp_name=passed"
            result = True
        else:
            invalid_valid_tsp_names = self.df["TSP"] != self.wfc.org
            l=self.df.index[invalid_valid_tsp_names].to_list()
            nl = [str(i) for i in l]
            positions = ",".join(nl)
            result = False
            message = ("check_tsp_name=TSP name should be your login domain name, check row {}".format(positions))
            #print(message)
            logger.error(message)
        self.check_result_list.append(result)
        self.message_list.append(message)        
        return result 
        
        
    def check_field_length(self):
        result = True   
        message = "check_data_length=passed" 
        self.df.dropna(inplace=True)
        xl_allowed_values = self.excel_configs.get('data_length')
        list_of_config_fields  = xl_allowed_values.keys()        
        for conf_field in list_of_config_fields:
            conf_field = conf_field.strip()
            confl = xl_allowed_values.get(conf_field)
            conf_f_len = int(confl) if confl else 0 
            xl_columns_values_str = self.df[conf_field].astype(str)
            for count, f in enumerate(xl_columns_values_str):
                if len(f) > conf_f_len:
                    result = False
                    message = ("{} length should be less or equal to {}, check row {}"
                               .format(conf_field, conf_f_len, str(count)))
                    #print(message)
                    logger.error(message)
                    break
        self.check_result_list.append(result)
        self.message_list.append(message)        
        return result 
                    
    
    
    def check_allowed_data_values(self):
        pass