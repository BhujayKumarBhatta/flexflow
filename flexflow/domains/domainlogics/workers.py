from flexflow.domains.domainlogics.workflow import Workflow
from flexflow.domains.xloder import xluploader_exceptions  as xlexc
from flexflow.exceptions import rules_exceptions  as rexc
from flexflow.msgqueue import kafka_producer
from flexflow.domains.xloder.uploader import XLReceiver



def xl_upload(confobj, wfc, doctype_name, request=None, xlfile=None):
    response_list = []
    if xlfile:
        xlreceiver = XLReceiver(confobj, wfc, xlfile=xlfile)
    else:
        xlreceiver = XLReceiver(confobj, wfc, request=request)    
    if not xlreceiver.lower_key_dict:
        raise xlexc.NoDataExtractedFromExcel        
    for xl_dict in xlreceiver.lower_key_dict:
        try:
            if xl_dict.get('doctype'): doctype_name = xl_dict.get('doctype')                      
            if xl_dict.get('action').lower().strip() == "create":
                wf = Workflow(doctype_name, wfc=wfc)
                status_msg_dict = wf.create_doc(xl_dict )
                response_list.append(status_msg_dict)                   
        except (xlexc.FlexFlowException, rexc.FlexFlowException) as e:
            #print(str(e))
            msg = e.ret_val
            response_list.append(msg)
            continue
        except Exception as e:
            msg = {"status": "Failed", "message": str(e)}
            response_list.append(msg)
            continue
#     logger.debug('got response list after calling the  the'
#                 ' workflow create_doc', status_msg_dict) 
    kafka_producer.notify_kafka(confobj, wfc, response_list)
    return response_list



def update_all_from_drafts(confobj, wfc, wf, wfdocs:list, intended_action):
    result_list =[]
    for uniquename in wfdocs:
        try:
            msg = wf.action_from_draft(uniquename, intended_action)
            result_list.append(msg)               
        except (rexc.FlexFlowException) as e:
            msg = e.ret_val
            result_list.append(msg)
            continue
        except Exception as e:
            msg = {"status": "Failed", "message": str(e)}
            result_list.append(msg)
            continue
    kafka_producer.notify_kafka(confobj, wfc, result_list)
    return result_list