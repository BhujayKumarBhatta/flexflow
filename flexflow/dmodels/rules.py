from flexflow.exceptions import rules_exceptions  as exc

class Status:
    '''Name of workflow status each has an associaltion with a doc_category
    which means the status is meant for a particular document type'''
    
    def __init__(self, name, doc_category):
        self.name = name
        self.doc_category = doc_category
        
        
class StatusList(list):
    '''holds all the status as a list 
    '''    
    def __init__(self, doc_category):        
        self.doc_category = doc_category
        
    def append(self, *args, **kwargs):
        '''The doc_category attributes of this list must match 
    with the doc_category of each status object'''
        for item in args:
            if item.doc_category == self.doc_category:
                return list.append(self, *args, **kwargs)
            else:
                raise exc.InvalidDocCategory(item.doc_category, self.doc_category)
        
    