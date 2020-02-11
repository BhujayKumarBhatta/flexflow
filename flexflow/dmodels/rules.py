import json
from flexflow.exceptions import rules_exceptions  as exc

class WFStatus:
    '''Name of workflow status each has an associaltion with a doc_category
    which means the status is meant for a particular document type'''
    
    def __init__(self, name, doc_category):
        self.name = name
        self.doc_category = doc_category
        
    @classmethod
    def from_dict(cls, adict):
        return cls(
            name = adict.get('name'),
            doc_category = adict.get('doc_category'))
        
    def to_dict(self):
        return {"name": self.name, "doc_category":  self.doc_category}
        
    def to_json(self):
        return  json.dumps(self.to_dict())
        
        
class StatusRepo:
    '''holds all the status as a list
    '''
    target_obj = "WFStatus"
    
    def __init__(self, db_engine=None):        
        self.db_engine = db_engine
        
    def add_status_form_dict(self, status_dict:dict):
        db_save_result = self.db_engine.add(self.target_obj, status_dict)
        return db_save_result
        
    def list_status_obj(self, filters={"name_eq": "", "doc_category": ""}):        
        lod = self.db_engine.list(self.target_obj, filters)
        result = [self._create_status_obj(d) for d in lod]    
        return result
    
    def list_status_dicts(self, filters={}):
        lod = self.db_engine.list(self.target_obj, filters)
        return json.dumps(lod)
    
    def delete_status(self, filters={}):
        delete_result = self.db_engine.delete(self.target_obj, filters={})
        return delete_result
    
    def _create_status_object(self, status_dict:dict):
        return WFStatus.from_dict(status_dict)
           

        
    