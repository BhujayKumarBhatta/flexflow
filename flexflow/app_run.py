import flexflow
#from flexflow.configs.prodconf import flexflow_configs , prod_db_conf
from flexflow.configs.testconf import testconf , test_db_conf



c = testconf.yml

token_settings =  c.get('token')
print(token_settings)

conf_obj = {"conf": testconf}

config_list = [conf_obj, c , test_db_conf, token_settings]

#DOn't import bp1 blueprint  it before all  conf and other  objects are initialized 
# from linkInventory.restapi.routes import bp1
bp_list = []

app = flexflow.create_app(blue_print_list=bp_list , config_map_list = config_list)

host = c.get('host_name')
port = c.get('host_port')
ssl = c.get('ssl')
ssl_settings = c.get('ssl_settings')

def main():   
    if  ssl == 'enabled':
        app.run(ssl_context=ssl_settings, host = host, port=port, )
    else:
        app.run(host = host, port=port, )
        
