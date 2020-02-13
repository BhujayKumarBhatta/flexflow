import json
from flexflow.configs import testconf
from flask_testing import TestCase as FTestCase
import flexflow
from flexflow.dbengines.sqlchemy import models as m
from sqlalchemy import exc
from flexflow.domains import repos
from flexflow.restapi.routes import bp1


        
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
        m.dbdriver.delete(m.Wfstatus)
        ###########ADDING SINGLE RECORD 
        record = m.Wfstatus(name="Status1")
        msg = m.dbdriver.insert(record)
        #print(msg)           
        self.assertTrue('has been registered' in msg)
        ############UPDATING THE RECORD 
        data = {"name": "Status1111"}
        msg = m.dbdriver.update(m.Wfstatus, data, name='Status1')
        self.assertTrue("updated the follwoing" in msg)
        msg = m.dbdriver.list(m.Wfstatus, name="Status1111")
        self.assertTrue(msg[0]['name'] == 'Status1111')
        #DELETE A SINGLE RECORD FILTERED BY NAME
        msg = m.dbdriver.delete(m.Wfstatus, name="Status1111")        
        self.assertTrue("has been  deleted successfully" in msg)
        #########INSERT BULK
        lod = [{"name": "status2"}, {"name": "status3"}, {"name": "status4"}]
        msg = m.dbdriver.insert_bulk(m.Wfstatus, lod)        
        msg = m.dbdriver.list(m.Wfstatus)
        self.assertTrue(len(msg) == 3)
        ###########DELETE ALL
        msg = m.dbdriver.delete(m.Wfstatus)
        print(msg)
        
    def test_repos(self):
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
        msg = statrepo.update_from_lod(updated_data_dict)
        self.assertTrue("updated the follwoing" in msg)
        ##########DELETE
        msg = statrepo.delete(name='Status222222')
        self.assertTrue("deleted successfully" in  msg)
        msg=statrepo.list_obj()
        self.assertTrue(not msg)
      
    def test_routes(self):
        api_route = '/wfmaster/add/Wfstatuswrong'
        ############WRONG OBJECT NAME   
        data= [{"name1": "ABC"}]        
        return_data = self._post_call(api_route, data)
        self.assertTrue(return_data.get('status') == "InvalidWorkflowObject")
        ############WRONG DATA , IS NOT LIST
        api_route = '/wfmaster/add/Wfstatus'      
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
            
    def _post_call(self, api_route, data):
#       token_in_byte = self.get_auth_token_with_actual_rsa_keys_fake_user()
        with self.client:
            self.headers = {'X-Auth-Token': "token_in_byte"}
            response = self.client.post(api_route, 
                                        headers=self.headers,
                                        data=json.dumps(data),
                                        content_type='application/json')
            return json.loads(response.data.decode())

