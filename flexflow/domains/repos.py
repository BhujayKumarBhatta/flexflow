import json
import inspect
from flexflow.dbengines.sqlchemy import models as sqlm
from flexflow.exceptions import rules_exceptions  as rexc
from sqlalchemy.orm.relationships import RelationshipProperty
from sqlalchemy.orm.properties import ColumnProperty
from flexflow.domains.entities import entities as ent
from flexflow.domains import utils
        
class DomainRepo:
    '''bridge between domain entities  and storage layer
    allows creation of domain objects from list of dictionaries
    and allows all CURD operation
    ''' 
    sql_obJ_map = {"Wfstatus": sqlm.Wfstatus,
                   "Doctype": sqlm.Doctype,
                   "Wfaction": sqlm.Wfaction,
                   "Wfdoc": sqlm.Wfdoc,
                   "Datadocfield": sqlm.Datadocfield,
                   "Wfdocaudit": sqlm.Wfdocaudit,
                   "Holddoc": sqlm.Holddoc,
                   "Draftdata": sqlm.Draftdata
                   }
    
    domain_obj_map = {"Wfstatus": ent.Wfstatus,
                      "Doctype": ent.Doctype,
                      "Wfaction": ent.Wfaction,
                      "Wfdoc": ent.Wfdoc,
                      "Datadocfield": ent.Datadocfield,
                      "Wfdocaudit": ent.Wfdocaudit,
                      "Holddoc": ent.Holddoc,
                      "Draftdata": ent.Draftdata,
                   }
    
    def __init__(self, objname:str, dbdriver=sqlm.dbdriver):        
        self.dbdriver = dbdriver        
        if self.sql_obJ_map.get(objname):
            self.sql_obj = self.sql_obJ_map.get(objname)
            self.domain_obj = self.domain_obj_map.get(objname)
        else:
            raise rexc.InvalidWorkflowObject(objname, ','.join(self.sql_obJ_map.keys()))
        
    def insert_bulk_mapping(self, data_lod:list):
        self._validate_input_data_lod(data_lod)
        db_save_result = self.dbdriver.insert_bulk(self.sql_obj, data_lod)
        return db_save_result
    
    def add_form_lod(self, data_lod:list):
        data_lod = utils.sanitize_lod(data_lod)
        self._validate_input_data_lod(data_lod)
        data_lobj = self._convert_lod_to_lobj(data_lod)
        db_save_result = self.dbdriver.add_from_lobj(data_lobj)
        return db_save_result
    
    def add_list_of_domain_obj(self, list_of_domain_obj):
        data_lod =[]
        for domain_obj in list_of_domain_obj:
            data_lod.append(domain_obj.to_dict())
        result = self.add_form_lod(data_lod)
        return result
        
    def list_domain_obj(self, **search_filters):        
