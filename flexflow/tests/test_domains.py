from unittest import TestCase
from flexflow.dmodels.rules import Status, StatusRepo

class T1(TestCase):
    
    def test_status(self):
        s1 = Status('Created', 'Invoice')
        self.assertTrue(s1.name == 'Created')
        self.assertTrue(s1.doc_category == 'Invoice')
        Srepo = StatusRepo()     
        result = Srepo.add_status_form_dict(s1.to_dict())
        self.assertTrue(result[0].name == 'Created')