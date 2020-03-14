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

auth_config = Configs()
tlclient = Client(auth_config)
enforcer = Enforcer(tlclient)
wf_doc_bp = Blueprint('wf_doc_bp', __name__)


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

@wf_doc_bp.route('/wfdoc/create/<doctype>', methods=['POST'])
@enforcer.enforce_access_rule_with_token('xluploader.upload_excel') 
def wfdoc_create(doctype, wfc):
    try:           
        doc_data = request.json
        #print('data posted.................',doc_data)
        wf = Workflow(doctype, wfc=wfc)
        msg = wf.create_doc(doc_data)
    except (rexc.FlexFlowException) as e:
        msg = e.ret_val
    except Exception as e:
        msg = {"status": "Failed", "message": str(e)}
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
        xlreceiver = XLReceiver(flexflow_configs, wfc, request=request)
        msg = xlreceiver.action_from_lod(wfc.roles, doctype)
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
def wfdoc_update(wfc):
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





#     except (xlexc.InvalidDocCategory, xlexc.NoDataExtractedFromExcel,
#             xlexc.MissingExcelConfig, rexc.RoleNotPermittedForThisAction,
#             rexc.UnknownFieldNameInDataDoc, rexc.DataTypeViolation,
#             rexc.DataLengthViolation, rexc.NoActionRuleForCreate) as e:

