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
        print(app.config.get('storage_drivers'))
        
    def test_models(self):
        record = m.Wfstatus(name="Status1")
#         msg = m.dbdriver.insert(record)            
#         print(msg)
        data = {"name": "Status1111"}
        msg = m.dbdriver.update(m.Wfstatus, data, id=1)
        print(msg)
        msg = m.dbdriver.list(m.Wfstatus)
        print(msg)
        
    

