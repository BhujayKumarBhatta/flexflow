from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import exc
from urllib.parse import quote_plus
from flexflow.exceptions import rules_exceptions  as rexc
# from sqlalchemy.orm import mapper, scoped_session, sessionmaker

    
class SqlalchemyDriver:
 
    def __init__(self, objname_to_objmap=None):        
        
        self.db = SQLAlchemy()
        self.migrate = Migrate()
        self.objname_to_objmap = objname_to_objmap

    def get_connection_settings(self, confobj):
        self.yml = confobj.yml
        self.storage_drivers = self.yml.get('storage_drivers')        
        self.mysql_conf = self.storage_drivers.get('mysql')
        self.server = self.mysql_conf.get('Server')
        self.database = self.mysql_conf.get('Database')
        self.uid = self.mysql_conf.get('UID')
        self.pwd = confobj.decrypt_password(self.mysql_conf.get('db_pwd_key_map'))        
        self.port = self.mysql_conf.get('Port')
        self.raw_connection_string = ('mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8mb4').format(
                                                                    self.uid, 
                                                                    self.pwd,
                                                                    self.server, 
                                                                    self.port, 
                                                                    self.database )
        #self.connection_string = quote_plus(self.raw_connection_string)
        return self.raw_connection_string
        
    def connect_to_database(self):
#             self.engine=create_engine(self.connection_string)
#             self.session=scoped_session(sessionmaker (autocommit=False,
#                                                 autoflush=False,
#                                                 bind=self.engine ))         
#             self.conn=self.engine.connect()
        pass
    
    def insert(self, record):
        if record:
            try:
                msg = self.db.session.add(record)        
                self.db.session.commit()               
                msg = "Registered in DB"  
                status = "success"
            except exc.IntegrityError as e :
                msg = ('databse integrity error, {} by the same name may be already present  or all the requred'
                       'fileds has not been supplied.\n\n Full detail: {}'.format( record, e))
                self.db.session.rollback()
                status = "failed"
                #raise
            except  Exception as e:
                msg =("{} could not be registered , the erro is: \n  {}".format(record, e))
                status = "failed"
                self.db.session.rollback() 
        msg = {"status": status,  "message": msg, "objectdict": record.to_dict() }   
        #print(msg)
        return msg
    
    def add_from_lod_mock(self, lod:list):
        pass
        #iterate through lod and get the dict 
        #the relationship keys will have the value as id or primary key 
        #auto id by sql may not work for this purpose , we might have to assign uuid or name field as the primary key
        #from the dict identify which keys are relationship and to which class
        #for relationship keys  search the respective class to get the object
        # append to a list of object - convert lod to loobj
        # use  session.all_all(loobj)
    
    def insert_bulk(self, target_class_obj, lod:list):
        Obj = target_class_obj
        try:
            self.db.session.bulk_insert_mappings(Obj, lod)     
            self.db.session.commit()
            msg = "has been registered"       
        except exc.IntegrityError as e :
            msg = ('databse integrity error, the same name may be already present  or all the requred'
                   'fileds has not been supplied.\n\n Full detail: {}'.format( e))
            self.db.session.rollback()
            #raise
        except  Exception as e:
            msg =("could not be registered , the erro is: \n  {}".format(e))
            self.db.session.rollback() 
        #print(msg)
        return msg
    
    def add_from_lobj(self, lobj:list):
        #Obj = target_class_obj
        try:
            self.db.session.add_all(lobj)     
            self.db.session.commit()
            msg = {"status": "success", "message": "has been registered", "objects": [l.to_dict() for l in lobj]} 
        except  Exception as e:
            msg ={"status": "Failed", 
                  "message": "could not be registered , the erro is: \n  {}".format(e),
                  "objects": [l.to_dict() for l in lobj]}
            self.db.session.rollback() 
        #print(msg)
        return msg
    
    def update_all(self, target_class_obj, updated_data:dict, **search_filters ):
        ''' Danger : if no search_filter if provided it will change all the records '''
        msg='no such record found to update'
        updated_value_list = []
        Obj = target_class_obj
        query_result = self.db.session.query(Obj).filter_by(**search_filters)
        for matchedObj in query_result:
            for k, v in updated_data.items():
                what_updated = ('{} attribute from current value {}'
                      ' to  {}'.format(k, getattr(matchedObj, k), v)
                      )
                updated_value_list.append(what_updated)
                setattr(matchedObj, k, v)
        if query_result and updated_value_list:            
            try:                
                self.db.session.commit()
                msg = {"message": "updated the follwoing %s" %updated_value_list,
                       "status": "success"}
            except  Exception as e:
                msg ={ "message": "could not be updated , the erro is: \n  {}".format( e),
                      "status": "failed"}
                self.db.session.rollback() 
        #print(msg)
        return msg
    
    def update(self, target_class_obj, updated_data:dict, **search_filters ):
        '''SAFE: without search filter no records will be updated'''        
        if not search_filters: raise rexc.SearhKeyNotProvided
        msg='no such record found to update'
        updated_value_list = []
        qdict = {}
        Obj = target_class_obj
        query_result = self.db.session.query(Obj).filter_by(**search_filters).first()
        for k, v in updated_data.items():
            what_updated = ('{} attribute from current value {}'
                  ' to  {}'.format(k, getattr(query_result, k), v)
                  )
            updated_value_list.append(what_updated)
            setattr(query_result, k, v)
        qdict = query_result.to_dict()
        #qdict.update(updated_data)
        if query_result and updated_value_list:            
            try:                
                self.db.session.commit()
                msg = {"message" : "updated the follwoing %s" %updated_value_list,
                       "status": "success", "objectdict": qdict}
            except  Exception as e:
                msg = {"message": "could not be updated , the erro is: \n  {}".format( e),
                       "status": "failed", "objectdict": qdict}
                self.db.session.rollback() 
        #print(msg)
        return msg  
    
    def list_as_dict(self, target_class_obj,  **search_filters ):            
        result_list = []
        Obj = target_class_obj
        #print('filter for the listing is  %s' %(search_filters))
        if not search_filters:
            query_result = self.db.session.query(Obj).all()            #result = conn.execute(s)
        else:
            query_result = self.db.session.query(Obj).filter_by(**search_filters)
        #obj_from_qry = [obj for obj in query_result]
        for obj in query_result:
            d = obj.to_dict()  #we have to keep a to_dict method in sql models
            #after copy method is loosing the attributes which have relationship
            #d = obj.__dict__.copy() ##THIS IS A WIRED BEHAVIOUR AND REASON FOR NOT USING DUNDER METHODS DIRECTLY
            result_list.append(d)
        for d in result_list:
            ####CAN WE KEEP THE SA INSTANCE AND PASS IT TO DOMAIN ENTITIES TO MAKE BOTH SQL AND ENTTITIES OBJECT HAVING SA INSTANCE STATE
            if '_sa_instance_state' in d:
                d.pop('_sa_instance_state')
        return result_list
    
    def list_as_obj(self, target_class_obj,  **search_filters ): 
        Obj = target_class_obj
        #print('filter for the listing is  %s' %(search_filters))
        if not search_filters:
            query_result = self.db.session.query(Obj).all()            #result = conn.execute(s)
        else:
            query_result = self.db.session.query(Obj).filter_by(**search_filters)        
        return query_result

    def delete(self, target_class_obj, **search_filters):
        record = None
        Obj = target_class_obj
        if search_filters:        
            query_result = self.db.session.query(Obj).filter_by(**search_filters)
            ##TODO: when search is wrong is it giving a  query_result?
            for record in query_result:
                self.db.session.delete(record) 
        else:
            query_result = self.db.session.query(Obj).delete()    
        if  query_result:
            #when search is worng how it is coming inside this condition???
            try:      
                self.db.session.commit()             
                status = "{} has been  deleted successfully".format(search_filters)
                return status
            except  Exception as e:
                    status = "{} could not be deleted , the erro is: \n  {}".format(search_filters, e)
        else:
            status = "{} not found in database".format(search_filters)
        return status   

    
