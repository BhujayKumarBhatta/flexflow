import json
from flexflow.dbengines.sqlchemy import models as sqlm
from flexflow.exceptions import rules_exceptions  as rexc
from flexflow.domains import entities as ent
from sqlalchemy.orm.relationships import RelationshipProperty
from sqlalchemy.orm.properties import ColumnProperty

        
class DomainRepo:
    '''bridge between domain entities  and storage layer
    allows creation of domain objects from list of dictionaries
    and allows all CURD operation
    ''' 
    sql_obJ_map = {"Wfstatus": sqlm.Wfstatus,
                   "Doctype": sqlm.Doctype,
                   "Wfaction": sqlm.Wfaction
                   }
    
    domain_obj_map = {"Wfstatus": ent.Wfstatus,
                   }
    
    def __init__(self, objname:str, dbdriver=sqlm.dbdriver):        
        self.dbdriver = dbdriver        
        if self.sql_obJ_map.get(objname):
            self.sql_obj = self.sql_obJ_map.get(objname)
            self.domain_obj = self.domain_obj_map.get(objname)
        else:
            raise rexc.InvalidWorkflowObject(objname, ','.join(self.sql_obJ_map.keys()))
        
    def add_form_lod(self, data_lod:list):
        self._validate_input_data_lod(data_lod)
        db_save_result = self.dbdriver.insert_bulk(self.sql_obj, data_lod)
        return db_save_result
        
    def list_obj(self, **search_filters):        
        lod = self.dbdriver.list(self.sql_obj, **search_filters)
        result = [self._create_domain_object(d) for d in lod]    
        return result
    
    def list_dict(self, **search_filters):
        self._validate_input_data_dict(search_filters)
        lod = self.dbdriver.list(self.sql_obj, **search_filters)
        return lod
    
    def update_from_dict(self, updated_data_dict, **search_filters):
        self._validate_input_data_dict(updated_data_dict)
        result = self.dbdriver.update(self.sql_obj, updated_data_dict, **search_filters)
        return result
    
    def delete(self, **search_filters):
        self._validate_input_data_dict(search_filters)
        delete_result = self.dbdriver.delete(self.sql_obj, **search_filters)
        return delete_result
    
    def _create_domain_object(self, status_dict:dict):
        return self.domain_obj.from_dict(status_dict)
    
    def _validate_input_data_lod(self, data_lod):
        if not isinstance(data_lod, list):
            raise rexc.InvalidInputDataList
        for data_dict in data_lod:
            self._validate_input_data_dict(data_dict)
            
    def _validate_input_data_dict(self, data_dict):        
        if not isinstance(data_dict, dict):
            raise rexc.InvalidInputDataDict
        for k in  data_dict.keys():
                if k not in  self.sql_obj.__dict__.keys():
                    obj_dict_copy = self.sql_obj.__dict__.copy()
                    pop_keys = [i for i in obj_dict_copy if '__' in i]
                    for j in pop_keys: obj_dict_copy.pop(j)
                    if '_sa_class_manager' in obj_dict_copy: obj_dict_copy.pop('_sa_class_manager')
                    if 'id' in obj_dict_copy: obj_dict_copy.pop('id')                 
                    raise rexc.InvalidKeysInData(k, obj_dict_copy.keys())
                else:
                    attr = getattr(self.sql_obj, k)
                    attr_property = attr.property
                    v = isinstance(attr_property, RelationshipProperty)
                    x = isinstance(attr_property, ColumnProperty)
                    #property checking worked well , now get the table name
                    print(attr_property)
                    attr_target = attr_property.target
                    print(attr_target)
                    attr_metatadta = attr.metadata.tables
                    print(attr_metatadta)
                    pass
                
    
            
        
           

        
    