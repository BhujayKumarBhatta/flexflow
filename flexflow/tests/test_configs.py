from flexflow.configs import testconf
from unittest import TestCase
from flask_testing import TestCase as FTestCase
from flask import Flask
import flexflow
from flexflow.dbengines.sqlchemy import models as m
from sqlalchemy import exc

# class T2(TestCase):
#     def test_conf(self):
#         print(testconf.yml)
        
        
app = flexflow.create_app(config_map_list = [testconf.yml, testconf.test_db_conf])
        
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
        #print(msg)
        self.assertTrue("has been  deleted successfully" in msg)
#         msg = m.dbdriver.insert(record)            
#         print(msg)
#         msg = m.dbdriver.delete(m.Wfstatus, id='all')
#         print(msg)
#         msg = m.dbdriver.list(m.Wfstatus)
#         print(msg)
#         
    

