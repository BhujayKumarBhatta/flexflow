from linkInventory.db.ldb.models import db, Lnetlink, Payment, Rate, Altaddress
from linkInventory.db import db_api 
from sqlalchemy import exc
import datetime
dt_str_fmt = '%d-%m-%Y'
current_date =   datetime.datetime.utcnow() + \
                   datetime.timedelta(hours=5, minutes=30) 

def add_rate(tsp, linktype, bandwidth, activity_type, otc, rate_per_year):
    rate = Rate(tsp=tsp, linktype=linktype, bandwidth=bandwidth, 
                activity_type=activity_type,
                otc=otc, rate_per_year=rate_per_year)
    msg = _register_record(rate)
    result =  {"rate": rate.to_dict(), "msg": msg}
    return result


def add_altaddress(prem_name, prem_no, state, city, pin ,
                   gstn, sgst_rate, cgst_rate):
    alt_address = Altaddress(prem_name=prem_name, prem_no=prem_no,
                             state=state, city=city, pin=pin,
                             gstn=gstn, sgst_rate=sgst_rate, cgst_rate=cgst_rate)
    print("have we got al_address model class %s" %alt_address)
    msg = _register_record(alt_address)    
    result =  {"alt_address": alt_address.to_dict(), "msg": msg}
    return result


def add_payment(invoice_id, billing_from, billing_to, 
                billing_type, amount, payment_date, mode, ref_no, 
                status, netlink_id):
    #TODO: search back the invoice in micros2 and ensure presense    
    try:
        b_form = datetime.datetime.strptime(billing_from, dt_str_fmt)
        b_to = datetime.datetime.strptime(billing_to, dt_str_fmt)
        p_date = datetime.datetime.strptime(payment_date, dt_str_fmt)   
    except Exception as e:
        msg = ("date format should "
               " be dd-mm-yyyy,  error {}".format(str(e)) )
        print(msg)
        result =  {"payment": None, "msg": msg}
        return msg
    if not b_form < b_to and not b_to <= current_date :
        msg = ("bill_to should be greater than bill_from and "
               " less than current_date")
        return msg
    try:
        l = Lnetlink.query.filter_by(id=netlink_id).first()
#         l = Lnetlink.query.filter_by(id=netlink_id)            
    except Exception as e:
        msg = ("Link not  found,  register them first in the respective"
               " master db, the error is {}".format(str(e)))
        print(msg)
        result =  {"payment": None, "msg": msg}
        return msg
    try:      
        payment = Payment(invoice_id=invoice_id, billing_from=b_form,
                          billing_to=b_to, billing_type=billing_type,
                          amount=amount, date=p_date,
                          mode=mode, ref_no=ref_no, status=status, 
                          netlink_id=netlink_id)    
        msg = _register_record(payment)
        l.last_payment_date = p_date
        update_msg = _update_record(l)
        print(update_msg)
    except Exception as e:
        msg = "DB error , check the error: {}".format(str(e))
        print(msg)
        result =  {"payment": None, "msg": msg}        
#     result =  {"payment": payment.to_dict(), "msg": msg}
    return msg


def add_lnetlink(infoopsid, altaddress_id, rate_id, last_payment_date=None):
    #TODO: check for the presense of infoopsid in infoopsdb
    #TODO: last_payment_date , can we auto populate from 
#     for p in self.payments:
#        latest  p.payment_date 
    if last_payment_date:
        try:
            l_payment_date = datetime.datetime.strptime(last_payment_date,
                                                         dt_str_fmt)                  
            assert(l_payment_date <= current_date)
        except Exception as e:
            msg = ("last_payment_date  format should be dd-mm-yyyy,"
                   " and can not be future date look at the detail"
                   " error {}".format(str(e)) )
            print(msg)
    #         result =  {"lnetlink": None, "msg": msg}
            return msg      
    try:
        a = Altaddress.query.filter_by(id=altaddress_id).first()
        r = Rate.query.filter_by(id=rate_id).first()
        #TODO: rate.activity_type == infoops link lifecycle_phase          
    except Exception as e:
        msg = "address or rate not  found  register them first in the respective master db, \
                   the error is {}".format(e)
        print(msg)
#         result =  {"lnetlink": None, "msg": msg}
        return msg
    if last_payment_date:
        lnetlink = Lnetlink(infoopsid=infoopsid, altaddress_id=altaddress_id,
                     rate_id=rate_id, last_payment_date=l_payment_date)
    else:
        lnetlink = Lnetlink(infoopsid=infoopsid, altaddress_id=altaddress_id,
                     rate_id=rate_id)
        
    msg = _register_record(lnetlink)
