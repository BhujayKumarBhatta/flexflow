from datetime import datetime
import uuid
from sqlalchemy.dialects.mysql import JSON
from flexflow.dbengines.sqlchemy import SqlalchemyDriver

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
    
    
class Doctype(db.Model):
    #id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), primary_key=True, unique=True, nullable=False)
    #one to many: -     
    #Because relationships are declared before they are established you can use strings to refer to classes that are not created yet (for instance if Doctype defines a relationship to WFAction which is declared later in the file).
    #the foreign key will be declared in the WFAction class , doctype_id = db.Column(db.Integer, db.ForeignKey('doctype.id'))
    #actionrules = db.relationship('WFAction', backref='doctype')
    #In this case we will use many to one , that is from WFAction class we will create the relationship
    
class Wfaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    #many to one - place both foreign key  id and relationship in the "Many side" of the relationship
    assocated_doctype = db.relationship('Doctype', backref='wfactions')
    assocated_doctype_name = db.Column(db.String(120), db.ForeignKey('doctype.name'))
    ###########       
    need_prev_status = db.Column(db.String(120), nullable=False)    
    ####################
    need_current_status = db.Column(db.String(120), nullable=False)    
    ####################
    leads_to_status = db.Column(db.String(120), nullable=False)    
    #############
    permitted_to_roles = db.Column(JSON)
    

    