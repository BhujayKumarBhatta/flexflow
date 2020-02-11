from unittest import TestCase
from flexflow.dmodels.rules import Status, StatusList

class T1(TestCase):
    
    def test_status(self):
        s1 = Status('Created', 'Invoice')
        self.assertTrue(s1.name == 'Created')
        self.assertTrue(s1.doc_category == 'Invoice')
        SL = StatusList('wrong_doc_category')
        self.assertTrue(SL.doc_category == 'wrong_doc_category')
        try:
            SL.append(s1)
        except Exception as e:
            self.assertTrue(e.status == "InvalidDocCategory")
        SL = StatusList('Invoice')        
        s2 = Status('InfobahnRecommended', 'Invoice')
        SL.append(s1)
        SL.append(s2)
        self.assertTrue(s1 in SL)
        self.assertTrue(SL[1].name == 'InfobahnRecommended')