from unittest import TestCase
from flexflow.dmodels.rules import WFStatus, StatusRepo

class T1(TestCase):
    
    def test_status(self):
        s1 = WFStatus('Created', 'Invoice')
        self.assertTrue(s1.name == 'Created')
        self.assertTrue(s1.doc_category == 'Invoice')
        