#     result =  {"lnetlink": lnetlink.to_dict(), "msg": msg}
    return msg



def _update_record(record):
    if record:
        try:                
            db.session.commit()
            msg = "{} has been updated.".format(record)         
        except exc.IntegrityError as e :
            msg = ('databse integrity error, {}Full detail: {}'.format( record, e))
            db.session.rollback()
            #raise
        except  Exception as e:
            msg =("{} could not be updated , the erro is: \n  {}".format(record, e))
            db.session.rollback() 
    print(msg)
    return msg  


def _register_record(record):
    if record:
        try:
            db.session.add(record)        
            db.session.commit()
            msg = "{} has been registered.".format(record.to_dict())         
        except exc.IntegrityError as e :
            msg = ('databse integrity error, {} by the same name may be already present  or all the requred'
                   'fileds has not been supplied.\n\n Full detail: {}'.format( record, e))
            db.session.rollback()
            #raise
        except  Exception as e:
            msg =("{} could not be registered , the erro is: \n  {}".format(record, e))
            db.session.rollback() 
    print(msg)
    return msg

def list_obj(objname,  fname, fvalue, wfc, infolink_lod=None):
        objmap = {"Rate": Rate, "Payment": Payment, "Altaddress": Altaddress,
               "Lnetlink": Lnetlink}
        Obj = objmap[objname]
        result_list = []
        print('within LAPI %s, %s ' %(fname, fvalue))
        kv = {}
        kv[fname] = fvalue
        if fname == 'all' and fvalue == 'all':
            s = db.session.query(Obj).all()            #result = conn.execute(s)
        else:
            s = db.session.query(Obj).filter_by(**kv) 
                   
        for row in s:
            if objname == "Lnetlink":
                if hasattr(row, "infoopsid")  and infolink_lod:
                    if _list_obj_filter_by_div(row, infolink_lod, wfc):
                        d = row.to_dict()
                        result_list.append(d)
            else:
                d = row.to_dict()
                result_list.append(d)
        return result_list
    
def _list_obj_filter_by_div(row, infolink_lod:list,  wfc):
    for infl in infolink_lod:
        if row.infoopsid == infl.get('serial_no'):
            infolink = infl
#     infolink = [infl  for infl in infolink_lod if row.infoopsid == infl.get('serial_no')]

            if (wfc.orgunit == infolink.get('division_name') or 
                wfc.orgunit == "ITSS" or 
                wfc.org == infolink.get('tsp_name')):
                return True
    return False
     
    
             
     
def delete_obj(objname, id):
    record = None  
    objmap = {"Rate": Rate, "Payment": Payment, "Altaddress": Altaddress,
               "Lnetlink": Lnetlink}
    Obj = objmap[objname]
    if id !='all':        
        record = db.session.query(Obj).filter_by(id=id).first()
        db.session.delete(record) 
    else:
        record = db.session.query(Obj).delete()    
    if  record:
        try:      
            db.session.commit()             
            status = "{} has been  deleted successfully".format(id) 
            print(status)
            #print('i am here')
            return status
        except  Exception as e:
                status = "{} could not be deleted , the erro is: \n  {}".format(id, e)
                print(status)
                #return status
    else:
        status = "{}  not found in database".format(id)
        print(status)
    
    return status   


def add_bulk_obj(objname, lod:list):
    objmap = {"Rate": Rate, "Payment": Payment, "Altaddress": Altaddress,
               "Lnetlink": Lnetlink}
    Obj = objmap[objname]
    try:
        db.session.bulk_insert_mappings(Obj, lod)     
        db.session.commit()
        msg = "{} has been registered".format(objname)        
    except exc.IntegrityError as e :
        msg = ('databse integrity error, {} by the same name may be already present  or all the requred'
               'fileds has not been supplied.\n\n Full detail: {}'.format( lod, e))
        db.session.rollback()
        #raise
    except  Exception as e:
        msg =("{} could not be registered , the erro is: \n  {}".format(lod, e))
        db.session.rollback() 
    print(msg)
    return msg

     
     
'''
https://docs.sqlalchemy.org/en/latest/orm/tutorial.html

from linkInventory.db.models  import NetLink
from linkInventory.db.engine import conf, DataBase
db = DataBase(conf)


for instance in db.session.query(NetLink).order_by(NetLink.serial_no):
   print(instance.link_type)
   
query = db.session.query(NetLink).filter_by(serial_no=1)
query.all()
query.first()
query.count()

 

'''