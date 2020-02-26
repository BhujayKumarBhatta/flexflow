import os
import json
import datetime
import jwt
from io import BytesIO
from flexflow.configs import testconf
from flask_testing import TestCase as FTestCase
import flexflow
from flexflow.dbengines.sqlchemy import models as m, SqlalchemyDriver
from sqlalchemy import exc
from flexflow.domains import repos
from flexflow.restapi.routes import bp1
from flexflow.restapi.wfdoc_routes import wf_doc_bp
from flexflow.domains.repos import DomainRepo
from flexflow.domains.entities import entities as ent
from flexflow.domains.domainlogics.workflow import Workflow
from flexflow.exceptions import rules_exceptions  as rexc

from flexflow.configs.testconf import  test_data_path
test_file = os.path.join(test_data_path, 'sample_inv_upload_v2.xlsx')
        
app = flexflow.create_app(config_map_list = [testconf.yml, testconf.test_db_conf],
                          blue_print_list = [bp1, wf_doc_bp])
        
class Tflask(FTestCase):
    
    def create_app(self):       
#         app.config.from_object('app1.configs.testconfigs.TestConfig')
        app.config['TESTING'] = True
        app.config['LIVESERVER_PORT'] = 0
        return app    
        
#     def test_routes(self):
#         pass
#         m.dbdriver.delete(m.Wfdoc) 
#         m.dbdriver.delete(m.Wfaction)
#         m.dbdriver.delete(m.Wfstatus)
#         m.dbdriver.delete(m.Datadocfield)
#         m.dbdriver.delete(m.Doctype) 
#         api_route = '/add/Wfstatuswrong'
#         ############WRONG OBJECT NAME   
#         data= [{"name1": "ABC"}]        
#         return_data = self._post_call(api_route, data)
#         self.assertTrue(return_data.get('status') == "InvalidWorkflowObject")
#         ############WRONG DATA , IS NOT LIST
#         api_route = '/add/Wfstatus'      
#         data= {"name1": "ABC"}      
#         return_data = self._post_call(api_route, data)        
#         self.assertTrue(return_data.get('status') == "InvalidInputDataList")
#         ############WRONG DATA, NOT DICTIONARY WITHIN THE LIST            
#         data= ["name1" ,  "ABC" ]     
#         return_data = self._post_call(api_route, data)        
#         self.assertTrue(return_data.get('status') == "InvalidInputDataDict")           
#         ############WRONG KEY IN DATA        
#         data= [{"name1": "ABC"}]        
#         return_data = self._post_call(api_route, data)        
#         self.assertTrue(return_data.get('status') == "InvalidKeysInData")
#         ############REGISTER WITH CORRECT DATA       
#         data= [{"name": "ABC"}]        
#         return_data = self._post_call(api_route, data)
#         #print(return_data)       
#         self.assertTrue(return_data['message'] == "has been registered" )
#         ###########LIST WITHOUT FILTER WITH GET METHOD
#         api_route = '/list/Wfstatus/all/all'
#         msg = self._get_call(api_route)
#         self.assertTrue(msg[0].get('name') == "ABC")
#         api_route = '/list/Wfstatus/name/ABC'
#         msg = self._get_call(api_route)
#         self.assertTrue(msg[0].get('name') == "ABC")
#         ###########LIST WITH FILTER WITH POST METHOD
#         api_route = '/list/Wfstatus'
#         filter_data = {"name": "ABC"}
#         msg = self._post_call(api_route, filter_data)        
#         self.assertTrue(msg[0].get('name') == "ABC")
#         ###########UPDATE THE DATA
#         api_route = '/update/Wfstatus'
#         data_dict = {"update_data_dict": {"name": "DEF"},
#                      "search_filter": {"name": "ABC"}
#                      }
#                               
#         msg = self._put_call(api_route, data_dict)
#         self.assertTrue(msg['status'] == "success")
#         ###########DELETE
#         api_route = '/delete/Wfstatus'
#         filter_data = {"name": "DEF"}
#         msg = self._post_call(api_route, filter_data)        
#         self.assertTrue("has been  deleted successfully" in msg)  
    
    def test_upload_xl(self):
        self._register_doctype_n_actions()
        api_route = "/wfdoc/uploadxl/doctype2"
        filepath = test_file
        msg = self._file_upload_post(api_route, filepath)
        print(msg)
    
    def _register_doctype_n_actions(self):
        m.dbdriver.delete(m.Wfdoc) 
        m.dbdriver.delete(m.Wfaction)
        m.dbdriver.delete(m.Wfstatus)
        m.dbdriver.delete(m.Datadocfield)
        m.dbdriver.delete(m.Doctype) 
        doctype1 = ent.Doctype("doctype1", "dk1")
        doctype2 = ent.Doctype("doctype2", "invoiceno")
        lodobj = [doctype1, doctype2]
        doctype_repo = DomainRepo("Doctype")
        doctype_repo.add_list_of_domain_obj(lodobj)
        ####DEFINING FIELDS FOR DOCTYPE2
        f1_dict = {"name": "invoiceno",
                   "associated_doctype": {"name": "doctype2"},
                   "ftype": "str",
                   "flength": 100,
                   "status_needed_edit": [""]} #this should be status not role
        f2_dict = {"name": "dk2",
                   "associated_doctype": {"name": "doctype2"},
                   "ftype": "str",
                   "flength": 10,
                   "status_needed_edit": ["Created"]}
        docf_repo = repos.DomainRepo("Datadocfield")
        docf_repo.add_form_lod([f1_dict, f2_dict])
        wfcaction_create = {"name": "Create",
                         "associated_doctype": {"name": "doctype2"},
                         "need_prev_status": "NewBorn",
                         "need_current_status": "NewBorn",
                         "leads_to_status": "Created",
                         "permitted_to_roles": ["role1",]
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
    
    def _post_call(self, api_route, data):                                        
        token_in_byte = self.get_auth_token_with_actual_rsa_keys_fake_user()
        with self.client:
            self.headers = {'X-Auth-Token': token_in_byte}
            response = self.client.post(api_route, 
                                        headers=self.headers,
                                        data=json.dumps(data),
                                        content_type='application/json')
            return json.loads(response.data.decode())
     
    def _file_upload_post(self, api_route, filepath):
        token_in_byte = self.get_auth_token_with_actual_rsa_keys_fake_user()
        #{'file': (BytesIO(b'my file contents'), "work_order.123"), }
        
        
#         files = {'file': ( os.path.basename(filepath), 
#                           open(filepath, 'rb'), 
#                           'application/vnd.ms-excel', 
#                           {'Expires': '0'})}

        files = {'file':  open(filepath, 'rb'),}
        
        
        with self.client:
            self.headers = {'X-Auth-Token': token_in_byte}
            response = self.client.post(api_route, 
                                        headers=self.headers,
                                        data=files,
                                        #content_type='application/json')
                                        content_type='multipart/form-data')
            return json.loads(response.data.decode())
                 
        #r = self.client.post(service_endpoint, headers=headers, 
        #                     files=files, verify=self.ssl_verify)
        
        
    def _get_call(self, api_route):
        token_in_byte = self.get_auth_token_with_actual_rsa_keys_fake_user()
        with self.client:
            self.headers = {'X-Auth-Token': token_in_byte}
            response = self.client.get(api_route, 
                                        headers=self.headers,)
            return json.loads(response.data.decode())

    def _put_call(self, api_route, data):
        token_in_byte = self.get_auth_token_with_actual_rsa_keys_fake_user()
        with self.client:
            self.headers = {'X-Auth-Token': token_in_byte}
            response = self.client.put(api_route, 
                                        headers=self.headers,
                                        data=json.dumps(data),
                                        content_type='application/json')
            return json.loads(response.data.decode())

    def _delete_call(self, api_route, data):
        token_in_byte = self.get_auth_token_with_actual_rsa_keys_fake_user()
        with self.client:
            self.headers = {'X-Auth-Token': token_in_byte}
            response = self.client.delete(api_route, 
                                        headers=self.headers,
                                        data=json.dumps(data),
                                        content_type='application/json')
            return json.loads(response.data.decode())
           
    def get_auth_token_with_actual_rsa_keys_fake_user(self, wfc={'department': 'dept1',
                                'name': 'TATAWFC',
                                'orgunit': 'TATA',
                                'id': 1, 
                                'org': 'TATA'}):          
        user_from_db = {'id': 1,
                        'username': 'u1', 
                        'email': 'u1@abc.com', 
                        'roles': ['role1'],
                        'creation_date': str(datetime.datetime.utcnow()),
                        'allowemaillogin': 'N',
                        'is_active': 'Y',
                        'wfc': wfc,
                        'created_by': 1
                        }

        payload = {
                    'exp': (datetime.datetime.utcnow() + \
                            datetime.timedelta(days=0,
                                               seconds=200)),
                    'iat': datetime.datetime.utcnow(),
                    'sub': user_from_db
                     }
        privkey_path = app.config.get('token').get('private_key_file_location')
        privkey_path = os.path.expanduser(privkey_path)
        #print('priv key exists', os.path.exists(privkey_path))
        #print('private key path: ', privkey_path)
        with  open(privkey_path) as f:
            privkey = f.read()
        auth_token = self._generate_encrypted_auth_token(payload, privkey)#        
        return auth_token
    
    def _generate_encrypted_auth_token(self, payload, priv_key):
        #print(payload)
        #print(priv_key)
        try:
            auth_token = jwt.encode(
                 payload,
                 priv_key,
                 algorithm='RS512'
            )
            return auth_token
        except Exception as e:
            return e
        
        
        