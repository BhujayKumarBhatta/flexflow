import json
from flask import Blueprint, request
from flexflow.domains import repos
from flexflow.exceptions import rules_exceptions  as rexc

bp1 = Blueprint('bp1', __name__)


@bp1.route('/add/<objname>', methods=['POST'])
def wfmaster_add(objname):
    try:
        repo = repos.DomainRepo(objname)
        result = repo.add_form_lod(request.json)
    except (rexc.InvalidWorkflowObject, rexc.InvalidInputDataList,
            rexc.InvalidInputDataDict, rexc.InvalidKeysInData) as errObj:
        result = errObj.ret_val
    except Exception as err:
            result = {'status': "unknown", 'msg': str(err)}
    return json.dumps(result)


@bp1.route('/list/<objname>/<searchkey>/<searchvalue>', methods=['GET'])
def wfmaster_list_single_searchkey(objname, searchkey, searchvalue):
    '''
    GET method to use for listing all  or filter by a single key
    POST method is used to capture the filters''' 
    try:
        repo = repos.DomainRepo(objname)
        if searchkey == 'all' and searchvalue == 'all':
            result = repo.list_json()
        else:
            filter = {searchkey: searchvalue}
            result = repo.list_json(**filter)#convert dict as name=value with **
    except (rexc.InvalidWorkflowObject, rexc.InvalidInputDataDict,
            rexc.InvalidKeysInData) as errObj:
        result = errObj.ret_val
    except Exception as err:
            result = {'status': "unknown", 'msg': str(err)}
    return result


@bp1.route('/list/<objname>', methods=['POST'])
def wfmaster_list_multiple_searchkey(objname):
    '''
    GET method to use for listing all  or filter by a single key
    POST method is used to capture the filters''' 
    try:
        repo = repos.DomainRepo(objname)
        result = repo.list_json(**request.json) #convert dict as name=value with **        
    except (rexc.InvalidWorkflowObject, rexc.InvalidInputDataDict,
            rexc.InvalidKeysInData) as errObj:
        result = errObj.ret_val
    except Exception as err:
            result = {'status': "unknown", 'msg': str(err)}
    return result
  
    
@bp1.route('/update/<objname>', methods=['PUT']) #PUT is to replace the entire resourcce, whereas patch is partial update
def wfmaster_update(objname):
    try:
        repo = repos.DomainRepo(objname)
        result = repo.update_from_dict(request.json.get('update_data_dict'),
                                       **request.json.get('search_filter'))
    except (rexc.InvalidWorkflowObject, rexc.InvalidInputDataDict,
            rexc.InvalidKeysInData) as errObj:
        result = errObj.ret_val
    except Exception as err:
            result = {'status': "unknown", 'msg': str(err)}
    return json.dumps(result)


@bp1.route('/delete/<objname>', methods=['POST'])
def wfmaster_delete(objname):
    print("request.json in delete", request.json)
    try:
        repo = repos.DomainRepo(objname)        
        result = repo.delete(**request.json)#convert dict as name=value with **
    except (rexc.InvalidWorkflowObject, rexc.InvalidInputDataDict,
            rexc.InvalidKeysInData) as errObj:
        result = errObj.ret_val
    except Exception as err:
            result = {'status': "unknown", 'msg': str(err)}
    return json.dumps(result)
