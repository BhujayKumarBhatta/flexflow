import json
from flexflow.configs import testconf
from flask_testing import TestCase as FTestCase
import flexflow
from flexflow.dbengines.sqlchemy import models as m, SqlalchemyDriver
from sqlalchemy import exc
from flexflow.domains import repos
from flexflow.restapi.routes import bp1
from flexflow.domains.repos import DomainRepo
from flexflow.domains.entities import entities as ent
from flexflow.domains.domainlogics.workflow import Workflow
from flexflow.exceptions import rules_exceptions  as rexc


        
app = flexflow.create_app(config_map_list = [testconf.yml, testconf.test_db_conf],
                          blue_print_list = [bp1,])
        
class Tflask(FTestCase):
    
    def create_app(self):       
#         app.config.from_object('app1.configs.testconfigs.TestConfig')
        app.config['TESTING'] = True
        app.config['LIVESERVER_PORT'] = 0
        return app
        
    
    
    def test_entities(self):
        m.dbdriver.delete(m.Holddoc) 
        m.dbdriver.delete(m.Wfdocaudit) 
        m.dbdriver.delete(m.Wfdoc) 
        m.dbdriver.delete(m.Wfaction)
        m.dbdriver.delete(m.Wfstatus)
        m.dbdriver.delete(m.Datadocfield)
        m.dbdriver.delete(m.Doctype)                     
        docrepo = DomainRepo("Wfdoc")
        ###########REGISTER DOCTYPE
        doctype1 = ent.Doctype("doctype1", "dk1", ["r1"])
        doctype2 = ent.Doctype("doctype2", "dk2",  ["r1"])
        lodobj = [doctype1, doctype2]
        doctype_repo = DomainRepo("Doctype")  
        msg = doctype_repo.add_list_of_domain_obj(lodobj)
        self.assertTrue(msg['message'] == "has been registered" )
        ########REGISTER ACTION RULES        
        wfaction1_dict=  {"name": "wfaction1",
                         "associated_doctype": {"name": "doctype1"},
                         "need_prev_status": "s0",
                         "need_current_status": "s1",
                         "leads_to_status": "s2",
                         "permitted_to_roles": ["r1",],
                         "hide_to_roles": ["r5",]
                         }
        wfaction2_dict=  {"name": "wfaction2",
                         "associated_doctype": {"name": "doctype2"},
                         "need_prev_status": "s1",
                         "need_current_status": "s2",
                         "leads_to_status": "s3",
                         "permitted_to_roles": ["r2",],
                         "hide_to_roles": ["r5",]
                         }
        wfaction3_dict=  {"name": "wfaction3",
                         "associated_doctype": {"name": "doctype2"},
                         "need_prev_status": "s2",
                         "need_current_status": "s3",
                         "leads_to_status": "s4",
                         "permitted_to_roles": ["r3",],
                         "hide_to_roles": ["r5",]
                         }
        wfaction1 = ent.Wfaction.from_dict(wfaction1_dict)
        wfaction2 = ent.Wfaction.from_dict(wfaction2_dict)
        wfaction3 = ent.Wfaction.from_dict(wfaction3_dict)
        lodobj = [wfaction1, wfaction2, wfaction3]
        action_repo = DomainRepo("Wfaction")
        msg = action_repo.add_list_of_domain_obj(lodobj)
        self.assertTrue(msg['message'] == "has been registered" )
        ############RETRIEVE ACTION1 FROM REPO
        doctype_list_sobj = doctype_repo.list_obj()
        self.assertTrue(isinstance(doctype_list_sobj[0], m.Doctype ))
        doctype_list_dobj = doctype_repo.list_domain_obj()
        self.assertTrue(isinstance(doctype_list_dobj[0], ent.Doctype ))
        action_list_dict = action_repo.list_dict()
        self.assertTrue( isinstance(action_list_dict[0]['associated_doctype'], dict))
        action_list_sobj = action_repo.list_obj()
        self.assertTrue( isinstance(action_list_sobj[0], m.Wfaction))
        action_list_dobj= action_repo.list_domain_obj()
        self.assertTrue( isinstance(action_list_dobj[0], ent.Wfaction))
        seearchf = {"associated_doctype": {"name": "doctype2"}}
        action_list_filtered_by_doctype = action_repo.list_domain_obj(**seearchf)
        self.assertTrue(action_list_filtered_by_doctype[0].associated_doctype.name == 'doctype2')
        self.assertTrue(action_list_filtered_by_doctype[1].associated_doctype.name == 'doctype2')
        ####UPDATE RELATTIONSHIP FIELD ACTION1 DOCTYPE FROM 1 TO 2 
        wfaction1_dict.update( 
            { "associated_doctype": {"name": "doctype2"} } )
        searchf = {"name": "wfaction1"}
        msg = action_repo.update_from_dict(wfaction1_dict, **searchf)
        self.assertTrue(msg['status'] == "success")
        action_list_filtered_by_doctype = action_repo.list_domain_obj(**seearchf)
        self.assertTrue(len(action_list_filtered_by_doctype) == 3)
        ####DEFINING FIELDS FOR DOCTYPE2
        f1_dict = {"name": "field1",
                   "associated_doctype": {"name": "doctype2"},
                   "ftype": "str",
                   "flength": 2,
                   "status_needed_edit": ["s3"]}
        f2_dict = {"name": "field2",
                   "associated_doctype": {"name": "doctype2"},
                   "ftype": "int",
                   "flength": 2,
                   "status_needed_edit": [""]}
        docf_repo = repos.DomainRepo("Datadocfield")
        msg = docf_repo.add_form_lod([f1_dict, f2_dict])
        self.assertTrue(msg['status'] == "success" )
        datadocfields_repo = repos.DomainRepo("Datadocfield")
        searh_filter = {"associated_doctype": {"name": "doctype2"} }
        result = datadocfields_repo.list_domain_obj(**searh_filter)
        fnames = [item.name for item in result]
        self.assertTrue("field1" in fnames)
        ###CHECK THE ID ATTRIBUTE FROM SQL OBJ HAS BEEN PASSED TO DOMAINOBJ
        #self.assertTrue(hasattr(action_list_filtered_by_doctype[0], 'id'))
        doc_data1 = {"field1": "v1", "field2": 10}
        primval_datadoc = doc_data1["field1"]
        wfdoc_dict1 = {"name": primval_datadoc,
                       "associated_doctype": {"name": "doctype2"},
                         "prev_status": "s2",
                         "current_status": "s3",
                         "doc_data": doc_data1,
                         }
        wfdoc_lod = [wfdoc_dict1]
        wfdoc_repo = repos.DomainRepo("Wfdoc")
        msg = wfdoc_repo.add_form_lod(wfdoc_lod)
        #######RETRIEVE DOC USING PRIMKEY
        wfdoc_list = wfdoc_repo.list_domain_obj(**{"name": "v1"})
        ##########SEE THE COMNNETS above IN CASE OF INPUT TYPE EXCEPTION       
        self.assertTrue(len(wfdoc_list[0].wfactions) == 3)
        self.assertTrue((wfdoc_list[0].doc_data == doc_data1))
        #####FROM DICT CREATE DOMAIN OBJ AND THEN SAVE TO REPO
        doc_data1 = {"field1": "v2", "field2": 10}
        primval_datadoc = doc_data1["field1"]
        wfdoc_dict2 = {"name": primval_datadoc,
                       "associated_doctype": {"name": "doctype2"},
                         "prev_status": "s2",
                         "current_status": "s3",
                         "doc_data": doc_data1,
                         }
        wfdoc2 = ent.Wfdoc.from_dict(wfdoc_dict2)
        ###ADD THE DOMAIN OBJECT TO THE DOMAIN REPO
        msg = wfdoc_repo.add_list_of_domain_obj([wfdoc2])
        self.assertTrue(msg['message'] == "has been registered" )        
        ###SEE DOCTYPE2 HAVE THE DOCDATAFIELDS
        doctype2Obj_list = doctype_repo.list_domain_obj(**{"name": "doctype2"})
        ###CREATE DOC ONCE ITS FIELDS ARE DEFINED ABOVE        
        doc_data3 = {"field1": "v3", "field2": 10 }
        wfdoc_dict3 = {"name": 'v3',
                       "associated_doctype": {"name": "doctype2"},
                       "prev_status": "",
                       "current_status": "Created",
                       "doc_data": doc_data3,
                        }
        ###FAIL FOR FIELD NAME MISTACH
        try:
            ent.Wfdoc.from_dict(wfdoc_dict3)
        except rexc.UnknownFieldNameInDataDoc as e:
            self.assertTrue(e.status == "UnknownFieldNameInDataDoc")
        ##FAILURE FOR FIELD LENGTH LARGER THAN CONFIGURED
        doc_data3 = {"field1": "v44444" , "field2": 10}
        wfdoc_dict3.update({"doc_data": doc_data3})
        try:
            ent.Wfdoc.from_dict(wfdoc_dict3)
        except rexc.DataLengthViolation as e:
            self.assertTrue(e.status == "DataLengthViolation")
        ####FAIL FOR FIELD TYPE, FIELD2 SHOULD BE INT TYPE        
        wfdoc_dict3.update({"name": "v3", "doc_data": {"field1": "v3", "field2": "v2"}})
        try:
            ent.Wfdoc.from_dict(wfdoc_dict3)
        except rexc.DataTypeViolation as e:
            self.assertTrue(e.status == "DataTypeViolation")
        ###########CHECK SUCCESS
        wfdoc_dict3.update({"name": "v3", "doc_data": {"field1": "v3", "field2": 10}})
        docobj = ent.Wfdoc.from_dict(wfdoc_dict3)
        self.assertTrue(docobj.name == "v3")
         
   