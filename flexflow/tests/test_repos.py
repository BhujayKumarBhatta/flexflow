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
        ####delete on on existing document is also saying succress to be tested
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
    
    
    
    