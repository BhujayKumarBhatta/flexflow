from flexflow.domains.domainlogics.workflow import Workflow
from flexflow.domains.xloder import xluploader_exceptions  as xlexc
from flexflow.exceptions import rules_exceptions  as rexc

def update_all_from_drafts(wf, wfdocs:list, intended_action):
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
    return result_list