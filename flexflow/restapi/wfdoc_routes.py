import json
from flask import Blueprint, request, jsonify
from flexflow.domains import repos
from flexflow.configs.prodconf import flexflow_configs
from flexflow.domains.xloder.uploader import XLReceiver
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
    except (xlexc.InvalidDocCategory, xlexc.NoDataExtractedFromExcel,
            xlexc.MissingExcelConfig, rexc.RoleNotPermittedForThisAction,
            rexc.UnknownFieldNameInDataDoc, rexc.DataTypeViolation,
            rexc.DataLengthViolation, rexc.NoActionRuleForCreate) as e:
        msg = e.ret_val
    except Exception as e:
        msg = {"status": "Failed", "message": str(e)}
    return jsonify(msg)

