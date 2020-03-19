got the value from msg value before decoding ....
printing masg ...........................: 
{'wfcdict': {'username': 'TATAUSER3', 'roles': 'null', 'email': 'TATAUSER3@tata.com', 'org': 'TATA', 'name': 'TATAWFC', 'client_address': '10.174.112.134', 'orgunit': 'TATAOU', 'time_stamp': '10-01-2020 08:14:59', 'request_id': '04dd4a37-4c69-4a47-95a3-a5b405da126a', 'department': 'TSPDEPT'}, 
'stage2_candidates': [{'CustomerID': 'XI000555', 'AccountNo': 'XDN043451', 'Speed': '20 Mbps', 'ServiceType': 'GXDN', 'PremiseName': '5245', 'ARC': '765500', 'Total': 12234, 'InvoiceNo': 'TCL00102', 'InvoiceDate': '15-03-2019', 'BillingDateTO': '01-03-2019', 'SLNo': 2, 'City': 'Gujrat', 'Action': 'CREATE', 'Division': 'ABD', 'InfoID': 'S0000000009', 'FullSiteAddress': '65 Hempstead Turnpike, East Meadow NY 11554', 'SiteID': '5245', 'TSP': 'TATA', 'PIN': 5245, 'CustomerName': 'ITC', 'REMARKS': 'OK', 'TaxName': ' GErmany SGST SGST@9%+CGST@9%', 'PremiseNo': '5245', 'GSTNo': '08KJHLHLHLH88879', 'State': 'KA', 'CircuitID': 'LJLKJKJKGJ545425', 'BillingDateFrom': '02-04-2018'}], 
'request_id': '04dd4a37-4c69-4a47-95a3-a5b405da126a', 
'msg_source': 'paperhouse', 
'response_list': [{'invoice_num': 'TCL00101', 
                   'roll_back_event': True, 
                   'save_status': "ValidationError (Invoice:None) (state.String value is too long: ['xldata'])", 
                   'org': 'TATA', 'event_id': 'd667e320-8c67-4c3e-9d43-0abebce567c9'}, 
                   
                {'invoice_num': 'TCL00102', 
                 'inv': {'status': 'InvoiceCreated', 
                         'xldata': {'remarks': 'OK', 'invoiceno': 'TCL00102', 'city': 'Gujrat', 'tsp': 'TATA', 'circuitid': 'LJLKJKJKGJ545425', 'total': 12234, 'gstno': 'None', 'infoid': 'S0000000009', 'siteid': '5245', 'taxname': ' GErmany SGST SGST@9%+CGST@9%', 'servicetype': 'GXDN', 'fullsiteaddress': '65 Hempstead Turnpike, East Meadow NY 11554', 'action': 'CREATE', 'division': 'ABD', 'arc': '765500', 'billingdateto': '01-03-2019', 'slno': 2, 'accountno': 'XDN043451', 'premiseno': '5245', 'customerid': 'XI000555', 'pin': 5245, 'state': 'KA', 'billingdatefrom': '02-04-2018', 'customername': 'ITC', 'premisename': '5245', 'invoicedate': '15-03-2019', 'speed': '20 Mbps'}, 'invoiceno': 'TCL00102'}, 
                 'org': 'TATA', 
                 'save_status': 'created', 
                 'event_id': 'd05e9aec-3084-4a39-8be9-79f82a8ceb2a'}, 
                
                {'invoice_num': 'TCL00103', 'roll_back_event': True, 'save_status': "ValidationError (Invoice:None) (state.String value is too long: ['xldata'])", 'org': 'TATA', 'event_id': '4cf10b84-6e8d-4601-adce-62b0d17febf7'}, {'invoice_num': 'TCL00104', 'roll_back_event': True, 'save_status': "ValidationError (Invoice:None) (state.String value is too long: ['xldata'])", 'org': 'TATA', 'event_id': 'adb5c435-2dc1-44f2-b8c0-e9e21ac4a206'}]}
