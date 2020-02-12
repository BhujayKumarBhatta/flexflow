'''test conf'''
import os
import datetime
from tokenleaderclient.rbac import wfc
from flexflow.configs.config_handler import Configs
from flexflow.dbengines.sqlchemy.models import dbdriver
test_data_path = os.path.join(os.path.dirname(__file__),
                               os.pardir, 'tests', 'testdata')
test_client_conf_file = os.path.join(test_data_path, 'test_client_configs.yml')
conf_file= os.path.join(test_data_path,'test_flexflow_configs.yml')
print(test_client_conf_file, conf_file)
# must_have_keys_in_yml = {'host_name',
#                              'host_port',
#                              'ssl',
#                              'ssl_settings',
#                              'database',
#                              'secrets'
#                              'celery'
#                              }
must_have_keys_in_yml = {}
testconf = Configs('flexflow', conf_file=conf_file, must_have_keys_in_yml=must_have_keys_in_yml)
yml = testconf.yml
con_string = dbdriver.get_connection_settings(testconf)
print('con_string', con_string)
test_db_conf = { 'SQLALCHEMY_DATABASE_URI': con_string, 
                'SQLALCHEMY_TRACK_MODIFICATIONS': False }


testwfc= wfc.WorkFuncContext()
testwfc.username = 'user1'
testwfc.org = 'ITC'
testwfc.orgunit = 'ou1'
testwfc.department = 'dept1'
testwfc.roles = ['role1', ]
testwfc.name = 'wfc1'
testwfc.email = 'user1@a.b'
testwfc.request_id = 'hhihihhh-890809-jklkk;k-ytfty'
testwfc.time_stamp = datetime.datetime.utcnow()
testwfc.client_address = '10.10.10.10'


tspwfc= wfc.WorkFuncContext()
tspwfc.username = 'TSP1user1'
tspwfc.org = 'TSP1'
tspwfc.orgunit = 'TSP1ou1'
tspwfc.department = 'TSP1dept1'
tspwfc.roles = ['role1', ]
tspwfc.name = 'TSP1wfc1'
tspwfc.email = 'TSP1user1@a.b'
tspwfc.request_id = 'TSP1ihhh-890809-jklkk;k-ytfty'
tspwfc.time_stamp = datetime.datetime.utcnow()
tspwfc.client_address = '10.10.10.10'

ITSSwfc= wfc.WorkFuncContext()
ITSSwfc.username = 'ITSSuser1'
ITSSwfc.org = 'ITC'
ITSSwfc.orgunit = 'ITSS'
ITSSwfc.department = 'ITSSept1'
ITSSwfc.roles = ['role1', ]
ITSSwfc.name = 'ITSSSwfc1'
ITSSwfc.email = 'ITSSuser1@a.b'
ITSSwfc.request_id = 'ITSSihhh-890809-jklkk;k-ytfty'
ITSSwfc.time_stamp = datetime.datetime.utcnow()
ITSSwfc.client_address = '10.10.10.10'


MISwfc= wfc.WorkFuncContext()
MISwfc.username = 'MISuser1'
MISwfc.org = 'ITC'
MISwfc.orgunit = 'MIS1'
MISwfc.department = 'MISept1'
MISwfc.roles = ['role1', ]
MISwfc.name = 'MISwfc1'
MISwfc.email = 'MISuser1@a.b'
MISwfc.request_id = 'MISihhh-890809-jklkk;k-ytfty'
MISwfc.time_stamp = datetime.datetime.utcnow()
MISwfc.client_address = '10.10.10.10'



