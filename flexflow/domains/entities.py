import json
from flexflow.dbengines.sqlchemy import models as sqlm
from flexflow.exceptions import rules_exceptions  as exc

class Wfstatus:
    '''Name of workflow status each has an associaltion with a doc_category
    which means the status is meant for a particular document type'''
    
    def __init__(self, name):
        self.name = name        
        
    @classmethod
    def from_dict(cls, adict):
        return cls(
            name = adict.get('name'),  )
        
    def to_dict(self):
        return {"name": self.name}
        
    def to_json(self):
        return  json.dumps(self.to_dict())
        
        
class StatusRepo:
    '''holds all the status as a list
    '''    
    sql_obj = sqlm.Wfstatus
    domain_obj = Wfstatus
    
    def __init__(self, dbdriver=sqlm.dbdriver):        
        self.dbdriver = dbdriver
        
    def add_status_form_lod(self, status_lod:list):        
        db_save_result = self.dbdriver.insert_bulk(self.sql_obj, status_lod)
        return db_save_result
        
    def list_status_obj(self, **search_filters):        
        lod = self.dbdriver.list(self.sql_obj, **search_filters)
        result = [self._create_status_obj(d) for d in lod]    
        return result
    
#     def list_status_dicts(self, filters={}):
#         lod = self.db_engine.list(self.target_obj, filters)
#         return lod
    
#     def delete_status(self, filters={}):
#         delete_result = self.db_engine.delete(self.target_obj, filters={})
#         return delete_result
    
    def _create_status_object(self, status_dict:dict):
        return self.domain_obj.from_dict(status_dict)
           

        
    