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
            wf = Workflow(doctype_name, wfc=wfc)                      
            if xl_dict.get('action').lower().strip() == "create":
                status_msg_dict = wf.create_doc(xl_dict )
            else:
                wfdoc_name = xl_dict.get('invoiceno')
                intended_action = xl_dict.get('action')
                #strip-off non editable fields since xl will come with all fields
                status_msg_dict = wf.action_change_status(wfdoc_name, intended_action, xl_dict, strip_off=True)
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


def create_document(confObj, wfc, doctype, request):
    try:           
        doc_data = request.json
        #print('data posted.................',doc_data)
        wf = Workflow(doctype, wfc=wfc)
        msg = wf.create_doc(doc_data)
    except (rexc.FlexFlowException) as e:
        msg = e.ret_val
    except Exception as e:
        msg = {"status": "Failed", "message": str(e)}
    kafka_producer.notify_kafka(confObj, wfc, [msg])
    return msg


def update_document(confObj, wfc, doctype, request):
    try:
        wfdoc_name = request.json.get('wfdoc_name')
        intended_action = request.json.get('intended_action')
        doc_data = request.json.get('doc_data')
        wf = Workflow('Wfdoc', wfc=wfc)# TODO: doctype param shoikd be passed here. 'Wfdoc' was passed  worongly here , howere we were saved since the change is not dependent on the Doctyoe
        msg = wf.action_change_status(wfdoc_name, intended_action, doc_data)
    except (rexc.FlexFlowException) as e:
        msg = e.ret_val
    except Exception as e:
        msg = {"status": "Failed", "message": str(e)}
    kafka_producer.notify_kafka(confObj, wfc, [msg])
    return msg



        
        
    