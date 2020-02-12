import yaml
import os
import sys
import six
from cryptography.fernet import Fernet


class Configs():
    
    test_data_path = os.path.join(os.path.dirname(__file__),
                               os.pardir, 'tests', 'testdata')
        
    def __init__(self, service_name, conf_file=None, must_have_keys_in_yml={} ):
        #    
        self.must_have_keys_in_yml = must_have_keys_in_yml 
        
        if conf_file:
            self.config_file = conf_file
        else:            
            self.config_file='/etc/tokenleader/{}_configs.yml'.format(service_name, service_name)

        if not os.path.exists(self.config_file):
            print("no configuration file found. you need to create a config file "
                  "first in {} ".format(self.config_file))
            sys.exit()
        else:            
            self.yml = self.parse_yml(self.config_file)            
#         print(self.general_config.keys()) 
            if  sorted(self.yml.keys()) >= sorted(self.must_have_keys_in_yml):
                pass                                    
                
            else:
                print("{} file must have the following sections {}".format(
                    self.config_file, self.must_have_keys_in_yml ))
                print('config %s ' % sorted(self.yml.keys()))
                print('must have %s ' % sorted(self.must_have_keys_in_yml))
                sys.exit()
            if (self.yml.get('secrets').get('user_auth_info_file_location')) == 'testlocation':  
                test_secret_file= os.path.join(self.test_data_path,'secrets.yml')                
                self.secret_file_loc_from_yml = test_secret_file
                print('reading configs from test path  ', self.test_data_path )
            else:
                self.secret_file_loc_from_yml = self.yml.get('secrets').get('user_auth_info_file_location')
                
            if self.yml.get('secrets').get('fernet_key_file') == 'testlocation':
                test_fernet_file = os.path.join(self.test_data_path,'fernet_key_file.yml')
                self.fernet_file_loc_from_yml = test_fernet_file
            else:
                self.fernet_file_loc_from_yml = self.yml.get('secrets').get('fernet_key_file')
                    
    def parse_yml(self, file):
        with open(file, 'r') as f:
            try:
                parsed = yaml.safe_load(f)
            except yaml.YAMLError as e:            
                raise ValueError(six.text_type(e))
            return parsed or {}
    
    def  get_fernet_cipher_from_keyfile(self, keyfilepath):
        filepath =  os.path.expanduser(keyfilepath)
        dirpath = os.path.dirname(filepath)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)        
        if not  os.path.exists(keyfilepath):
            key = Fernet.generate_key()
            with open(filepath, 'wb') as f:
                f.write(key)
        
        with open(filepath, 'rb') as f:
           file_content = f.readline()        
           cipher_suite = Fernet(file_content)        
           return cipher_suite
        
    
    def generate_secret_file(self, key_map, text_pwd):
        '''
        stores encrypted password. user should use a cli utility to call this method to generate 
        the file
        '''
        #file_loc_from_yml = self.yml.get('secrets').get('secrets_file_location')
        filepath =  os.path.expanduser(self.secret_file_loc_from_yml)
        dirpath = os.path.dirname(filepath)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)  
                      
        if  os.path.exists(filepath): 
            existing_secrets = self.parse_yml(filepath)
                        
        else:
            existing_secrets = {}
            
        cipher_suite = self.get_fernet_cipher_from_keyfile(
            self.fernet_file_loc_from_yml)
        
        byte_password = text_pwd.encode("utf-8")
        encrypted_password = cipher_suite.encrypt(byte_password)
        encrypted_password_text = bytes(encrypted_password).decode("utf-8")                 
              
        new_secrets = {key_map: encrypted_password_text}
        existing_secrets.update(new_secrets) 
        
        with open(filepath, 'w') as f:
            yaml.dump(existing_secrets, f, default_flow_style=False)
            msg =  ("file {} has been generated".format(filepath))
        
        print(msg)
        return self
        

    def decrypt_password(self, key_map):                
       
#         file_loc_from_yml = self.yml.get('secrets').get('secrets_file_location')
#         filepath =  os.path.expanduser(file_loc_from_yml)
#         print(filepath)
        filepath =  os.path.expanduser(self.secret_file_loc_from_yml)
        try:    
            cipher_suite = self.get_fernet_cipher_from_keyfile(
                                            self.fernet_file_loc_from_yml)
                    
            secret_yml = self.parse_yml(filepath)
            encrpted_text_from_file = secret_yml.get(key_map)               
            msg = "got the encrypted the password"
            
            byte_encrpted_text = encrpted_text_from_file.encode("utf-8")            
            byte_decrpted_text = cipher_suite.decrypt(byte_encrpted_text)
            clear_decrypted_text = bytes(byte_decrpted_text).decode("utf-8")  
            
        except Exception as e:
            msg = " secret  file or the keymap or fernetkey file is not found, the full error is {}".format(e)
            print(msg)
            clear_decrypted_text = ""            
            sys.exit()     
            
        return clear_decrypted_text   
    
    

#     
