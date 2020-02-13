import json
from flask import Blueprint, request
from flexflow.domains import repos
from flexflow.exceptions import rules_exceptions  as rexc

bp1 = Blueprint('bp1',__name__)


@bp1.route('/wfmaster/add/<objname>', methods=['POST'])
def wfmaster_add(objname):
    try:
        repo = repos.DomainRepo(objname)
        result = repo.add_form_lod(request.json)
    except (rexc.InvalidWorkflowObject, rexc.InvalidInputDataList,
            rexc.InvalidInputDataDict, rexc.InvalidKeysInData) as errObj:
        result = errObj.__repr__()
    except Exception as err:
            result = {'status': "unknown", 'msg': str(err)}
    return json.dumps(result)
    
    