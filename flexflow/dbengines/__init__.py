# from flask import current_app
# from flexflow.dbengines.mongodb.mongoengine import MongoEngineStorageDriver
# 
# class DBEngines:    
#     
#     def __init__(self, driverclass):
#         self.driverclass = driverclass
#         self.get_active_drivers()      
#     
#     def get_active_drivers(self):
#         db_engines = current_app.config.get('storage_drivers')
#         if db_engines:
#             if self.driver == 'mongodb' and self.driver in db_engines.keys():
#                 mongo_conf = db_engines.get('mongodb')
#                 self.mongodb = MongoStorageDriver(mongo_conf)
#                 return self.driverclass
#                 
#             elif  self.driver == 'mysql' and 'mysql' in db_engines.keys():
#                 mysql_conf = db_engines.get('mysql')
#                 self.driverclass
#             
#             
#             
#     
#     
#     
#     