'''
docker run  --name mysql -p 3307:3306 -v /opt/mysqldata:/var/lib/mysql  -e MYSQL_ROOT_PASSWORD=welcome@123 -d mysql

mysql -h 172.17.0.4 -u root -p
docker exec -it mysql bash

GRANT ALL ON *.* TO root@'%' IDENTIFIED BY 'welcome@123';

CREATE USER 'lnet'@'localhost' IDENTIFIED BY 'welcome@123';
GRANT ALL PRIVILEGES ON *.* TO 'lnet'@'localhost' WITH GRANT OPTION;

CREATE USER 'lnet'@'%' IDENTIFIED BY 'welcome@123';
GRANT ALL PRIVILEGES ON *.* TO 'lnet'@'%' WITH GRANT OPTION;

flush privileges;



https://docs.sqlalchemy.org/en/latest/orm/tutorial.html

from linkInventory.db.models  import NetLink
from linkInventory.db.engine import conf, DataBase
db = DataBase(conf)


for instance in db.session.query(NetLink).order_by(NetLink.serial_no):
   print(instance.link_type)
   
query = db.session.query(NetLink).filter_by(serial_no=1)
query.all()
query.first()
query.count()


how to create the db using flsk-sqlalchemy ?  for normal sqlalchemy : 

engine = sqlalchemy.create_engine(url)  # connect to server

create_str = "CREATE DATABASE IF NOT EXISTS %s ;" % (DATABASE)
engine.execute(create_str)
engine.execute("USE location;")
db.create_all()
db.session.commit()
 


'''