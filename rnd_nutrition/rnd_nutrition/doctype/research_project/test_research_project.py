import frappe
import unittest
from frappe.utils import nowdate, add_days

class TestResearchProject(unittest.TestCase):
    def setUp(self):
        self.project = frappe.get_doc({
            "doctype": "Research Project",
            "project_name": "Test Research Project",
            "description": "Test project for research",
            "status": "Planning"
        })
    
    def tearDown(self):
        if frappe.db.exists("Research Project", self.project.name):
            frappe.delete_doc("Research Project", self.project.name)
    
    def test_project_creation(self):
        self.project.insert()
        self.assertTrue(frappe.db.exists("Research Project", self.project.name))
    
    def test_date_validation(self):
        self.project.start_date = nowdate()
        self.project.end_date = add_days(nowdate(), -1)
        
        with self.assertRaises(frappe.ValidationError):
            self.project.insert()