message received from paperhouse
reached beffore calling triggermail .........
invalid msg format from kafka, the error is  'inv'


got the value from msg value before decoding ....
printing masg ...........................: {'wfcdict': {'username': 'TATAUSER3', 'roles': 'null', 'email': 'TATAUSER3@tata.com', 'org': 'TATA', 'time_stamp': '10-01-2020 08:14:59', 'client_address': '10.174.112.134', 'orgunit': 'TATAOU', 'name': 'TATAWFC', 'request_id': '04dd4a37-4c69-4a47-95a3-a5b405da126a', 'department': 'TSPDEPT'}, 'request_id': '04dd4a37-4c69-4a47-95a3-a5b405da126a', 'msg_source': 'paperhouse', 'response_list': [{'save_status': 'auto chk result updated', 'invoice': {'autochk': {'lnet_status': 'No link in lnet by the infoops id S0000000009', 'autocheck_status': 'Failed', 'inventory_status': 'No link in inventory by the infoops id S0000000009', 'bom_comp_result': []}, 'status': 'InvoiceCreated', '_id': {'$oid': '5e183284787b2bc9f2df232e'}, 'xldata': {'remarks': 'OK', 'invoiceno': 'TCL00102', 'city': 'Gujrat', 'tsp': 'TATA', 'circuitid': 'LJLKJKJKGJ545425', 'total': 12234, 'gstno': 'None', 'infoid': 'S0000000009', 'siteid': '5245', 'taxname': ' GErmany SGST SGST@9%+CGST@9%', 'servicetype': 'GXDN', 'fullsiteaddress': '65 Hempstead Turnpike, East Meadow NY 11554', 'action': 'CREATE', 'division': 'ABD', 'arc': '765500', 'billingdateto': '01-03-2019', 'slno': 2, 'accountno': 'XDN043451', 'premiseno': '5245', 'customerid': 'XI000555', 'pin': 5245, 'state': 'KA', 'billingdatefrom': '02-04-2018', 'customername': 'ITC', 'premisename': '5245', 'invoicedate': '15-03-2019', 'speed': '20 Mbps'}, 'invoiceno': 'TCL00102'}}]}
message received from paperhouse
reached beffore calling triggermail .........
invalid msg format from kafka, the error is  'inv'




