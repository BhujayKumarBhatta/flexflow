import json
from flask import Blueprint, request, jsonify
from flexflow.domains import repos
from flexflow.configs.prodconf import flexflow_configs
from flexflow.domains.domainlogics.xloder.uploader import XLReceiver
from flexflow.domains.domainlogics.xloder import xluploader_exceptions  as xlexc
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
    except (xlexc.InvalidDocCategory, xlexc.NoDataExtractedFromExcel) as e:
        msg = e.ret_val
    except Exception as e:
        msg = {"status": "Failed", "message": str(e)}
    return jsonify(msg)
