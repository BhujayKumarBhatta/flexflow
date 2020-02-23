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
    
    def test_flask_config(self):
        #print(app.config.get('storage_drivers'))
        pass
        
    def test_models(self):
        m.dbdriver.delete(m.Wfdoc) 
        m.dbdriver.delete(m.Wfaction)
        m.dbdriver.delete(m.Wfstatus)
        m.dbdriver.delete(m.Datadocfield)
        m.dbdriver.delete(m.Doctype)                     
        docrepo = DomainRepo("Wfdoc")       
        ###########ADDING SINGLE RECORD 
        record = m.Wfstatus(name="Status1")
        msg = m.dbdriver.insert(record)
        #print(msg)           
        self.assertTrue('has been registered' in msg)
        ############UPDATING THE RECORD 
        data = {"name": "Status1111"}
        msg = m.dbdriver.update(m.Wfstatus, data, name='Status1')
        self.assertTrue(msg['status'] == "success")
        msg = m.dbdriver.list_as_dict(m.Wfstatus, name="Status1111")
        self.assertTrue(msg[0]['name'] == 'Status1111')
        #DELETE A SINGLE RECORD FILTERED BY NAME
        msg = m.dbdriver.delete(m.Wfstatus, name="Status1111")        
        self.assertTrue("has been  deleted successfully" in msg)
        #########INSERT BULK
        lod = [{"name": "status2"}, {"name": "status3"}, {"name": "status4"}]
        msg = m.dbdriver.insert_bulk(m.Wfstatus, lod)        
        msg = m.dbdriver.list_as_dict(m.Wfstatus)
        self.assertTrue(len(msg) == 3)
        ###########DELETE ALL
        msg = m.dbdriver.delete(m.Wfstatus)
        self.assertTrue("has been  deleted successfully" in msg)
        
    def test_repos(self):
        m.dbdriver.delete(m.Wfdoc) 
        m.dbdriver.delete(m.Wfaction)
        m.dbdriver.delete(m.Wfstatus)
        m.dbdriver.delete(m.Datadocfield)
        m.dbdriver.delete(m.Doctype)  
        #####INITIALIZE A REPO FOR DOMAIN ENTITY
        statrepo = repos.DomainRepo("Wfstatus")
        ##############ADD ENTITY
        status_lod = [{"name": "Status1111"}]        
        msg = statrepo.add_form_lod(status_lod)
        self.assertTrue(msg['message'] == "has been registered" )
        ##################LIST OBJECTS  FROM REPO
        msg = statrepo.list_obj(name="Status1111")
        self.assertTrue(msg[0].name == 'Status1111')
        ############LIST THE ENTITIES AS DICT 
        msg = statrepo.list_dict(name="Status1111")
        self.assertTrue(msg[0]['name'] == 'Status1111')
        ##########UPDATE THE ENTITIES 
        updated_data_dict = {"name": "Status222222"}
        searchf = {"name": "Status1111"}
        msg = statrepo.update_from_dict(updated_data_dict, **searchf)
        self.assertTrue(msg['status'] == "success")
        ##########DELETE
        msg = statrepo.delete(name='Status222222')
        self.assertTrue("deleted successfully" in  msg)
        msg=statrepo.list_obj()
        self.assertTrue(not msg)
        ##########Test LOD WHEN RELATION
        Doctype_lod = [{"name": "doctype1", "primkey_in_datadoc": "dk1"}, 
                       {"name": "doctype2", "primkey_in_datadoc": "dk2"}]
        doctype_repo = repos.DomainRepo("Doctype")
        msg = doctype_repo.add_form_lod(Doctype_lod)
        self.assertTrue(msg['message'] == "has been registered" )
        Wfaction_lod = [{"name": "name1",
                         "associated_doctype": {"name": "doctype1"},
                         "need_prev_status": "s0",
                         "need_current_status": "s1",
                         "leads_to_status": "s2",
                         "permitted_to_roles": ["r1",]
                         }]
        actionrepo = repos.DomainRepo("Wfaction")
        msg = actionrepo.add_form_lod(Wfaction_lod)
        self.assertTrue(msg['message'] == 'has been registered')
        msg = actionrepo.list_dict()
        self.assertTrue(isinstance(msg[0], dict))
        self.assertTrue(msg[0]['associated_doctype_name'] == 'doctype1')
        searchf = {"name": "name1"}
        updated_data_dict = {"name": "name1",
                         "associated_doctype": {"name": "doctype2"},
                         "need_prev_status": "s0",
                         "need_current_status": "s1",
                         "leads_to_status": "s2",
                         "permitted_to_roles": ["r1",]
                         }
        msg = actionrepo.update_from_dict(updated_data_dict, **searchf)
        self.assertTrue(msg['status'] == "success")
        
    def test_routes(self):
        pass
        m.dbdriver.delete(m.Wfdoc) 
        m.dbdriver.delete(m.Wfaction)
        m.dbdriver.delete(m.Wfstatus)
        m.dbdriver.delete(m.Datadocfield)
        m.dbdriver.delete(m.Doctype) 
        api_route = '/add/Wfstatuswrong'
        ############WRONG OBJECT NAME   
        data= [{"name1": "ABC"}]        
        return_data = self._post_call(api_route, data)
        self.assertTrue(return_data.get('status') == "InvalidWorkflowObject")
        ############WRONG DATA , IS NOT LIST
        api_route = '/add/Wfstatus'      
        data= {"name1": "ABC"}      
        return_data = self._post_call(api_route, data)        
        self.assertTrue(return_data.get('status') == "InvalidInputDataList")
        ############WRONG DATA, NOT DICTIONARY WITHIN THE LIST            
        data= ["name1" ,  "ABC" ]     
        return_data = self._post_call(api_route, data)        
        self.assertTrue(return_data.get('status') == "InvalidInputDataDict")           
        ############WRONG KEY IN DATA        
        data= [{"name1": "ABC"}]        
        return_data = self._post_call(api_route, data)        
        self.assertTrue(return_data.get('status') == "InvalidKeysInData")
        ############REGISTER WITH CORRECT DATA       
        data= [{"name": "ABC"}]        
        return_data = self._post_call(api_route, data)
        #print(return_data)       
        self.assertTrue(return_data['message'] == "has been registered" )
        ###########LIST WITHOUT FILTER WITH GET METHOD
        api_route = '/list/Wfstatus/all/all'
        msg = self._get_call(api_route)
        self.assertTrue(msg[0].get('name') == "ABC")
        api_route = '/list/Wfstatus/name/ABC'
        msg = self._get_call(api_route)
        self.assertTrue(msg[0].get('name') == "ABC")
        ###########LIST WITH FILTER WITH POST METHOD
        api_route = '/list/Wfstatus'
        filter_data = {"name": "ABC"}
        msg = self._post_call(api_route, filter_data)        
        self.assertTrue(msg[0].get('name') == "ABC")
        ###########UPDATE THE DATA
        api_route = '/update/Wfstatus'
        data_dict = {"update_data_dict": {"name": "DEF"},
                     "search_filter": {"name": "ABC"}
                     }
                              
        msg = self._put_call(api_route, data_dict)
        self.assertTrue(msg['status'] == "success")
        ###########DELETE
        api_route = '/delete/Wfstatus'
        filter_data = {"name": "DEF"}
        msg = self._post_call(api_route, filter_data)        
        self.assertTrue("has been  deleted successfully" in msg)
    
    def test_entities(self):
        m.dbdriver.delete(m.Wfdoc) 
        m.dbdriver.delete(m.Wfaction)
        m.dbdriver.delete(m.Wfstatus)
        m.dbdriver.delete(m.Datadocfield)
        m.dbdriver.delete(m.Doctype)                     
        docrepo = DomainRepo("Wfdoc")
        ###########REGISTER DOCTYPE
        doctype1 = ent.Doctype("doctype1", "dk1")
        doctype2 = ent.Doctype("doctype2", "dk2")
        lodobj = [doctype1, doctype2]
        doctype_repo = DomainRepo("Doctype")  
        msg = doctype_repo.add_list_of_domain_obj(lodobj)
        self.assertTrue(msg['message'] == "has been registered" )
        ########REGISTER ACTION RULES        
        wfaction1_dict=  {"name": "wfaction1",
                         "associated_doctype": {"name": "doctype1"},
                         "need_prev_status": "s0",
                         "need_current_status": "s1",
                         "leads_to_status": "s2",
                         "permitted_to_roles": ["r1",]
                         }
        wfaction2_dict=  {"name": "wfaction2",
                         "associated_doctype": {"name": "doctype2"},
                         "need_prev_status": "s1",
                         "need_current_status": "s2",
                         "leads_to_status": "s3",
                         "permitted_to_roles": ["r2",]
                         }
        wfaction3_dict=  {"name": "wfaction3",
                         "associated_doctype": {"name": "doctype2"},
                         "need_prev_status": "s2",
                         "need_current_status": "s3",
                         "leads_to_status": "s4",
                         "permitted_to_roles": ["r3",]
                         }
        wfaction1 = ent.Wfaction.from_dict(wfaction1_dict)
        wfaction2 = ent.Wfaction.from_dict(wfaction2_dict)
        wfaction3 = ent.Wfaction.from_dict(wfaction3_dict)
        lodobj = [wfaction1, wfaction2, wfaction3]
        action_repo = DomainRepo("Wfaction")
        msg = action_repo.add_list_of_domain_obj(lodobj)
        self.assertTrue(msg['message'] == "has been registered" )
        ############RETRIEVE ACTION1 FROM REPO
        doctype_list_sobj = doctype_repo.list_obj()
        self.assertTrue(isinstance(doctype_list_sobj[0], m.Doctype ))
        doctype_list_dobj = doctype_repo.list_domain_obj()
        self.assertTrue(isinstance(doctype_list_dobj[0], ent.Doctype ))
        action_list_dict = action_repo.list_dict()
        self.assertTrue( isinstance(action_list_dict[0]['associated_doctype'], dict))
        action_list_sobj = action_repo.list_obj()
        self.assertTrue( isinstance(action_list_sobj[0], m.Wfaction))
        action_list_dobj= action_repo.list_domain_obj()
        self.assertTrue( isinstance(action_list_dobj[0], ent.Wfaction))
        seearchf = {"associated_doctype": {"name": "doctype2"}}
        action_list_filtered_by_doctype = action_repo.list_domain_obj(**seearchf)
        self.assertTrue(action_list_filtered_by_doctype[0].associated_doctype.name == 'doctype2')
        self.assertTrue(action_list_filtered_by_doctype[1].associated_doctype.name == 'doctype2')
        ####UPDATE RELATTIONSHIP FIELD ACTION1 DOCTYPE FROM 1 TO 2 
        wfaction1_dict.update( 
            { "associated_doctype": {"name": "doctype2"} } )
        searchf = {"name": "wfaction1"}
        msg = action_repo.update_from_dict(wfaction1_dict, **searchf)
        self.assertTrue(msg['status'] == "success")
        action_list_filtered_by_doctype = action_repo.list_domain_obj(**seearchf)
        self.assertTrue(len(action_list_filtered_by_doctype) == 3)
        ####DEFINING FIELDS FOR DOCTYPE2
        f1_dict = {"name": "field1",
                   "associated_doctype": {"name": "doctype2"},
                   "ftype": "str",
                   "flength": 2,
                   "status_needed_edit": ["s3"]}
        f2_dict = {"name": "field2",
                   "associated_doctype": {"name": "doctype2"},
                   "ftype": "int",
                   "flength": 2,
                   "status_needed_edit": [""]}
        docf_repo = repos.DomainRepo("Datadocfield")
        msg = docf_repo.add_form_lod([f1_dict, f2_dict])
        self.assertTrue(msg['status'] == "success" )
        datadocfields_repo = repos.DomainRepo("Datadocfield")
        searh_filter = {"associated_doctype": {"name": "doctype2"} }
        result = datadocfields_repo.list_domain_obj(**searh_filter)
        fnames = [item.name for item in result]
        self.assertTrue("field1" in fnames)
        ###CHECK THE ID ATTRIBUTE FROM SQL OBJ HAS BEEN PASSED TO DOMAINOBJ
        #self.assertTrue(hasattr(action_list_filtered_by_doctype[0], 'id'))
        doc_data1 = {"field1": "v1" }
        primval_datadoc = doc_data1["field1"]
        wfdoc_dict1 = {"name": primval_datadoc,
                       "associated_doctype": {"name": "doctype2"},
                         "prev_status": "s2",
                         "current_status": "s3",
                         "doc_data": doc_data1,
                         }
        wfdoc_lod = [wfdoc_dict1]
        wfdoc_repo = repos.DomainRepo("Wfdoc")
        msg = wfdoc_repo.add_form_lod(wfdoc_lod)
        #######RETRIEVE DOC USING PRIMKEY
        #####SOMETIMES ADD IS FAILING SINVCE THE associated_doctype in wfdoc_lod
        ###is becoming Doctype object although we are supplying a dict ???????????
        wfdoc_list = wfdoc_repo.list_domain_obj(**{"name": "v1"})
        ##########SEE THE COMNNETS above IN CASE OF INPUT TYPE EXCEPTION       
        self.assertTrue(len(wfdoc_list[0].wfactions) == 3)
        self.assertTrue((wfdoc_list[0].doc_data == doc_data1))
        #####FROM DICT CREATE DOMAIN OBJ AND THEN SAVE TO REPO
        doc_data1 = {"field1": "v2" }
        primval_datadoc = doc_data1["field1"]
        wfdoc_dict2 = {"name": primval_datadoc,
                       "associated_doctype": {"name": "doctype2"},
                         "prev_status": "s2",
                         "current_status": "s3",
                         "doc_data": doc_data1,
                         }
        wfdoc2 = ent.Wfdoc.from_dict(wfdoc_dict2)
        ###ADD THE DOMAIN OBJECT TO THE DOMAIN REPO
        msg = wfdoc_repo.add_list_of_domain_obj([wfdoc2])
        self.assertTrue(msg['message'] == "has been registered" )        
        ###SEE DOCTYPE2 HAVE THE DOCDATAFIELDS
        doctype2Obj_list = doctype_repo.list_domain_obj(**{"name": "doctype2"})
        ###CREATE DOC ONCE ITS FIELDS ARE DEFINED ABOVE        
        doc_data3 = {"field1": "v3" }
        wfdoc_dict3 = {"name": 'v3',
                       "associated_doctype": {"name": "doctype2"},
                       "prev_status": "",
                       "current_status": "Created",
                       "doc_data": doc_data3,
                        }
        ###FAIL FOR FIELD NAME MISTACH
        try:
            ent.Wfdoc.from_dict(wfdoc_dict3)
        except rexc.UnknownFieldNameInDataDoc as e:
            self.assertTrue(e.status == "UnknownFieldNameInDataDoc")
        ##FAILURE FOR FIELD LENGTH LARGER THAN CONFIGURED
        doc_data3 = {"field1": "v44444" }
        wfdoc_dict3.update({"doc_data": doc_data3})
        try:
            ent.Wfdoc.from_dict(wfdoc_dict3)
        except rexc.DataLengthViolation as e:
            self.assertTrue(e.status == "DataLengthViolation")
        ####FAIL FOR FIELD TYPE, FIELD2 SHOULD BE INT TYPE        
        wfdoc_dict3.update({"name": "v3", "doc_data": {"field1": "v3", "field2": "v2"}})
        try:
            ent.Wfdoc.from_dict(wfdoc_dict3)
        except rexc.DataTypeViolation as e:
            self.assertTrue(e.status == "DataTypeViolation")
        ###########CHECK SUCCESS
        wfdoc_dict3.update({"name": "v3", "doc_data": {"field1": "v3", "field2": 10}})
        docobj = ent.Wfdoc.from_dict(wfdoc_dict3)
        self.assertTrue(docobj.name == "v3")
         
    def test_workflow(self):
        m.dbdriver.delete(m.Wfdoc) 
        m.dbdriver.delete(m.Wfaction)
        m.dbdriver.delete(m.Wfstatus)
        m.dbdriver.delete(m.Datadocfield)
        m.dbdriver.delete(m.Doctype)
        self._register_doctype_n_actions()
        wf = Workflow('doctype2', 'r1')        
        ### WORKFLOW IS ABLE TO CREATE DOC
        msg = wf.create_doc({"dk1": "dv1", "dk2": "dv2"})
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
                   "status_needed_edit": ["Created"]}
        docf_repo = repos.DomainRepo("Datadocfield")
        docf_repo.add_form_lod([f1_dict, f2_dict])
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
        wfaction1 = ent.Wfaction.from_dict(wfaction1_dict)
        wfaction2 = ent.Wfaction.from_dict(wfaction2_dict)
        wfaction3 = ent.Wfaction.from_dict(wfaction3_dict)
        lodobj = [wfaction1, wfaction2, wfaction3]
        action_repo = DomainRepo("Wfaction")
        action_repo.add_list_of_domain_obj(lodobj)
    
    def _post_call(self, api_route, data):
