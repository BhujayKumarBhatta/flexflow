from flexflow.domains.entities import entities as ent
from flexflow.domains.repos import DomainRepo
from flexflow.exceptions import rules_exceptions  as rexc

class Workflow:
    
    def __init__(self, doctype_name:str):
        self.doctype_name = doctype_name
    
    def create_doc(self, data:dict):
        ''' a key from the data is treated as the primary key for the 
        document. The key name is defined in the doctype.
        for creation of the doc the condition is no such doc by the id(primary key)
        exists in the repo.
        
        Also see wfdocObj initialization. Earlier we used to call the storage classes from sqlalchemy or mongoengine for creating the object, now we are using domain entities 
        '''
        doctyoeObj = self.get_doctype_obj_from_name()
        primkey_in_datadoc = doctyoeObj.primkey_in_datadoc
        if not data.get(primkey_in_datadoc):
            raise rexc.PrimaryKeyNotPresentInDataDict(primkey_in_datadoc)
        docid = data.get(primkey_in_datadoc)
        if self.get_wfdoc_by_id(docid):
            raise rexc.DuplicateDocumentExists(docid)
        ###earlier we used to call the storage classes from sqlalchemy or mongoengine for creating the object, now we are using domain entities 
        wfdocObj = ent.Wfdoc(id=docid,
                         assocated_doctype=doctyoeObj,
                         prev_status="",
                         current_status="Created",
                         doc_data=data)
        wfdoc_repo = DomainRepo("Wfdoc")
        msg = wfdoc_repo.add_list_of_domain_obj([wfdocObj])
        return msg
        
    def get_doctype_obj_from_name(self):
        '''search by primary key name, hence expected to get one object'''
        result = None
        search_dict = {"name": self.doctype_name}
        doctype_repo = DomainRepo("Doctype")
        lst = doctype_repo.list_domain_obj(**search_dict)
        if  len(lst) == 1 : result = lst[0]              
        return result
    
    def get_wfdoc_by_id(self, wfdoc_id):
        '''search by primary key id, hence expected to get one object'''
        result = None
        search_dict = {"id": wfdoc_id}
        wfdoc_repo = DomainRepo("Wfdoc")
        lst = wfdoc_repo.list_domain_obj(**search_dict)
        if  len(lst) == 1 : result = lst[0]              
        return result
        