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
@enforcer.enforce_access_rule_with_token('xluploader.upload_excel') 
def wfdoc_fulldetial(uniquename, wfc):
    try:
        wf = Workflow('Wfdoc')
        msg = wf.get_full_wfdoc_as_dict(uniquename, wfc.roles)
    except (rexc.FlexFlowException) as e:
        msg = e.ret_val
    except Exception as e:
        msg = {"status": "Failed", "message": str(e)}
    return jsonify(msg)


@wf_doc_bp.route('/wfdoc/update', methods=['POST'])
@enforcer.enforce_access_rule_with_token('xluploader.upload_excel') 
def wfdoc_update(wfc):
    try:
        wfdoc_name = request.json.get('wfdoc_name')
        intended_action = request.json.get('intended_action')
        doc_data = request.json.get('doc_data')
        wf = Workflow('Wfdoc', wfc=wfc)
        msg = wf.action_change_status(wfdoc_name, intended_action, wfc.roles, doc_data)
    except (rexc.FlexFlowException) as e:
        msg = e.ret_val
    except Exception as e:
        msg = {"status": "Failed", "message": str(e)}
    return jsonify(msg)







#     except (xlexc.InvalidDocCategory, xlexc.NoDataExtractedFromExcel,
#             xlexc.MissingExcelConfig, rexc.RoleNotPermittedForThisAction,
#             rexc.UnknownFieldNameInDataDoc, rexc.DataTypeViolation,
#             rexc.DataLengthViolation, rexc.NoActionRuleForCreate) as e:

