import json
from flexflow.exceptions import rules_exceptions  as rexc
from flexflow.domains import repos 
from flexflow.domains.entities import Entities
from sqlalchemy.orm.relationships import RelationshipProperty

class Wfstatus(Entities):
    '''workflow status master'''
    
    def __init__(self, name):
        self.name = name

class Doctype(Entities):
    
    def __init__(self, name):
        self.name = name 
        
class Wfaction(Entities):
    
    related_obj_map = {"assocated_doctype": {"mapped_object": Doctype, "primary_key": "name"},
                             }
    
    def __init__(self, name:str, assocated_doctype:Doctype,                 
                 need_prev_status:str, need_current_status:str,
                 leads_to_status:str, permitted_to_roles:list ):
        
        self.name = name        
        self.assocated_doctype = assocated_doctype
        self.need_prev_status = need_prev_status
        self.need_current_status = need_current_status
        self.leads_to_status = leads_to_status
#         if not isinstance(assocated_doctype, Doctype): 
#             raise rexc.InvalidObjTypeInInputParam("permitted_to_roles", list )
        self.permitted_to_roles = permitted_to_roles
        #self.repo = repos.DomainRepo(self.__class__.__name__)#ensure storage level class name is same as emtities class name
        self._validate_param_values()
        
    @property
    def assocated_doctype_name(self):
        return self.assocated_doctype.name
    
    def to_dict_with_pkey_for_relationship(self):
        return {"name": self.name, 
                "assocated_doctype": self.assocated_doctype,
                "need_prev_status": self.need_prev_status,
                "need_current_status": self.need_current_status,
                "leads_to_status": self.leads_to_status,
                "permitted_to_roles": self.permitted_to_roles
                }
        
    def _convert_relational_text_to_obj_in_dict(self, data_dict): 
        for k, v  in data_dict.items():
            attr = getattr(self.sql_obj, k)
            attr_property = attr.property
            if  isinstance(attr_property, RelationshipProperty): #otherwise isinstance(attr_property, ColumnProperty):
                attr_target = attr_property.target #<class 'sqlalchemy.sql.schema.Table'> doctype,  #print(type(attr_target), attr_target) #target itself is  the table
                related_class_name = attr_target.__str__().capitalize()  #All sqlobj class must be Only the first letter as Capital, all other small
                realted_class_object = self.sql_obJ_map.get(related_class_name)
                local_remote_pair = attr_property.local_remote_pairs[0]  #here assumption is this attribute of the class have only on local_remote_pair
                #could there be a case where there are multiple ?
                _, remote_obj = local_remote_pair
                primary_key_of_related_obj = remote_obj.name
                search_filter_for_related_obj = {primary_key_of_related_obj: v}
                row_obj_qset = self.dbdriver.list_as_obj(realted_class_object, **search_filter_for_related_obj)
                row_obj_list = [obj for obj in row_obj_qset]
                if row_obj_list: 
                    row_obj = row_obj_list[0] #replace the value of the relationship based key to actual object
                    data_dict.update({k: row_obj})
        return data_dict
        
        
class Wfdoc(Entities):
    
    def __init__(self, assocated_doctype:Doctype, prev_status:str, current_status:str, doc_data:dict):
        self.assocated_doctype = assocated_doctype
        self.prev_status = prev_status
        self.current_status = current_status
        self.doc_data = doc_data
        
    @property
    def assocated_doctype_name(self):
        return self.assocated_doctype.name
    
    def to_dict(self):
        return {"assocated_doctype": self.assocated_doctype,
                "prev_status": self.prev_status,
                "current_status": self.current_status,
                "doc_data": self.doc_data}
        