#       token_in_byte = self.get_auth_token_with_actual_rsa_keys_fake_user()
        with self.client:
            self.headers = {'X-Auth-Token': "token_in_byte"}
            response = self.client.post(api_route, 
                                        headers=self.headers,
                                        data=json.dumps(data),
                                        content_type='application/json')
            return json.loads(response.data.decode())
        
    def _get_call(self, api_route):
#       token_in_byte = self.get_auth_token_with_actual_rsa_keys_fake_user()
        with self.client:
            self.headers = {'X-Auth-Token': "token_in_byte"}
            response = self.client.get(api_route, 
                                        headers=self.headers,)
            return json.loads(response.data.decode())

    def _put_call(self, api_route, data):
#       token_in_byte = self.get_auth_token_with_actual_rsa_keys_fake_user()
        with self.client:
            self.headers = {'X-Auth-Token': "token_in_byte"}
            response = self.client.put(api_route, 
                                        headers=self.headers,
                                        data=json.dumps(data),
                                        content_type='application/json')
            return json.loads(response.data.decode())

    def _delete_call(self, api_route, data):
#       token_in_byte = self.get_auth_token_with_actual_rsa_keys_fake_user()
        with self.client:
            self.headers = {'X-Auth-Token': "token_in_byte"}
            response = self.client.delete(api_route, 
                                        headers=self.headers,
                                        data=json.dumps(data),
                                        content_type='application/json')
            return json.loads(response.data.decode())