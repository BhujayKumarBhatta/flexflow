from flexflow.configs import testconf
from flask_testing import TestCase as FTestCase
import flexflow
from flexflow.dbengines.sqlchemy import models as m
from sqlalchemy import exc
from flexflow.domains import repos

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
        status_lod = [{"name": "Status1111"}]
        statrepo = repos.DomainRepo("Wfstatus")
        msg = statrepo.add_form_lod(status_lod)
        self.assertTrue('has been registered' in msg)
        msg = statrepo.list_obj(name="Status1111")
        self.assertTrue(msg[0].name == 'Status1111')
        msg = statrepo.list_dict(name="Status1111")
        self.assertTrue(msg[0]['name'] == 'Status1111')
        updated_data_dict = {"name": "Status222222"}
        msg = statrepo.update_from_lod(updated_data_dict)
        self.assertTrue("updated the follwoing" in msg)
    

