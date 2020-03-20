import json
from flask import Blueprint, request, jsonify
from flexflow.domains import repos
from flexflow.configs.prodconf import flexflow_configs
from flexflow.domains.xloder.uploader import XLReceiver
from flexflow.domains.domainlogics.workflow import Workflow
from flexflow.domains.xloder import xluploader_exceptions  as xlexc
from flexflow.exceptions import rules_exceptions  as rexc
from tokenleaderclient.configs.config_handler import Configs    
from tokenleaderclient.client.client import Client 
from tokenleaderclient.rbac.enforcer import Enforcer


from flexflow.domains.domainlogics import workers

auth_config = Configs()
tlclient = Client(auth_config)
enforcer = Enforcer(tlclient)
wf_doc_bp = Blueprint('wf_doc_bp', __name__)




@wf_doc_bp.route('/wfdoc/create/<doctype>', methods=['POST'])
@enforcer.enforce_access_rule_with_token('xluploader.upload_excel') 
def wfdoc_create(doctype, wfc):
    msg = workers.create_document(flexflow_configs, wfc, doctype, request)
    return jsonify(msg)


@wf_doc_bp.route('/wfdoc/listbydoctype/<doctype>', methods=['GET'])
@enforcer.enforce_access_rule_with_token('paperhouse.list_all') 
def list_wfdoc_by_doctype(doctype, wfc):
    try:
        wf = Workflow(doctype, wfc=wfc)
        msg = wf.list_wfdoc()
    except (rexc.FlexFlowException) as e:
        msg = e.ret_val
    except Exception as e:
        msg = {"status": "Failed", "message": str(e)}
    return jsonify(msg)


@wf_doc_bp.route('/wfdoc/uploadxl/<doctype>', methods=['POST'])
@enforcer.enforce_access_rule_with_token('xluploader.upload_excel') 
def upload_excel(doctype, wfc):
    try:
        msg = workers.xl_upload(flexflow_configs, wfc, doctype, request=request )
        #xlreceiver = XLReceiver(flexflow_configs, wfc, request=request)
        #msg = xlreceiver.action_from_lod(wfc.roles, doctype)
    except (xlexc.FlexFlowException, rexc.FlexFlowException) as e:
        msg = e.ret_val
    except Exception as e:
        msg = {"status": "Failed", "message": str(e)}
    return jsonify(msg)


@wf_doc_bp.route('/wfdoc/get_fulldetail/<uniquename>', methods=['GET'])
@enforcer.enforce_access_rule_with_token('paperhouse.list_all') 
def wfdoc_fulldetial(uniquename, wfc):
    try:
        wf = Workflow('Wfdoc', wfc=wfc)
        msg = wf.get_full_wfdoc_as_dict(uniquename, )
    except (rexc.FlexFlowException) as e:
        msg = e.ret_val
    except Exception as e:
        msg = {"status": "Failed", "message": str(e)}
    return jsonify(msg)


@wf_doc_bp.route('/wfdoc/update', methods=['POST'])#TODO:we should have doctype as parameter here
@enforcer.enforce_access_rule_with_token('paperhouse.list_all') 
def wfdoc_update(wfc): # TODO: doctype param shoikd be passed
    doctype = 'tspinvoice'
    msg = workers.update_document(flexflow_configs, wfc, doctype, request)
    return jsonify(msg)

@wf_doc_bp.route('/wfdoc/saveasdraft/<doctype>/<wfdoc_name>', methods=['POST'])
@enforcer.enforce_access_rule_with_token('paperhouse.list_all') 
def wfdoc_saveasdraft(doctype, wfdoc_name, wfc):
    try:
        if "draft_data" not in request.json.keys():
            raise rexc.InvalidInputdata
        draft_data = request.json.get('draft_data')
        wf = Workflow(doctype, wfc=wfc)
        msg = wf.save_as_draft(wfdoc_name, draft_data)
    except (rexc.FlexFlowException) as e:
        msg = e.ret_val
    except Exception as e:
        msg = {"status": "Failed", "message": str(e)}
    return jsonify(msg)


@wf_doc_bp.route('/wfdoc/listdraft/<doctype>', methods=['GET'])
@enforcer.enforce_access_rule_with_token('paperhouse.list_all') 
def list_draft(doctype, wfc):
    try:
        wf = Workflow(doctype, wfc=wfc)
        msg = wf.list_wfdocs_superimposed_by_draft()
    except (rexc.FlexFlowException) as e:
        msg = e.ret_val
    except Exception as e:
        msg = {"status": "Failed", "message": str(e)}
    return jsonify(msg)


@wf_doc_bp.route('/wfdoc/draft/get_fulldetail/<uniquename>/<replace_orig_data>', methods=['GET'])
@enforcer.enforce_access_rule_with_token('paperhouse.list_all') 
def wfdocdraft_fulldetial(uniquename, replace_orig_data, wfc):
    try:
        wf = Workflow('Wfdoc', wfc=wfc)
        msg = wf.get_full_doc_with_draft_data(uniquename, replace_orig_data )
    except (rexc.FlexFlowException) as e:
        msg = e.ret_val
    except Exception as e:
        msg = {"status": "Failed", "message": str(e)}
    return jsonify(msg)


@wf_doc_bp.route('/wfdoc/action_fm_draft/<uniquename>/<intended_action>', methods=['POST'])
@enforcer.enforce_access_rule_with_token('paperhouse.list_all') 
def action_fm_draft(uniquename, intended_action, wfc):
    try:
        addl_input = request.json.get('addl_input')
        wf = Workflow('Wfdoc', wfc=wfc)
        msg = wf.action_from_draft(uniquename, intended_action, addl_input)
    except (rexc.FlexFlowException) as e:
        msg = e.ret_val
    except Exception as e:
        msg = {"status": "Failed", "message": str(e)}
    return jsonify(msg)


@wf_doc_bp.route('/wfdoc/update_all_from_drafts', methods=['POST'])
@enforcer.enforce_access_rule_with_token('paperhouse.list_all') 
def update_all_from_drafts(wfc):
    print('request.json',request.json)    
    try:
        wf = Workflow('Wfdoc', wfc=wfc)
        if "wfdocs" not in request.json.keys() and \
            "intended_action" not in request.json.keys():
            raise rexc.InvalidInputdata
        wfdocs = request.json.get('wfdocs')
        intended_action = request.json.get('intended_action')        
        result_list = workers.update_all_from_drafts(flexflow_configs, wfc, wf, wfdocs, intended_action)
        print('update_all_from_draft', result_list)
    except (rexc.FlexFlowException) as e:
        msg = e.ret_val
        result_list.append(msg)
    except Exception as e:
        msg = {"status": "Failed", "message": str(e)}
        result_list.append(msg)
    return jsonify(result_list)        
    
            
@wf_doc_bp.route('/wfdoctype/get_fulldetail/<doctype>', methods=['GET'])
@enforcer.enforce_access_rule_with_token('paperhouse.list_all') 
def wfdoctype_fulldetial(doctype, wfc):
    try:
        wf = Workflow(doctype, wfc=wfc)
        msg = wf.get_full_wfdoctype_as_dict()
    except (rexc.FlexFlowException) as e:
        msg = e.ret_val
    except Exception as e:
        msg = {"status": "Failed", "message": str(e)}
    return jsonify(msg)    
        
            
        
    

