import json
from flexflow.configs import testconf
from flask_testing import TestCase as FTestCase
import flexflow
from flexflow.dbengines.sqlchemy import models as m, SqlalchemyDriver
from sqlalchemy import exc
from flexflow.domains import repos
from flexflow.restapi.routes import bp1
from flexflow.domains.repos import DomainRepo
from flexflow.domains.entities import entities as ent
from flexflow.domains.domainlogics.workflow import Workflow
from flexflow.exceptions import rules_exceptions  as rexc


        
app = flexflow.create_app(config_map_list = [testconf.yml, testconf.test_db_conf],
                          blue_print_list = [bp1,])
        
class Tflask(FTestCase):
    
    def create_app(self):       
#         app.config.from_object('app1.configs.testconfigs.TestConfig')
        app.config['TESTING'] = True
        app.config['LIVESERVER_PORT'] = 0
        return app
    
      
    def test_workflow(self):
        m.dbdriver.delete(m.Wfdoc) 
        m.dbdriver.delete(m.Wfaction)
        m.dbdriver.delete(m.Wfstatus)
        m.dbdriver.delete(m.Datadocfield)
        m.dbdriver.delete(m.Doctype)
        self._register_doctype_n_actions()
        wf = Workflow('doctype2', 'r1')    
        
        ##create should fail  when primary key fields in datadoc is not in rule
        try:
            wf.create_doc({"dk1": "dv1", "dk2-nonprim": "dv2", }, ['r1'])
        except Exception as e:
            self.assertTrue(e.status == "PrimaryKeyNotPresentInDataDict")
        ##Fail  when  fields dk1 is not string        
        try:
            wf.create_doc({"dk1": 100, "dk2": "dv2", }, ['r1'])
        except Exception as e:
            self.assertTrue(e.status == "DataTypeViolation")
        ##Fail  when  fields dk3 is not present in the rule at all        
        try:
            wf.create_doc({"dk3": "not defined in the rule", "dk2": "dv2", }, ['r1'])
        except Exception as e:
            self.assertTrue(e.status == "UnknownFieldNameInDataDoc")
        ### WORKFLOW IS ABLE TO CREATE DOC
        msg = wf.create_doc({"dk1": "dv1", "dk2": "dv2", }, ['r1'])
        self.assertTrue(msg['message'] == "has been registered" )
        ####ABLE TO RETRIEVE THE BY THE PRIMKEY AS DEFINED IN THE DOCTYPE
        doc_repo = DomainRepo("Wfdoc")
        wfdocObj_list = doc_repo.list_domain_obj(name="dv2")
        self.assertTrue(wfdocObj_list[0].name == "dv2")          
        ####UPDATE DOC STATUS AS PER THE ACTION RULE
        msg = wf.action_change_status("dv2", "wfaction1", {"dk2": "dv2"})
        ### check that self._validate_editable_fields(wfdocObj, data) working
        self.assertTrue(msg['status'] =="success")
        ###wdoc should be able to understand that dk2 is editable and dk1 is not
        self.assertTrue("dk2" in wfdocObj_list[0].editable_fields_at_current_status)
        self.assertTrue("dk1" not in wfdocObj_list[0].editable_fields_at_current_status)
        ####SHOULD FAIL FOR INCORRECT ROLE
        wf = Workflow('doctype2', 'r1')
        try:
            msg = wf.action_change_status("dv2", "wfaction2")
        except rexc.RoleNotPermittedForThisAction as err:
            self.assertTrue(err.status == "RoleNotPermittedForThisAction")
        ###SHOULD PASS THE ROLE AND THE RULE 
        wf = Workflow('doctype2', 'r2')
        msg = wf.action_change_status("dv2", "wfaction2")
        self.assertTrue(msg['status'] =="success")
        ####HAVE A TEST FOR RULE STATUS VALIDATION FAILURE
        try:
            msg = wf.action_change_status("dv2", "wfaction1")
        except rexc.WorkflowActionRuleViolation as err:
            self.assertTrue(err.status == "WorkflowActionRuleViolation")
        ####WFDOC SHOULD HAVE actions_for_current_stattus
        actions_for_current_status = wfdocObj_list[0].actions_for_current_status
        self.assertTrue(actions_for_current_status == ['wfaction1'])
        ###fail due to data having non editable field dk1
        ###develop logic to check if the data has actually changed
        wf = Workflow('doctype2', 'r3') 
        try:
            wf.action_change_status("dv2", "wfaction3", {"dk1": "dv1", "dk2": "dv2"})
        except Exception as e:
            self.assertTrue(e.status == "EditNotAllowedForThisField")
        ###get full wfdoc dict including current action list and editable field list
        msg = wf.get_full_wfdoc_as_dict('dv2')
        self.assertTrue('dk2' in msg.get('current_edit_fields'))
        self.assertTrue('wfaction3' in msg.get('current_actions'))
      
    def _register_doctype_n_actions(self):
        doctype1 = ent.Doctype("doctype1", "dk1")
        doctype2 = ent.Doctype("doctype2", "dk2")
        lodobj = [doctype1, doctype2]
        doctype_repo = DomainRepo("Doctype")
        doctype_repo.add_list_of_domain_obj(lodobj)
        ####DEFINING FIELDS FOR DOCTYPE2
        f1_dict = {"name": "dk1",
                   "associated_doctype": {"name": "doctype2"},
                   "ftype": "str",
                   "flength": 10,
                   "status_needed_edit": [""]} #this should be status not role
        f2_dict = {"name": "dk2",
                   "associated_doctype": {"name": "doctype2"},
                   "ftype": "str",
                   "flength": 10,
                   "status_needed_edit": ["s1", "Created", "s2"]}
        docf_repo = repos.DomainRepo("Datadocfield")
        docf_repo.add_form_lod([f1_dict, f2_dict])
        wfcaction_create = {"name": "Create",
                         "associated_doctype": {"name": "doctype2"},
                         "need_prev_status": "NewBorn",
                         "need_current_status": "NewBorn",
                         "leads_to_status": "Created",
                         "permitted_to_roles": ["r1",]
                         }
        wfaction1_dict=  {"name": "wfaction1",
                         "associated_doctype": {"name": "doctype2"},
                         "need_prev_status": "",
                         "need_current_status": "Created",
                         "leads_to_status": "s1",
                         "permitted_to_roles": ["r1",]
                         }
        wfaction2_dict=  {"name": "wfaction2",
                         "associated_doctype": {"name": "doctype2"},
                         "need_prev_status": "Created",
                         "need_current_status": "s1",
                         "leads_to_status": "s2",
                         "permitted_to_roles": ["r2",]
                         }
        wfaction3_dict=  {"name": "wfaction3",
                         "associated_doctype": {"name": "doctype2"},
                         "need_prev_status": "s1",
                         "need_current_status": "s2",
                         "leads_to_status": "s3",
                         "permitted_to_roles": ["r3",]
                         }
        wfactionCreate = ent.Wfaction.from_dict(wfcaction_create)
        wfaction1 = ent.Wfaction.from_dict(wfaction1_dict)
        wfaction2 = ent.Wfaction.from_dict(wfaction2_dict)
        wfaction3 = ent.Wfaction.from_dict(wfaction3_dict)
        lodobj = [wfactionCreate, wfaction1, wfaction2, wfaction3]
        action_repo = DomainRepo("Wfaction")
        action_repo.add_list_of_domain_obj(lodobj)
    
    