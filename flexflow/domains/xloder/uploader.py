import logging
from  json import dumps
from flexflow.domains.xloder.excelchecker import ExcelChecker
from flexflow.domains.domainlogics.workflow import Workflow
from flexflow.domains.xloder import xluploader_exceptions as xlexc

logger = logging.getLogger(__name__)
#netstat -ano | findstr 5002 in windows

class XLReceiver:
    ''' get xlfile from http request
    convert to list of dictionaries after validation
    '''
        
    def __init__(self, conf, wfc, request=None, xlfile=None):
        if not request and not xlfile:
            print('either request or xlfile if required to initiate the class')
        self.conf = conf
        self.yml = conf.yml
        self.request = request
        self.wfc = wfc
        self.request_id = wfc.request_id
        if xlfile:
            self.xlfile = xlfile
        else:
            _, self.xlfile = self._get_xl_from_request()
        #bypassing the chk_result to get only lod
        _, self.lod = self._get_lod_from_xl_after_validate()
        self.lower_key_dict = self._convert_dict_in_lod_with_lower_key(self.lod)
        #bypass lod and get chk result
        self.xl_chk_status, _ = self._get_lod_from_xl_after_validate()
        self.message = {'wfcdict': self.wfc.to_dict(),
                        'lod': self.lod,
                        'msg_source': "TspXLPosted",
                        'save_status': self.xl_chk_status.get('checking_message_list'),
                        'invoice_num': "excel-upload-%s" %self.wfc.request_id}
#         self.json_message = json.dumps(self.message)
        #print(self.message)        
        logger.debug('initialization result ', self.message )
    
    def _lower_case_keys(self, input_dict):
        lower_key_dict = {}
        for k, v in input_dict.items():
            lowerk = k.lower()
            lower_key_dict.update({lowerk: v})
        return lower_key_dict
    
    def _convert_dict_in_lod_with_lower_key(self, lod):
        return [self._lower_case_keys(d) for d in lod]
            
    
    def action_from_lod(self, role, doctype_name):
        response_list = []
        if not self.lower_key_dict:
            raise xlexc.NoDataExtractedFromExcel        
        for xl_dict in self.lower_key_dict:
            if xl_dict.get('doctype'): doctype_name = xl_dict.get('doctype')                
            if xl_dict.get('action').lower() == "create":
                wf = Workflow(doctype_name)
                status_msg_dict = wf.create_doc(xl_dict, role)
                response_list.append(status_msg_dict)
        logger.debug('got response list after calling the  the'
                     ' workflow create_doc', status_msg_dict)       
        return response_list                  
        
    def _get_xl_from_request(self):
        if self.request.method == 'POST' or self.request.method == 'PUT':
            if 'file' not in self.request.files:
                r = {"status": "no file sent in the request"}
            else:
                received_file = self.request.files['file']
                if received_file.filename == '':
                    r = {"status": "no file name in the request"}             
                else:
                    r = {"status": "file reiceved for verifiaction" }
        return r , received_file
    
    def _get_lod_from_xl_after_validate(self):
        '''
        #lod=list of dictionaries       '''
           
        c = ExcelChecker(self.yml, self.xlfile, wfc=self.wfc)       
        c.check_all_checks()        
        check_status = {"checking_result_list": c.check_result_list,
                "checking_message_list": c.message_list }
        if not all(c.check_result_list): raise xlexc.ExcelCheckFailed(c.message_list)        
        df = c.df        
        if df is not None and all(c.check_result_list):
            excel_to_dict_list = df.to_dict('records')
        else:
            excel_to_dict_list = None
        return check_status, excel_to_dict_list
    
#     def notify(self):
#         result = None
#         if self.lod:
#             result = mixed_actions(self.conf, self.wfc, self.lod)
#         else:
#             result = {"response_list":[self.message]} #list because sucess results are in result_list
#         #print('xlloader calling mixed actions', result)
#         return result
#   