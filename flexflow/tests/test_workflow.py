import json
import uuid
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
        m.dbdriver.delete(m.Draftdata)
        m.dbdriver.delete(m.Holddoc)
        m.dbdriver.delete(m.Wfdocaudit)
        m.dbdriver.delete(m.Wfdoc) 
        m.dbdriver.delete(m.Wfaction)
        m.dbdriver.delete(m.Wfstatus)
        m.dbdriver.delete(m.Datadocfield)
        m.dbdriver.delete(m.Doctype)
        self._register_doctype_n_actions()
        testconf.testwfc.roles= ['r1']        
        wf = Workflow('doctype2', wfc=testconf.testwfc)        
        ##create should fail  when primary key fields in datadoc is not in rule
        try:
            msg = wf.create_doc({"dk1": "dv1", "dk2-nonprim": "dv22", })
        except Exception as e:
            self.assertTrue(e.status == "PrimaryKeyNotPresentInDataDict")
        ##Converts data type  when  fields dk1 is not string
        #wf.create_doc({"dk1": 100, "dk2": "dv2222", })
        ##Fail  when  fields dk3 is not present in the rule at all        
        try:
            msg = wf.create_doc({"dk3": "not defined in the rule", 
                                 "dk2": "dv22", "dk1": 100, 
                                 "tsp": "tata",
                                 "division": "divison1"})
        except Exception as e:
            self.assertTrue(e.status == "UnknownFieldNameInDataDoc")
        ### WORKFLOW IS ABLE TO CREATE DOC
        testconf.testwfc.roles= ['r1']
        testconf.testwfc.org= 'org1' 
        msg = wf.create_doc({"dk1": "dv1", "dk2": "dv22", 
                             "tsp": "org1",
                             "division": "divison1"})
        self.assertTrue(msg['message'] == "has been registered" )
        ####ABLE TO RETRIEVE THE BY THE PRIMKEY AS DEFINED IN THE DOCTYPE
        doc_repo = DomainRepo("Wfdoc")
        wfdocObj_list = doc_repo.list_domain_obj(name="dv22")
        self.assertTrue(wfdocObj_list[0].name == "dv22")          
        ####UPDATE DOC STATUS AS PER THE ACTION RULE, 
        testconf.testwfc.request_id = str(uuid.uuid4())
        wf = Workflow('doctype2', wfc=testconf.testwfc)
        msg = wf.action_change_status("dv22", "wfaction1", {"dk1": "changed_data_on_action1"})
        ### check that self._validate_editable_fields(wfdocObj, data) working
        self.assertTrue(msg['status'] =="success")
        ###wdoc should be able to understand that dk2 is editable and dk1 is not
        self.assertTrue("dk2" not in [f.name for f in wfdocObj_list[0].editable_fields_at_current_status])
        self.assertTrue("dk1" in [f.name for f in wfdocObj_list[0].editable_fields_at_current_status])
        ###USE ROLE "hide_to_roles": ["r4", "r5"] to see that data is showing from holddoc
        #data still should show previous data {"dk1": "dv1", "dk2": "dv22", }
        testconf.testwfc.roles= ['r4']
        testconf.testwfc.request_id = str(uuid.uuid4())
        wf = Workflow('doctype2', wfc=testconf.testwfc)
        result = wf.list_wfdoc()
        self.assertTrue(result[0].get('doc_data').get('dk1') == 'dv1') # data is showing from holddoc for role r4
        ####same for r5 
        testconf.testwfc.roles= ['r5']
        testconf.testwfc.request_id = str(uuid.uuid4())
        wf = Workflow('doctype2', wfc=testconf.testwfc)
        result = wf.list_wfdoc()
        self.assertTrue(result[0].get('doc_data').get('dk1') == 'dv1')
        #########FOR R6 AND R1 THE UPDATED DATA IS VISIBLE 
        testconf.testwfc.roles= ['r1', 'r6']
        testconf.testwfc.request_id = str(uuid.uuid4())
        wf = Workflow('doctype2', wfc=testconf.testwfc)
        result = wf.list_wfdoc()
        self.assertTrue(result[0].get('doc_data').get('dk1') == 'changed_data_on_action1')
        ####SHOULD FAIL FOR INCORRECT ROLE
        testconf.testwfc.roles= ['r1']
        testconf.testwfc.request_id = str(uuid.uuid4())
        wf = Workflow('doctype2', wfc=testconf.testwfc)        
        try:
            msg = wf.action_change_status("dv22", "wfaction2")
        except rexc.RoleNotPermittedForThisAction as err:
            self.assertTrue(err.status == "RoleNotPermittedForThisAction")
        ###SHOULD PASS THE ROLE AND THE RULE 
        testconf.testwfc.request_id = str(uuid.uuid4())
        testconf.testwfc.roles= ['r2']
        wf = Workflow('doctype2', wfc=testconf.testwfc)
        msg = wf.action_change_status("dv22", "wfaction2", {"dk1": "changed_data_on_action2"})
        self.assertTrue(msg['status'] =="success")
        ##during action1 "hide_to_roles": ["r4", "r5"], and in action2 "undo_prev_hide_for": ["r4",],
        ####should be able to see latest data
        ##########hold for R4 has now been removed
        ####should be able to see latest data
        testconf.testwfc.roles= ['r4']
        testconf.testwfc.request_id = str(uuid.uuid4())
        wf = Workflow('doctype2', wfc=testconf.testwfc)
        result = wf.list_wfdoc()
        self.assertTrue(result[0].get('doc_data').get('dk1') == 'changed_data_on_action2') 
        ##########hold for R5 stil remains        
        testconf.testwfc.roles= ['r5']
        testconf.testwfc.request_id = str(uuid.uuid4())
        wf = Workflow('doctype2', wfc=testconf.testwfc)
        result = wf.list_wfdoc()
        self.assertTrue(result[0].get('doc_data').get('dk1') == 'dv1')# data remained what it was before action1 which is the data at create stage
        ####HAVE A TEST FOR RULE STATUS VALIDATION FAILURE
        testconf.testwfc.request_id = str(uuid.uuid4())
        testconf.testwfc.roles= ['r1']
        wf = Workflow('doctype2', wfc=testconf.testwfc)
        try:
            msg = wf.action_change_status("dv22", "wfaction1")
        except rexc.WorkflowActionRuleViolation as err:
            self.assertTrue(err.status == "WorkflowActionRuleViolation")
        ####WFDOC SHOULD HAVE actions_for_current_stattus
        actions_for_current_status = [a.name for a in wfdocObj_list[0].actions_for_current_status]
        self.assertTrue(actions_for_current_status == ['wfaction1'])
        ###fail due to data having non editable field dk1
        ###develop logic to check if the data has actually changed
        testconf.testwfc.request_id = str(uuid.uuid4())
        testconf.testwfc.roles= ['r3']
        wf = Workflow('doctype2', wfc=testconf.testwfc)
        try:
            wf.action_change_status("dv22", "wfaction3", {"dk1": "dv1", "dk2": "dv22"})
        except Exception as e:
            self.assertTrue(e.status == "EditNotAllowedForThisField")
        ###get full wfdoc dict including current action list and editable field list
        msg = wf.get_full_wfdoc_as_dict('dv22')
        self.assertTrue('dk1' in msg.get('current_edit_fields'))
        self.assertTrue('wfaction3' in msg.get('current_actions'))
        ###WITH R5 ROLE SEE HOLDDOC IS CREATED
