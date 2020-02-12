from mongoengine import connect

try:
    # Python 3.x
    from urllib.parse import quote_plus
except ImportError:
    # Python 2.x
    from urllib import quote_plus


class MongoStorageDriver(object):    
    
    def __init__(self, conf):
#         print(conf)      
        self.yml = conf
        self.dbs = self.yml.get('database')  
        self.driver = self.dbs.get('DRIVER')
        self.server = self.dbs.get('Server')
        self.database = self.dbs.get('Database')
        self.uid = self.dbs.get('UID')
        self.pwd = conf.decrypt_password(self.dbs.get('db_pwd_key_map'))       
        self.port = self.dbs.get('Port')  
        self.connection_string = ("{}://{}:{}@{}:{}/{}").format(
            self.driver, quote_plus(self.uid), quote_plus(self.pwd),
            self.server, self.port,  self.database) 
        try:
            self.connect = connect(db=self.database,                                    
                                   port=self.port,
                                   username=self.uid,
                                   password=(self.pwd),
                                   host=self.server,
                                   authentication_source=self.uid,
                                   alias='default'
                                   )
#              self.connect = connect(db=self.database, host=self.connection_string,
#                                     authentication_source='admin')
        except:   
            print("Could not connect to MongoDB")    
               
     
'''


from importlib import reload
from micros1.db.mongoengine import MongoEng
from micros1.configs.prodconf import conf
mongoe = MongoEng(conf)
from micros1.db.models import Page
page = Page(title='Using MongoEngine')
page.save()
mongoe.connection_string



'''      
        
  