import json
from kafka import KafkaConsumer
from kafka.errors import KafkaError


class Klistener:
    def __init__(self, conf, Workflow):
        self.conf = conf
        self.ymlconf = conf.yml
        self.ks= self.ymlconf.get('kafka_servers')
        print(self.ymlconf.get('kafka_servers'))
        self.listener_group = 'invoiceflow-group_1'
        self.topics = ['topic_penman', 'topic_comparator', ]
        self.consumer = KafkaConsumer(
                                      bootstrap_servers=self.ymlconf.get('kafka_servers'),
                                      auto_offset_reset='earliest',
                                      enable_auto_commit=True,
                                      group_id=self.listener_group,
                                      )        
        self.consumer.subscribe(self.topics)
        self.Workflow = Workflow
        
    def _get_msg_n_trigger_action(self): 
        print(self.consumer)
        print(" Listener Group {} Listening for topics:"
              " {}".format(self.listener_group, self.topics))
        for message in self.consumer:
            msg = message.value
            try:
                msg = json.loads(msg.decode('utf-8'))            
                self._process_message(msg)
            except:
                print("invalid msg format, or error in processing ignoring this message")
                pass
            
    
    def _process_message(self, msg:dict):        
        ''' 
        input msg from kafka will be 
        {'request_id': 'hhihihhh-890809-jklkk;k-ytfty', 'wfcdict': {'time_stamp': '27-08-2019 14:08:44', 'department': 'dept1', 'email': 'user1@a.b', 'orgunit': 'ou1', 'roles': '["role1"]', 'name': 'wfc1', 'org': 'ITC', 'request_id': 'hhihihhh-890809-jklkk;k-ytfty', 'username': 'user1', 'client_address': '10.10.10.10'}, 'msg_source': 'EventGenerator', 'response_list': [{'eventdata': {'TaxName': 'USA SGST@9%+CGST@9%', 'FullSiteAddress': 'This looks like a good address', 'Action': 'CREATE', 'AccountNo': 'XDN038414', 'SiteID': '52454', 'InvoiceDate': '15-03-2019', 'REMARKS': 'OK', 'Total': 234455, 'PIN': 52454, 'InfoID': 'S0000000001', 'CircuitID': 'UploadCircuit', 'InvoiceNo': '1', 'SLNo': 1, 'Speed': '4 mbps', 'ServiceType': 'GXDN', 'TSP': 'TATA', 'CustomerName': 'ABC Limited', 'City': 'Gujrat', 'GSTNo': '09AAJJ888899N90', 'PremiseNo': '52454', 'PremiseName': '52454', 'BillingDateFrom': '02-12-2018', 'Division': 'POPCompany', 'CustomerID': 'XI000555', 'ARC': '2400', 'State': 'GG', 'BillingDateTO': '01-03-2019'}, 'event_name': 'InvoiceCreated', 'auditinfo': {'logged_in_user_dept': 'dept1', 'requestid': 'hhihihhh-890809-jklkk;k-ytfty', 'logged_in_user_email': 'user1@a.b', 'logged_in_user_org': 'ITC', 'logged_in_user_org_unit': 'ou1', 'api_call_time_stamp': {'$date': 1566914924182}, 'client_address': '10.10.10.10'}, 'invoiceno': '1', 'event_id': '4675b8c0-4f96-4cdd-97f9-7be2550edac5'}, {'message_source': 'EventGenerator'}, {'message_source': 'EventGenerator'}, {'eventdata': {'TaxName': 'Kunnur SGST@9%+CGST@9%', 'FullSiteAddress': '1 Washington Ave Extension, Albany NY 12205', 'Action': 'CREATE', 'AccountNo': 'XDN045164', 'SiteID': '95', 'InvoiceDate': '15-03-2019', 'REMARKS': 'OK', 'Total': 2345, 'PIN': 95, 'InfoID': 'S0000000004', 'CircuitID': 'KPK96334', 'InvoiceNo': '4', 'SLNo': 4, 'Speed': '11 Mbps', 'ServiceType': 'GXDN', 'TSP': 'TATA', 'CustomerName': 'ABC Limited', 'City': 'Nagpur', 'GSTNo': 'YYYY887766', 'PremiseNo': '95', 'PremiseName': '95', 'BillingDateFrom': '02-04-2018', 'Division': 'DIVISON1', 'CustomerID': 'XI000555', 'ARC': '76555', 'State': 'fdaf', 'BillingDateTO': '01-03-2019'}, 'event_name': 'InvoiceCreated', 'auditinfo': {'logged_in_user_dept': 'dept1', 'requestid': 'hhihihhh-890809-jklkk;k-ytfty', 'logged_in_user_email': 'user1@a.b', 'logged_in_user_org': 'ITC', 'logged_in_user_org_unit': 'ou1', 'api_call_time_stamp': {'$date': 1566914924182}, 'client_address': '10.10.10.10'}, 'invoiceno': '4', 'event_id': '0016f377-acb5-445f-b02f-6979f6040aeb'}]}
        
        output on kafka will be 
        {'msg_source': 'paperhouse', 'request_id': 'hhihihhh-890809-jklkk;k-ytfty', 'stage2_candidates': [{'Speed': '4 mbps', 'CustomerName': 'ABC Limited', 'PIN': 52454, 'ARC': '2400', 'TaxName': 'USA SGST@9%+CGST@9%', 'CustomerID': 'XI000555', 'Total': 234455, 'PremiseName': '52454', 'SiteID': '52454', 'TSP': 'TATA', 'Division': 'POPCompany', 'SLNo': 1, 'REMARKS': 'OK', 'CircuitID': 'UploadCircuit', 'InvoiceDate': '15-03-2019', 'City': 'Gujrat', 'BillingDateTO': '01-03-2019', 'ServiceType': 'GXDN', 'AccountNo': 'XDN038414', 'State': 'GG', 'BillingDateFrom': '02-12-2018', 'Action': 'CREATE', 'FullSiteAddress': 'This looks like a good address', 'InfoID': 'S0000000001', 'GSTNo': '09AAJJ888899N90', 'InvoiceNo': '1', 'PremiseNo': '52454'}, {'Speed': '11 Mbps', 'CustomerName': 'ABC Limited', 'PIN': 95, 'ARC': '76555', 'TaxName': 'Kunnur SGST@9%+CGST@9%', 'CustomerID': 'XI000555', 'Total': 2345, 'PremiseName': '95', 'SiteID': '95', 'TSP': 'TATA', 'Division': 'DIVISON1', 'SLNo': 4, 'REMARKS': 'OK', 'CircuitID': 'KPK96334', 'InvoiceDate': '15-03-2019', 'City': 'Nagpur', 'BillingDateTO': '01-03-2019', 'ServiceType': 'GXDN', 'AccountNo': 'XDN045164', 'State': 'fdaf', 'BillingDateFrom': '02-04-2018', 'Action': 'CREATE', 'FullSiteAddress': '1 Washington Ave Extension, Albany NY 12205', 'InfoID': 'S0000000004', 'GSTNo': 'YYYY887766', 'InvoiceNo': '4', 'PremiseNo': '95'}], 'wfcdict': {'org': 'ITC', 'username': 'user1', 'client_address': '10.10.10.10', 'email': 'user1@a.b', 'name': 'wfc1', 'orgunit': 'ou1', 'roles': '["role1"]', 'department': 'dept1', 'request_id': 'hhihihhh-890809-jklkk;k-ytfty', 'time_stamp': '27-08-2019 14:08:44'}, 'response_list': [{'org': 'TATA', 'save_status': 'created', 'invoice_num': '1'}, {'org': 'TATA', 'save_status': 'created', 'invoice_num': '4'}]}
        '''
        
        ''' segregating the message processing for ease of testing '''
        
        if msg.get('msg_source') == "comparator":
            print('got a message from Comparator ')
            try:
                result = self.get_autocheck_result_from_mq_and_update_invoice(msg)
            except Exception as e:
                result = str(e) 
                print(result)
        else:
            result = ("msg from unknown msg source: {} ".format(msg))
            print(result)
        return result
    
    def get_autocheck_result_from_mq_and_update_invoice(self, msg_fm_kafka):
        
        wf = self.Workflow('tspinvoice', wfc = msg_fm_kafka.get('wfcdict'))
        response_list = []
        for autochk_result in msg_fm_kafka.get('response_list'):
            invoiceno = autochk_result.get('invoiceno')
            if invoiceno:
                autochk_remarks = ("autocheck_status:  {} \n"
                           "inventory_status: {} \n"
                           "lnet_status: {} \n"
                           "billing_duration: {} \n"
                           "bill_to_status: {}\n"
                           "bill_to_msg: {}\n"
                           "bill_from_status: {}\n"
                           "bill_from_msg: {}").format(autochk_result.get('autocheck_status'),
                                                            autochk_result.get('inventory_status'),
                                                            autochk_result.get('lnet_status'),
                                                            autochk_result.get('billing_duration'),
                                                            autochk_result.get('bill_to_status'),
                                                            autochk_result.get('bill_to_msg'),
                                                            autochk_result.get('bill_from_status'),
                                                            autochk_result.get('bill_from_msg')
                                                            ) 
                
                result = wf.insert_autocheck_result(invoiceno, autochk_remarks)
            else:
                result = {"save_status": "could not find invoice %s" %invoiceno }
            response_list.append(result)
            print(response_list)
    



    
        
