import json
from flexflow.dbengines.sqlchemy import models as sqlm
from flexflow.exceptions import rules_exceptions  as exc
from flexflow.domains import entities as ent

        
class DomainRepo:
    '''bridge between domain entities  and storage layer
    allows creation of domain objects from list of dictionaries
    and allows all CURD operation
    ''' 
    sql_obJ_map = {"Wfstatus": sqlm.Wfstatus,
                   }
    
    domain_obj_map = {"Wfstatus": ent.Wfstatus,
                   }
    
    def __init__(self, objname:str, dbdriver=sqlm.dbdriver):        
        self.dbdriver = dbdriver
        self.sql_obj = self.sql_obJ_map.get(objname)
        self.domain_obj = self.domain_obj_map.get(objname)
        
    def add_form_lod(self, status_lod:list):        
        db_save_result = self.dbdriver.insert_bulk(self.sql_obj, status_lod)
        return db_save_result
        
    def list_obj(self, **search_filters):        
        lod = self.dbdriver.list(self.sql_obj, **search_filters)
        result = [self._create_domain_object(d) for d in lod]    
        return result
    
    def list_dict(self, **search_filters):
        lod = self.dbdriver.list(self.sql_obj, **search_filters)
        return lod
    
    def update_from_lod(self, updated_data_dict, **search_filters):
        result = self.dbdriver.update(self.sql_obj, updated_data_dict, **search_filters)
        return result
    
#     def delete_status(self, filters={}):
#         delete_result = self.db_engine.delete(self.target_obj, filters={})
#         return delete_result
    
    def _create_domain_object(self, status_dict:dict):
        return self.domain_obj.from_dict(status_dict)
           

        
    