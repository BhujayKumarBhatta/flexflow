from datetime import datetime
import uuid
from sqlalchemy.dialects.mysql import JSON
from flexflow.dbengines.sqlchemy import SqlalchemyDriver
from pip._internal import self_outdated_check

dbdriver = SqlalchemyDriver()
db = dbdriver.db
migrate = dbdriver.migrate
dt_str_fmt = '%d-%m-%Y'
# from db import Models , Column , Integer, String, DateTime


# status_to_doc_map = db.Table('status_to_doc_map',
#     db.Column('wfstatus_id', db.Integer, db.ForeignKey('wfstatus.id'), primary_key=True),
#     db.Column('doccategory_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
# )


class Wfstatus(db.Model):
    #id = db.Column(db.String(200), primary_key=True)
    name = db.Column(db.String(120), primary_key=True, unique=True, nullable=False)
    
    def to_dict(self):
        return {"name": self.name}
        
    
class Doctype(db.Model):
    #id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), primary_key=True, unique=True, nullable=False)
    primkey_in_datadoc = db.Column(db.String(120),nullable=False) 
    #one to many: -     
    #Because relationships are declared before they are established you can use strings to refer to classes that are not created yet (for instance if Doctype defines a relationship to WFAction which is declared later in the file).
    #the foreign key will be declared in the WFAction class , doctype_id = db.Column(db.Integer, db.ForeignKey('doctype.id'))
    #actionrules = db.relationship('WFAction', backref='doctype')
    #In this case we will use many to one , that is from WFAction class we will create the relationship
    def to_dict(self):
        return {"name": self.name,
                "primkey_in_datadoc": self.primkey_in_datadoc}

   
class Datadocfield(db.Model):    
        name = db.Column(db.String(120), primary_key=True, unique=True, nullable=False)
        associated_doctype = db.relationship('Doctype', backref='datadocfields')
        associated_doctype_name = db.Column(db.String(120), db.ForeignKey('doctype.name'))
        ftype = db.Column(db.String(120), nullable=False)
        flength = db.Column(db.Integer, nullable=False)
        status_needed_edit = db.Column(JSON)
        
        def to_dict(self):
            return {"name": self.name,
                    "associated_doctype": {"name": self.associated_doctype.name},
                    "associated_doctype_name": self.associated_doctype_name,
                    "ftype": self.ftype,
                    "flength": self.flength,
                    "status_needed_edit": self.status_needed_edit
                }
            
 
class Wfaction(db.Model):
    #id = db.Column(db.Integer, primary_key=True)    
    name = db.Column(db.String(120), primary_key=True, unique=True, nullable=False)
    #many to one - place both foreign key  id and relationship in the "Many side" of the relationship
    associated_doctype = db.relationship('Doctype', backref='wfactions')
    associated_doctype_name = db.Column(db.String(120), db.ForeignKey('doctype.name'))
    ###########       
    need_prev_status = db.Column(db.String(120), nullable=False)    
    ####################
    need_current_status = db.Column(db.String(120), nullable=False)    
    ####################
    leads_to_status = db.Column(db.String(120), nullable=False)    
    #############
    permitted_to_roles = db.Column(JSON)
    
    def to_dict(self):
        return {"name": self.name, 
                "associated_doctype": {"name": self.associated_doctype.name},
                "associated_doctype_name": self.associated_doctype_name,
                "need_prev_status": self.need_prev_status,
                "need_current_status": self.need_current_status,
                "leads_to_status": self.leads_to_status,
                "permitted_to_roles": self.permitted_to_roles}
    

class Wfdoc(db.Model):
    name = db.Column(db.String(500), primary_key=True, unique=True, nullable=False)
    #many to one - place both foreign key  id and relationship in the "Many side" of the relationship
    associated_doctype = db.relationship('Doctype', backref='wfdocs')
    associated_doctype_name = db.Column(db.String(120), db.ForeignKey('doctype.name'))
    #associated actions = wfdoc.associated_doctype.wfactions   
    prev_status = db.Column(db.String(120))
    current_status = db.Column(db.String(120))
    #allowed_next_action is filter the assocated_actions by prev and current_status
    ## we should compute the allowed actions, 
    doc_data = db.Column(JSON)
    
    def to_dict(self):
        return {"name": self.name,
                "associated_doctype": {"name": self.associated_doctype.name},
                "associated_doctype_name": self.associated_doctype_name,
                "prev_status": self.prev_status,
                "current_status": self.current_status,
                "doc_data": self.doc_data}
        

class Wfdocaudit(db.Model):
    name = db.Column(db.String(500), primary_key=True, unique=True, nullable=False)
    wfdoc = db.relationship('Wfdoc', backref='wfdocaudit')
    wfdoc_name = db.Column(db.String(120), db.ForeignKey('wfdoc.name'))
    username = db.Column(db.String(120))
    email = db.Column(db.String(120))
    time_stamp = db.Column(db.String(120))
    client_address = db.Column(db.String(120))
    org = db.Column(db.String(120))
    orgunit = db.Column(db.String(120))
    department = db.Column(db.String(120))
    action = db.Column(db.String(120))
    roles = db.Column(JSON)
    data = db.Column(JSON)
    
    def to_dict(self):
        return {"name": self.name,
                "wfdoc": {"name": self.wfdoc.name},
                "wfdoc_name": self.wfdoc_name,
                "username": self.username,
                "email": self.email,
                "time_stamp": self.time_stamp,
                "client_address": self.client_address,
                "org": self.org,
                "orgunit": self.orgunit,
                "department": self.department,
                "action": self.action,
                "roles": self.roles,
                "data": self.data }
                
        
    
    