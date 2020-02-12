from flexflow.configs.config_handler import Configs
from flexflow.dbengines.sqlchemy.models import dbdriver
# must_have_keys_in_yml = {'host_name',
#                              'host_port',
#                              'ssl',
#                              'ssl_settings',
#                              'database',
#                              'secrets'
#                              }
must_have_keys_in_yml = {}
 
flexflow_configs = Configs('flexflow', must_have_keys_in_yml=must_have_keys_in_yml)

yml = flexflow_configs.yml

con_string = dbdriver.get_connection_settings(flexflow_configs)
prod_db_conf = { 'SQLALCHEMY_DATABASE_URI': con_string, 
                'SQLALCHEMY_TRACK_MODIFICATIONS': False }