#         lod = self.dbdriver.list_as_dict(self.sql_obj, **search_filters)
        lod = self.list_dict(**search_filters)
        result = [self._create_domain_object(d) for d in lod]    
        return result
    
    def list_dict(self, **search_filters):
        self._validate_input_data_dict(search_filters)
        search_filter_dict_to_obj = self._convert_relational_text_to_obj_in_dict(search_filters)
        lod = self.dbdriver.list_as_dict(self.sql_obj, **search_filter_dict_to_obj)
        return lod
    
    def list_json(self, **search_filters):
        lod = self.list_dict(**search_filters)
        for d in lod:
            if '_sa_instance_state' in d:
                d.pop('_sa_instance_state')
        return json.dumps(lod)
    
    def list_obj(self, **search_filters):
        '''returns as iterator'''
        self._validate_input_data_dict(search_filters)
        obj = self.dbdriver.list_as_obj(self.sql_obj, **search_filters)
        return obj
    
    def update_all_from_dict(self, updated_data_dict, **search_filters):
        ''' Danger : if no search_filter if provided it will change all the records '''
        self._validate_input_data_dict(updated_data_dict)
        dict_to_obj = self._convert_relational_text_to_obj_in_dict(updated_data_dict)
        result = self.dbdriver.update_all(self.sql_obj, dict_to_obj, **search_filters)
        return result
    
    def update_from_dict(self, updated_data_dict, **search_filters):
        ''' SAFE : if no search_filter if provided it will change only the first  records '''
        updated_data_dict = utils.sanitize_input_dict(updated_data_dict)
        self._validate_input_data_dict(updated_data_dict)
        dict_to_obj = self._convert_relational_text_to_obj_in_dict(updated_data_dict)
        result = self.dbdriver.update(self.sql_obj, dict_to_obj, **search_filters)
        return result
    
    def delete(self, **search_filters):
        self._validate_input_data_dict(search_filters)
        delete_result = self.dbdriver.delete(self.sql_obj, **search_filters)
        return delete_result
    
    def get_wfmobj_keys(self):
        obj_named_dict =  inspect.getfullargspec(self.domain_obj)
        #print(obj_named_dict)
        for i, arg   in enumerate(obj_named_dict.args):
            if arg == 'self' or arg.startswith('__') and arg.endswith('__'):
                print('poping ........', arg)
                obj_named_dict.args.pop(i)
        #print('after pop .......', obj_named_dict.args)
        #########this block may not be required###
        if hasattr(obj_named_dict, "keywords") and not obj_named_dict.keywords == "kwargs":
            for kwd in obj_named_dict.keywords:
                if kwd : obj_named_dict.args.append(kwd)
        #print( 'after adding keywords ...')
        #############################################
        return obj_named_dict.args
    
    def _create_domain_object(self, status_dict:dict):
        return self.domain_obj.from_dict(status_dict)
    
    def _validate_input_data_lod(self, input_data_lod):
        data_lod = input_data_lod        
        if not isinstance(input_data_lod, list):
            raise rexc.InvalidInputDataList
        #data_lod = utils.sanitize_lod(input_data_lod)
        for data_dict in data_lod:
            self._validate_input_data_dict(data_dict)
            
    def _validate_input_data_dict(self, input_data_dict):
        data_dict = input_data_dict                
        if not isinstance(input_data_dict, dict):
            raise rexc.InvalidInputDataDict
        for k in  data_dict.keys():
                if k not in  self.sql_obj.__dict__.keys():
                    obj_dict_copy = self.sql_obj.__dict__.copy()
                    pop_keys = [i for i in obj_dict_copy if '__' in i]
                    for j in pop_keys: obj_dict_copy.pop(j)
                    if '_sa_class_manager' in obj_dict_copy: obj_dict_copy.pop('_sa_class_manager')
                    if 'id' in obj_dict_copy: obj_dict_copy.pop('id')                 
                    raise rexc.InvalidKeysInData(k, obj_dict_copy.keys())
                
    def _convert_lod_to_lobj(self, lod: list):
        lobj = []
        for data_dict in lod:
            dict_to_obj = self._convert_relational_text_to_obj_in_dict(data_dict)
            #convert the non relational also to obj
            dict_to_obj = self.sql_obj(**data_dict)#convert the data_dict as parameter to class object
            lobj.append(dict_to_obj) #add  the object to the list, items in new list is class object replacing the earlier dictionary items
        return  lobj    
        
    def _convert_relational_text_to_obj_in_dict(self, data_dict): 
        for k, v  in data_dict.items():
            attr = getattr(self.sql_obj, k)
            attr_property = attr.property
            if  isinstance(attr_property, RelationshipProperty): #otherwise isinstance(attr_property, ColumnProperty):
                attr_target = attr_property.target #<class 'sqlalchemy.sql.schema.Table'> doctype,  #print(type(attr_target), attr_target) #target itself is  the table
                related_class_name = attr_target.__str__().capitalize()  #All sqlobj class must be Only the first letter as Capital, all other small
                realted_class_object = self.sql_obJ_map.get(related_class_name)
                if not (isinstance(v, dict) or isinstance(v, realted_class_object) ):
                    raise rexc.InvalidObjTypeInInputParam(k, dict)
                if  isinstance(v, dict):
                    local_remote_pair = attr_property.local_remote_pairs[0]  #here assumption is this attribute of the class have only on local_remote_pair
                    #could there be a case where there are multiple ?
                    _, remote_obj = local_remote_pair
                    primary_key_of_related_obj = remote_obj.name                
                    if not primary_key_of_related_obj in v:
                        raise rexc.PrimaryKeyNotPresentInSearch(primary_key_of_related_obj, v)
                    search_value = v.get(primary_key_of_related_obj)
                    search_filter_for_related_obj = {primary_key_of_related_obj: search_value}
                    row_obj_qset = self.dbdriver.list_as_obj(realted_class_object, **search_filter_for_related_obj)
                    row_obj_list = [obj for obj in row_obj_qset]
                    if row_obj_list: 
                        row_obj = row_obj_list[0] #replace the value of the relationship based key to actual object
                        data_dict.update({k: row_obj})
                elif isinstance(v, realted_class_object):
                    data_dict.update({k: v})
        return data_dict
        
    