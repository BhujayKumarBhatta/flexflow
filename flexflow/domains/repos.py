import json
from flexflow.dbengines.sqlchemy import models as sqlm
from flexflow.exceptions import rules_exceptions  as rexc
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
        if objname in self.sql_obJ_map.keys():
            self.sql_obj = self.sql_obJ_map.get(objname)
            self.domain_obj = self.domain_obj_map.get(objname)
        else:
            raise rexc.InvalidWorkflowObject(objname, self.sql_obJ_map.keys())
        
    def add_form_lod(self, data_lod:list):
        self._validate_input_data_lod(data_lod)
        db_save_result = self.dbdriver.insert_bulk(self.sql_obj, data_lod)
        return db_save_result
        
    def list_obj(self, **search_filters):        
        lod = self.dbdriver.list(self.sql_obj, **search_filters)
        result = [self._create_domain_object(d) for d in lod]    
        return result
    
    def list_dict(self, **search_filters):
        lod = self.dbdriver.list(self.sql_obj, **search_filters)
        return lod
    
    def update_from_lod(self, updated_data_dict, **search_filters):
        self._validate_input_data_dict(updated_data_dict)
        result = self.dbdriver.update(self.sql_obj, updated_data_dict, **search_filters)
        return result
    
    def delete(self, **search_filters):
        delete_result = self.dbdriver.delete(self.sql_obj, **search_filters)
        return delete_result
    
    def _create_domain_object(self, status_dict:dict):
        return self.domain_obj.from_dict(status_dict)
    
    def _validate_input_data_lod(self, data_lod):
        for data_dict in data_lod:
            self._validate_input_data_dict(data_dict)
            
    def _validate_input_data_dict(self, data_dict):
        for k in  data_dict.keys():
                if k not in  self.sql_obj__dict__.keys():
                    raise rexc.InvalidKeysInData(k, self.sql_obj__dict__.keys())
        
           

        
    