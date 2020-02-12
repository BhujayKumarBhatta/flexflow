from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import exc
from urllib.parse import quote_plus
# from sqlalchemy.orm import mapper, scoped_session, sessionmaker

    
class SqlalchemyDriver:
    
#     metadata=MetaData()
    
    def __init__(self, objname_to_objmap:dict):        
        
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
            self.connection_string = quote_plus(self.raw_connection_string)
        
        
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
                    self.db.session.add(record)        
                    self.db.session.commit()
                    msg = "{} has been registered.".format(record.to_dict())         
                except exc.IntegrityError as e :
                    msg = ('databse integrity error, {} by the same name may be already present  or all the requred'
                           'fileds has not been supplied.\n\n Full detail: {}'.format( record, e))
                    self.db.session.rollback()
                    #raise
                except  Exception as e:
                    msg =("{} could not be registered , the erro is: \n  {}".format(record, e))
                    self.db.session.rollback() 
            print(msg)
            return msg
        
        def update(record):
            if record:
                try:                
                    self.db.session.commit()
                    msg = "{} has been updated.".format(record)         
                except exc.IntegrityError as e :
                    msg = ('databse integrity error, {}Full detail: {}'.format( record, e))
                    self.db.session.rollback()
                    #raise
                except  Exception as e:
                    msg =("{} could not be updated , the erro is: \n  {}".format(record, e))
                    self.db.session.rollback() 
            print(msg)
            return msg  
        
        def list_obj(objname,  **kwargs ):
            #objmap = {"Rate": Rate, "Payment": Payment, "Altaddress": Altaddress,
            #       "Lnetlink": Lnetlink}
            Obj = self.objname_to_objmap.get(objname)
            result_list = []
            print('filter for the listing is  %s' %(kwargs))
            if Obj:
                if not kwargs:
                    query_result = self.db.session.query(Obj).all()            #result = conn.execute(s)
                else:
                    query_result = self.db.session.query(Obj).filter_by(**kwargs)
                for rowObj in query_result:
                    d = rowObj.to_dict()
                    d = rowObj.__dict__()
                    result_list.append(d)
            return result_list


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