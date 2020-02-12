import pymongo
try:
    # Python 3.x
    from urllib.parse import quote_plus
except ImportError:
    # Python 2.x
    from urllib import quote_plus



class DataBase(object):    
    
    def __init__(self, conf):
#         print(conf)      
        self.yml = conf.yml
        self.dbs = self.yml.get('database')  
        self.driver = self.dbs.get('DRIVER')
        self.server = self.dbs.get('Server')
        self.database = self.dbs.get('Database')
        self.uid = self.dbs.get('UID')
        self.pwd = conf.decrypt_password(self.dbs.get('db_pwd_key_map'))       
        self.port = self.dbs.get('Port')  
        self.connection_string = ("{}://{}:{}@{}:{}").format(
            self.driver, quote_plus(self.uid), quote_plus(self.pwd),
            self.server, self.port) 
        try:
            self.client = pymongo.MongoClient(self.connection_string) 
        except:   
            print("Could not connect to MongoDB")    
               
        self.db=self.client[self.database]
        
        
    def db_insert_many(self, data, coll_name):
        '''
        data should be a list of dictionaries
        '''
        coll = self.db[coll_name]
        d = coll.insert_many(data)
        if d.acknowledged:
            message = "{} number of records inserted".format("check")            
            result = {"message": message, "coll": coll}
#             print(result)
            return result
    
    def list(self, query, coll_name):
        if query == 'all':
            query = {}  
        coll = self.db[coll_name] 
        colldocs = coll.find(query)
        return colldocs 
        
    def db_delete_many(self, query, coll_name ):
        if query == 'all':
            query = {}
        coll = self.db[coll_name]
        x = coll.delete_many(query)
        print(x.deleted_count, " documents deleted.") 
        return x.deleted_count