HOW PAPERHOUSE IS PRODUCING abs(x)
==============================================
got a message from penman 
UpdateFromDraft:  False
after the invoice update the result is :  {'inv': {'invoiceno': 'TATA00106', 'status': 'InvoiceCreated', 'xldata': {'customerid': 'XI000555', 'siteid': '52454', 'invoiceno': 'TATA00106', 'premisename': '52454', 'pin': 52454, 'servicetype': 'GXDN', 'speed': '4 mbps', 'remarks': 'OK', 'taxname': 'USA SGST@9%+CGST@9%', 'total': 234455, 'state': 'KA', 'infoid': 'S0000000008', 'tsp': 'TATA', 'accountno': 'XDN038414', 'arc': '2400', 'slno': 111, 'division': 'ABD', 'invoicedate': '15-03-2019', 'billingdatefrom': '02-12-2018', 'city': 'Gujrat', 'gstno': 'None', 'circuitid': 'UploadCircuit', 'action': 'CREATE', 'billingdateto': '01-03-2019', 'fullsiteaddress': 'This looks like a good address', 'customername': 'ITC', 'premiseno': '52454'}}, 'save_status': 'created', 'invoice_num': 'TATA00106'}
{'response_list': [{'invoice_num': 'TATA00101', 'save_status': 'invalid event type None ', 'org': 'ITC', 'event_id': None, 'roll_back_event': True}, {'invoice_num': 'TATA00101', 'save_status': 'invalid event type None ', 'org': 'ITC', 'event_id': None, 'roll_back_event': True}, {'inv': {'invoiceno': 'TATA00105', 'status': 'InvoiceCreated', 'xldata': {'customerid': 'XI000555', 'siteid': '52454', 'invoiceno': 'TATA00105', 'premisename': '52454', 'pin': 52454, 'servicetype': 'GXDN', 'speed': '4 mbps', 'remarks': 'OK', 'taxname': 'USA SGST@9%+CGST@9%', 'total': 234455, 'state': 'KA', 'infoid': 'S0000000008', 'tsp': 'TATA', 'accountno': 'XDN038414', 'arc': '2400', 'slno': 111, 'division': 'ABD', 'invoicedate': '15-03-2019', 'billingdatefrom': '02-12-2018', 'city': 'Gujrat', 'gstno': 'None', 'circuitid': 'UploadCircuit', 'action': 'CREATE', 'billingdateto': '01-03-2019', 'fullsiteaddress': 'This looks like a good address', 'customername': 'ITC', 'premiseno': '52454'}}, 'save_status': 'created', 'org': 'TATA', 'event_id': '4a695f96-5875-4cde-99bf-669dcc43b89f', 'invoice_num': 'TATA00105'}, {'inv': {'invoiceno': 'TATA00106', 'status': 'InvoiceCreated', 'xldata': {'customerid': 'XI000555', 'siteid': '52454', 'invoiceno': 'TATA00106', 'premisename': '52454', 'pin': 52454, 'servicetype': 'GXDN', 'speed': '4 mbps', 'remarks': 'OK', 'taxname': 'USA SGST@9%+CGST@9%', 'total': 234455, 'state': 'KA', 'infoid': 'S0000000008', 'tsp': 'TATA', 'accountno': 'XDN038414', 'arc': '2400', 'slno': 111, 'division': 'ABD', 'invoicedate': '15-03-2019', 'billingdatefrom': '02-12-2018', 'city': 'Gujrat', 'gstno': 'None', 'circuitid': 'UploadCircuit', 'action': 'CREATE', 'billingdateto': '01-03-2019', 'fullsiteaddress': 'This looks like a good address', 'customername': 'ITC', 'premiseno': '52454'}}, 'save_status': 'created', 'org': 'TATA', 'event_id': '2b165d83-80c1-451c-9336-1a8195b7a4d0', 'invoice_num': 'TATA00106'}], 'wfcdict': {'username': 'TATAUSER3', 'client_address': '127.0.0.1', 'request_id': 'ffce607c-bd20-42b9-88cc-5c4fecd77599', 'orgunit': 'TATAOU', 'time_stamp': '13-01-2020 06:26:42', 'name': 'TATAWFC', 'department': 'TSPDEPT', 'org': 'TATA', 'email': 'TATAUSER3@tata.com', 'roles': 'null'}, 'request_id': 'ffce607c-bd20-42b9-88cc-5c4fecd77599', 'msg_source': 'paperhouse', 'stage2_candidates': [{'PremiseName': '52454', 'PIN': 52454, 'Speed': '4 mbps', 'SLNo': 111, 'CircuitID': 'UploadCircuit', 'ARC': '2400', 'SiteID': '52454', 'Division': 'ABD', 'State': 'KA', 'GSTNo': '09AAJJ888899N90', 'REMARKS': 'OK', 'Action': 'CREATE', 'City': 'Gujrat', 'InfoID': 'S0000000008', 'AccountNo': 'XDN038414', 'TSP': 'TATA', 'BillingDateFrom': '02-12-2018', 'PremiseNo': '52454', 'BillingDateTO': '01-03-2019', 'FullSiteAddress': 'This looks like a good address', 'Total': 234455, 'InvoiceDate': '15-03-2019', 'CustomerName': 'ITC', 'InvoiceNo': 'TATA00106', 'TaxName': 'USA SGST@9%+CGST@9%', 'ServiceType': 'GXDN', 'CustomerID': 'XI000555'}]}
topic_paperhouse
0
32

