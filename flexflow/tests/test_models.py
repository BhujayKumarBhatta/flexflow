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
        
    def test_models(self):
        m.dbdriver.delete(m.Wfdocaudit) 
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
        
    