import os
from unittest import TestCase
from flask_testing import TestCase as FTestCase
from flexflow.domains.xloder.uploader import XLReceiver
from flexflow.domains.xloder.excelchecker import ExcelChecker
from flexflow.configs.testconf import yml, testconf, testwfc, test_data_path, test_db_conf
test_file = os.path.join(test_data_path, 'sample_inv_upload_v2.xlsx')

from flexflow.dbengines.sqlchemy import models as m
from flexflow.domains.repos import DomainRepo
from flexflow.domains.entities import entities as ent
import flexflow
from flexflow.restapi.routes import bp1

l1 = ['file extention check passed', 'check_no_empty_cell_within_data_area=passed', 
 'check_within_max_row=passed', 'check_cloumn_heading=passed', 
 'check_no_duplicate_invoice_no=passed', 'check_tsp_name=passed'
      ]

app = flexflow.create_app(config_map_list = [yml, test_db_conf],
                          blue_print_list = [bp1,])

class TestUpload(FTestCase):
    
    def create_app(self):       
#         app.config.from_object('app1.configs.testconfigs.TestConfig')
        app.config['TESTING'] = True
        app.config['LIVESERVER_PORT'] = 0
        return app
    
    def test_configs(self):
#         print(yml)
        pass
        
    def test_xlfile_path(self):        
        self.assertEqual(os.path.exists(test_file), True)      
          
    def test_file(self):
        testwfc.org = "TATA"
        c = ExcelChecker(yml, test_file, wfc=testwfc)
        c.check_all_checks()
        msgl = c.message_list
        self.assertTrue(c.message_list == l1)
        self.assertTrue(False not in c.check_result_list)
  
       
    def test_xlreceiver(self):
        testwfc.org = "TATA"
        xlr = XLReceiver(testconf, testwfc, xlfile=test_file)
        self.assertTrue(xlr.lower_key_dict)
        self.assertTrue(isinstance(xlr.lower_key_dict, list))
        self.assertTrue(isinstance(xlr.lower_key_dict[0], dict))
        
    
    def test_workers(self):       
        self._register_doctype_n_actions()
        from flexflow.domains.domainlogics import workers #to prevent circular dependency 
        rlist = workers.xl_upload(testconf, testwfc, 'tspinvoice', xlfile=test_file)
        self.assertTrue(d.get('status') == "success" for d in rlist)
        
    def _register_doctype_n_actions(self):
        m.dbdriver.delete(m.Draftdata)
        m.dbdriver.delete(m.Holddoc)
        m.dbdriver.delete(m.Wfdocaudit)
        m.dbdriver.delete(m.Wfdoc) 
        m.dbdriver.delete(m.Wfaction)
        m.dbdriver.delete(m.Wfstatus)
        m.dbdriver.delete(m.Datadocfield)
        m.dbdriver.delete(m.Doctype)        
        tspinvoice = ent.Doctype("tspinvoice", "InvoiceNo", ['role1'])        
        lodobj = [tspinvoice]
        doctype_repo = DomainRepo("Doctype")
        doctype_repo.add_list_of_domain_obj(lodobj)
        ####DEFINING FIELDS FOR tspinvoice
        InvoiceNo = {"name": "InvoiceNo",
                   "associated_doctype": {"name": "tspinvoice"},
                   "ftype": "str",
                   "flength": 25,
                   "status_needed_edit": ["", "NewBorn"],#this should be status not role
                   "wfc_filter": "",
                   "wfc_filter_to_roles": []} 
        Action = {"name": "Action",
                   "associated_doctype": {"name": "tspinvoice"},
                   "ftype": "str",
                   "flength": 25,
                   "status_needed_edit": [""],
                   "wfc_filter": "",
                   "wfc_filter_to_roles": []}
        TSP = {"name": "TSP",
                   "associated_doctype": {"name": "tspinvoice"},
                   "ftype": "str",
                   "flength": 25,
                   "status_needed_edit": [""],
                   "wfc_filter": "org",
                   "wfc_filter_to_roles": ['r1']}
        Division = {"name": "Division",
                   "associated_doctype": {"name": "tspinvoice"},
                   "ftype": "str",
                   "flength": 25,
                   "status_needed_edit": [""],
                   "wfc_filter": "ou",
                   "wfc_filter_to_roles": ['r3']}
        InfoID = {"name": "InfoID",
                   "associated_doctype": {"name": "tspinvoice"},
                   "ftype": "str",
                   "flength": 25,
                   "status_needed_edit": [""],
                   "wfc_filter": "",
                   "wfc_filter_to_roles": ['']}
        CircuitID = {"name": "CircuitID",
                   "associated_doctype": {"name": "tspinvoice"},
                   "ftype": "str",
                   "flength": 25,
                   "status_needed_edit": [""],
                   "wfc_filter": "",
                   "wfc_filter_to_roles": ['']}
        Speed = {"name": "Speed",
                   "associated_doctype": {"name": "tspinvoice"},
                   "ftype": "str",
                   "flength": 25,
                   "status_needed_edit": [""],
                   "wfc_filter": "",
                   "wfc_filter_to_roles": []}
        ARC = {"name": "ARC",
                   "associated_doctype": {"name": "tspinvoice"},
                   "ftype": "str",
                   "flength": 25,
                   "status_needed_edit": [""],
                   "wfc_filter": "",
                   "wfc_filter_to_roles": []}
        ServiceType = {"name": "ServiceType",
                   "associated_doctype": {"name": "tspinvoice"},
                   "ftype": "str",
                   "flength": 25,
                   "status_needed_edit": [""],
                   "wfc_filter": "",
                   "wfc_filter_to_roles": []}
        SiteID = {"name": "SiteID",
                   "associated_doctype": {"name": "tspinvoice"},
                   "ftype": "str",
                   "flength": 25,
                   "status_needed_edit": [""],
                   "wfc_filter": "",
                   "wfc_filter_to_roles": []}
        FullSiteAddress = {"name": "FullSiteAddress",
                   "associated_doctype": {"name": "tspinvoice"},
                   "ftype": "str",
                   "flength": 50,
                   "status_needed_edit": [""],
                   "wfc_filter": "",
                   "wfc_filter_to_roles": []}
        GSTNo = {"name": "GSTNo",
                   "associated_doctype": {"name": "tspinvoice"},
                   "ftype": "str",
                   "flength": 25,
                   "status_needed_edit": [""],
                   "wfc_filter": "",
                   "wfc_filter_to_roles": []}
        BillingDateFrom = {"name": "BillingDateFrom",
                   "associated_doctype": {"name": "tspinvoice"},
                   "ftype": "str",
                   "flength": 25,
                   "status_needed_edit": [""],
                   "wfc_filter": "",
                   "wfc_filter_to_roles": []}
        BillingDateTO = {"name": "BillingDateTO",
                   "associated_doctype": {"name": "tspinvoice"},
                   "ftype": "str",
                   "flength": 25,
                   "status_needed_edit": [""],
                   "wfc_filter": "",
                   "wfc_filter_to_roles": []}
        InvoiceDate = {"name": "InvoiceDate",
                   "associated_doctype": {"name": "tspinvoice"},
                   "ftype": "str",
                   "flength": 25,
                   "status_needed_edit": [""],
                   "wfc_filter": "",
                   "wfc_filter_to_roles": []}
        TaxName = {"name": "TaxName",
                   "associated_doctype": {"name": "tspinvoice"},
                   "ftype": "str",
                   "flength": 25,
                   "status_needed_edit": [""],
                   "wfc_filter": "",
                   "wfc_filter_to_roles": []}
        Total = {"name": "Total",
                   "associated_doctype": {"name": "tspinvoice"},
                   "ftype": "int",
                   "flength": 25,
                   "status_needed_edit": [""],
                   "wfc_filter": "",
                   "wfc_filter_to_roles": []}
        REMARKS = {"name": "REMARKS",
                   "associated_doctype": {"name": "tspinvoice"},
                   "ftype": "str",
                   "flength": 100,
                   "status_needed_edit": [""],
                   "wfc_filter": "",
                   "wfc_filter_to_roles": []}
         
         
        docf_repo = DomainRepo("Datadocfield")
        docf_repo.add_form_lod([InvoiceNo,Action,TSP,Division,InfoID,
                                CircuitID,Speed,ARC,ServiceType,SiteID,
                                FullSiteAddress,GSTNo,BillingDateFrom,
                                BillingDateTO,InvoiceDate,TaxName,
                                Total,REMARKS])
        wfcaction_create = {"name": "Create",
                         "associated_doctype": {"name": "tspinvoice"},
                         #"need_prev_status": "NewBorn",
                         "need_current_status": ["NewBorn"],
                         "leads_to_status": "Created",
                         "permitted_to_roles": ["role1",],
                         "hide_to_roles": ["r7"],
                         "undo_prev_hide_for": [],
                         }
        wfaction1_dict=  {"name": "wfaction1",
                         "associated_doctype": {"name": "tspinvoice"},
                         #"need_prev_status": "NewBorn",
                         "need_current_status": ["Created"],
                         "leads_to_status": "s1",
                         "permitted_to_roles": ["r1",], 
                         "hide_to_roles": ["r4", "r5"],
                         "undo_prev_hide_for": [],
                         }
        wfaction2_dict=  {"name": "wfaction2",
                         "associated_doctype": {"name": "tspinvoice"},
                         #"need_prev_status": "Created",
                         "need_current_status": ["s1"],
                         "leads_to_status": "s2",
                         "permitted_to_roles": ["r2",],
                         "hide_to_roles": ["r5", "r6"],
                         "undo_prev_hide_for": ["r4",], #r4 hold doc shold be deleted but r5 to be retained
                         }
        wfaction3_dict=  {"name": "wfaction3",
                         "associated_doctype": {"name": "tspinvoice"},
                         #"need_prev_status": "s1",
                         "need_current_status": ["s2"],
                         "leads_to_status": "s3",
                         "permitted_to_roles": ["r3",],
                         "hide_to_roles": ["r1",],
                         "undo_prev_hide_for": ["r5", "r6"],
                         }
        wfaction4_dict=  {"name": "wfaction4",
                         "associated_doctype": {"name": "tspinvoice"},
                         #"need_prev_status": "s2",
                         "need_current_status": ["s3"],
                         "leads_to_status": "s4",
                         "permitted_to_roles": ["r3",],
                         "hide_to_roles": ["r5",],
                         "undo_prev_hide_for": [],
                         }
        wfactionCreate = ent.Wfaction.from_dict(wfcaction_create)
        wfaction1 = ent.Wfaction.from_dict(wfaction1_dict)
        wfaction2 = ent.Wfaction.from_dict(wfaction2_dict)
        wfaction3 = ent.Wfaction.from_dict(wfaction3_dict)
        lodobj = [wfactionCreate, wfaction1, wfaction2, wfaction3]
        action_repo = DomainRepo("Wfaction")
        action_repo.add_list_of_domain_obj(lodobj)
#         



        
          
        


