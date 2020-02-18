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
        m.dbdriver.delete(m.Wfaction)
        m.dbdriver.delete(m.Wfstatus)
        m.dbdriver.delete(m.Doctype)        
        ###########ADDING SINGLE RECORD 
        record = m.Wfstatus(name="Status1")
        msg = m.dbdriver.insert(record)
        #print(msg)           
        self.assertTrue('has been registered' in msg)
        ############UPDATING THE RECORD 
        data = {"name": "Status1111"}
        msg = m.dbdriver.update(m.Wfstatus, data, name='Status1')
        self.assertTrue("updated the follwoing" in msg)
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
        pass
        #####INITIALIZE A REPO FOR DOMAIN ENTITY
        statrepo = repos.DomainRepo("Wfstatus")
        ##############ADD ENTITY
        status_lod = [{"name": "Status1111"}]        
        msg = statrepo.add_form_lod(status_lod)
        self.assertTrue('has been registered' in msg)
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
        self.assertTrue("updated the follwoing" in msg)
        ##########DELETE
        msg = statrepo.delete(name='Status222222')
        self.assertTrue("deleted successfully" in  msg)
        msg=statrepo.list_obj()
        self.assertTrue(not msg)
        ##########Test LOD WHEN RELATION
        Doctype_lod = [{"name": "doctype1"}, {"name": "doctype2"}]
        doctype_repo = repos.DomainRepo("Doctype")
        msg = doctype_repo.add_form_lod(Doctype_lod)
        self.assertTrue('has been registered' in msg)
        Wfaction_lod = [{"name": "name1",
                         "assocated_doctype": {"name": "doctype1"},
                         "need_prev_status": "s0",
                         "need_current_status": "s1",
                         "leads_to_status": "s2",
                         "permitted_to_roles": ["r1",]
                         }]
        actionrepo = repos.DomainRepo("Wfaction")
        msg = actionrepo.add_form_lod(Wfaction_lod)
        self.assertTrue('has been registered' in msg)
        msg = actionrepo.list_dict()
        self.assertTrue(isinstance(msg[0], dict))
        self.assertTrue(msg[0]['assocated_doctype_name'] == 'doctype1')
        searchf = {"name": "name1"}
        updated_data_dict = {"name": "name1",
                         "assocated_doctype": {"name": "doctype2"},
                         "need_prev_status": "s0",
                         "need_current_status": "s1",
                         "leads_to_status": "s2",
                         "permitted_to_roles": ["r1",]
                         }
        msg = actionrepo.update_from_dict(updated_data_dict, **searchf)
        self.assertTrue("updated the follwoing" in  msg)
        
    def test_routes(self):
        pass
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
        self.assertTrue("has been registered" in return_data)
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
        self.assertTrue("updated the follwoing" in msg)         
        self.assertTrue("updated the follwoing" in msg)
        ###########DELETE
        api_route = '/delete/Wfstatus'
        filter_data = {"name": "DEF"}
        msg = self._delete_call(api_route, filter_data)        
        self.assertTrue("has been  deleted successfully" in msg)
    
    def test_entities(self):
        m.dbdriver.delete(m.Wfaction)
        m.dbdriver.delete(m.Wfstatus)
        m.dbdriver.delete(m.Doctype)
        m.dbdriver.delete(m.Wfdoc)              
        docrepo = DomainRepo("Wfdoc")
        ###########register doctype
        doctype1 = ent.Doctype("doctype1")
        doctype2 = ent.Doctype("doctype2")
        lodobj = [doctype1, doctype2]
        doctype_repo = DomainRepo("Doctype")  
        msg = doctype_repo.add_list_of_domain_obj(lodobj)
        self.assertTrue("has been registered" in msg)
        ########register action rules        
        wfaction1_dict=  {"name": "wfaction1",
                         "assocated_doctype": {"name": "doctype1"},
                         "need_prev_status": "s0",
                         "need_current_status": "s1",
                         "leads_to_status": "s2",
                         "permitted_to_roles": ["r1",]
                         }
        wfaction2_dict=  {"name": "wfaction2",
                         "assocated_doctype": {"name": "doctype2"},
                         "need_prev_status": "s1",
                         "need_current_status": "s2",
                         "leads_to_status": "s3",
                         "permitted_to_roles": ["r2",]
                         }
        wfaction3_dict=  {"name": "wfaction3",
                         "assocated_doctype": {"name": "doctype2"},
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
        self.assertTrue("has been registered" in msg)
        ############retrieve action1 from repo
        doctype_list_sobj = doctype_repo.list_obj()
        self.assertTrue(isinstance(doctype_list_sobj[0], m.Doctype ))
        doctype_list_dobj = doctype_repo.list_domain_obj()
        self.assertTrue(isinstance(doctype_list_dobj[0], ent.Doctype ))
        action_list_dict = action_repo.list_dict()
        self.assertTrue( isinstance(action_list_dict[0]['assocated_doctype'], dict))
        action_list_sobj = action_repo.list_obj()
        self.assertTrue( isinstance(action_list_sobj[0], m.Wfaction))
        action_list_dobj= action_repo.list_domain_obj()
        self.assertTrue( isinstance(action_list_dobj[0], ent.Wfaction))
        seearchf = {"assocated_doctype": {"name": "doctype2"}}
        action_list_filtered_by_doctype = action_repo.list_domain_obj(**seearchf)
        self.assertTrue(action_list_filtered_by_doctype[0].assocated_doctype.name == 'doctype2')
        self.assertTrue(action_list_filtered_by_doctype[1].assocated_doctype.name == 'doctype2')
        ####update relattionship field action1 doctype from 1 to 2 
        wfaction1_dict.update( 
            { "assocated_doctype": {"name": "doctype2"} } )
        searchf = {"name": "wfaction1"}
        msg = action_repo.update_from_dict(wfaction1_dict, **searchf)
        self.assertTrue("updated the follwoing" in msg)
        action_list_filtered_by_doctype = action_repo.list_domain_obj(**seearchf)
        self.assertTrue(len(action_list_filtered_by_doctype) == 3)
        ###CHECK THE ID ATTRIBUTE FROM SQL OBJ HAS BEEN PASSED TO DOMAINOBJ
        self.assertTrue(hasattr(action_list_filtered_by_doctype[0], 'id'))
        
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