#         testconf.testwfc.request_id = str(uuid.uuid4())
#         testconf.testwfc.roles= ['r3']
#         wf = Workflow('doctype2', wfc=testconf.testwfc)
        ##############################################################
        ############document was created as tsp="org1", division="division1"
        ###field to wfc mapping was tsp field maps to  org for role r1 
        ###and divison maps to ou for role r3 
        testconf.testwfc.org = "org2"
        testconf.testwfc.orgunit = "divison1"
        testconf.testwfc.roles= ['r3']
        testconf.testwfc.request_id = str(uuid.uuid4())
        wf = Workflow('doctype2', wfc=testconf.testwfc)
        result = wf.list_wfdoc()
        self.assertTrue(result[0].get('doc_data').get('division') == 'divison1')
        ####division1 cant see when the  doc is created for  divison2 
        testconf.testwfc.roles= ['r1']
        testconf.testwfc.org= 'org1' 
        msg = wf.create_doc({"dk1": "dv1", "dk2": "dkdiv2", 
                             "tsp": "org1",
                             "division": "divison2"})
        testconf.testwfc.org = "org2"
        testconf.testwfc.orgunit = "divison1"
        testconf.testwfc.roles= ['r3']
        testconf.testwfc.request_id = str(uuid.uuid4())
        wf = Workflow('doctype2', wfc=testconf.testwfc)
        result = wf.list_wfdoc()
        self.assertTrue(not len(result) == 2)
        ###TSPorg2 cant see doc created by tsp=org1
        testconf.testwfc.roles= ['r1']
        testconf.testwfc.org= 'tsporg2'
        wf = Workflow('doctype2', wfc=testconf.testwfc)
        result = wf.list_wfdoc()
        self.assertTrue(not result)
        ###AT THIS STAGE ACTION 3 IS PERMITTED TO ROLE3
        ###Role3 should be able to put some data in save as draft
        testconf.testwfc.org = "org2"
        testconf.testwfc.orgunit = "divison1"
        testconf.testwfc.roles= ['r3']
        testconf.testwfc.request_id = str(uuid.uuid4())
        wf = Workflow('doctype2', wfc=testconf.testwfc)
        draft_data = {"dk1": "want_to_save_as_draft"}
        result = wf.save_as_draft("dv22", draft_data)
        self.assertTrue(result.get('draft_create_msg').get('status') == "success")
        self.assertTrue(result.get('wfdoc_update_msg').get('status') == "success")
        ##get draft data for  same role 
        result = wf.get_draft_data_for_role('dv22')
        self.assertTrue(result.get('dk1') == 'want_to_save_as_draft')
        ##other are not seeing the draft doc even when queried
        testconf.testwfc.roles= ['r2']
        testconf.testwfc.request_id = str(uuid.uuid4())
        wf = Workflow('doctype2', wfc=testconf.testwfc)
        result = wf.get_draft_data_for_role('dv22')
        self.assertTrue(not result)
        #list draft doc
        result = wf.list_wfdocs_superimposed_by_draft()
        self.assertTrue(result[0].get('doc_data').get('dk1') == "want_to_save_as_draft")
        ##update or action  from draft
        testconf.testwfc.roles= ['r3']
        testconf.testwfc.request_id = str(uuid.uuid4())
        wf = Workflow('doctype2', wfc=testconf.testwfc)
        result = wf.action_from_draft('dv22', "wfaction3")
        self.assertTrue("want_to_save_as_draft" in result.get('message'))
        
        
    def _register_doctype_n_actions(self):
        doctype1 = ent.Doctype("doctype1", "dk1", ['role1'])
        doctype2 = ent.Doctype("doctype2", "dk2", ['role1'])
        lodobj = [doctype1, doctype2]
        doctype_repo = DomainRepo("Doctype")
        doctype_repo.add_list_of_domain_obj(lodobj)
        ####DEFINING FIELDS FOR DOCTYPE2
        f1_dict = {"name": "dk1",
                   "associated_doctype": {"name": "doctype2"},
                   "ftype": "str",
                   "flength": 25,
                   "status_needed_edit": ["s1", "Created", "s2"],#this should be status not role
                   "wfc_filter": "",
                   "wfc_filter_to_roles": []} 
        f2_dict = {"name": "dk2",
                   "associated_doctype": {"name": "doctype2"},
                   "ftype": "str",
                   "flength": 10,
                   "status_needed_edit": [""],
                   "wfc_filter": "",
                   "wfc_filter_to_roles": []}
        f3_dict = {"name": "tsp",
                   "associated_doctype": {"name": "doctype2"},
                   "ftype": "str",
                   "flength": 10,
                   "status_needed_edit": [""],
                   "wfc_filter": "org",
                   "wfc_filter_to_roles": ['r1']}
        f4_dict = {"name": "division",
                   "associated_doctype": {"name": "doctype2"},
                   "ftype": "str",
                   "flength": 10,
                   "status_needed_edit": [""],
                   "wfc_filter": "ou",
                   "wfc_filter_to_roles": ['r3']}
        docf_repo = repos.DomainRepo("Datadocfield")
        docf_repo.add_form_lod([f1_dict, f2_dict, f3_dict, f4_dict])
        wfcaction_create = {"name": "Create",
                         "associated_doctype": {"name": "doctype2"},
                         #"need_prev_status": "NewBorn",
                         "need_current_status": ["NewBorn"],
                         "leads_to_status": "Created",
                         "permitted_to_roles": ["r1",],
                         "hide_to_roles": ["r7"],
                         "undo_prev_hide_for": [],
                         }
        wfaction1_dict=  {"name": "wfaction1",
                         "associated_doctype": {"name": "doctype2"},
                         #"need_prev_status": "NewBorn",
                         "need_current_status": ["Created"],
                         "leads_to_status": "s1",
                         "permitted_to_roles": ["r1",], 
                         "hide_to_roles": ["r4", "r5"],
                         "undo_prev_hide_for": [],
                         }
        wfaction2_dict=  {"name": "wfaction2",
                         "associated_doctype": {"name": "doctype2"},
                         #"need_prev_status": "Created",
                         "need_current_status": ["s1"],
                         "leads_to_status": "s2",
                         "permitted_to_roles": ["r2",],
                         "hide_to_roles": ["r5", "r6"],
                         "undo_prev_hide_for": ["r4",], #r4 hold doc shold be deleted but r5 to be retained
                         }
        wfaction3_dict=  {"name": "wfaction3",
                         "associated_doctype": {"name": "doctype2"},
                         #"need_prev_status": "s1",
                         "need_current_status": ["s2"],
                         "leads_to_status": "s3",
                         "permitted_to_roles": ["r3",],
                         "hide_to_roles": ["r1",],
                         "undo_prev_hide_for": ["r5", "r6"],
                         }
        wfaction4_dict=  {"name": "wfaction4",
                         "associated_doctype": {"name": "doctype2"},
                         #"need_prev_status": "s2",
                         "need_current_status": ["s3"],
                         "leads_to_status": "s4",
                         "permitted_to_roles": ["r3",],
                         "hide_to_roles": ["r5",],
                         "undo_prev_hide_for": [],
                         }
        wfactionCreate = ent.Wfaction.from_dict(wfcaction_create)
        wfaction1 = ent.Wfaction.from_dict(wfaction1_dict)
        wfaction2 = ent.Wfaction.from_dict(wfaction2_dict)
        wfaction3 = ent.Wfaction.from_dict(wfaction3_dict)
        lodobj = [wfactionCreate, wfaction1, wfaction2, wfaction3]
        action_repo = DomainRepo("Wfaction")
        action_repo.add_list_of_domain_obj(lodobj)
    
    