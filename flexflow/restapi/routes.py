import json
from flask import Blueprint
from flexflow.domains import repos
from flexflow.exceptions import rules_exceptions  as rexc

bp1 = Blueprint('bp1',__name__)


@bp1.route('/wfmaster/add/<objname>', methods=['POST'])
def wfmaster_add(objname):
    try:
        repo = repos.DomainRepo(objname)
        repo.add_form_lod(status_lod)
    except (rexc.InvalidWorkflowObject, rexc.InvalidKeysInData) as err:
        result = err
    except Exception as err:
            result = {'status': "error", 'msg': str(err)}
    return json.dumps(result)
    
    