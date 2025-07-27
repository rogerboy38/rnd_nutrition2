import frappe
import unittest
from frappe.utils import nowdate, add_days
from rnd_nutrition.rnd_nutrition.doctype.formulation_change_log.formulation_change_log import FormulationChangeLog

class TestFormulationChangeLog(unittest.TestCase):
    def setUp(self):
        # Create test data
        self.create_test_formulation()
        self.create_test_user()
        self.create_test_item()
        
    def tearDown(self):
        # Clean up test data
        frappe.delete_doc_if_exists("Formulation Change Log", "FL-TEST-001")
        frappe.delete_doc_if_exists("Formulation", "TEST-FORM-001")
        frappe.delete_doc_if_exists("User", "test_rnd_user@example.com")
        frappe.delete_doc_if_exists("Item", "TEST-INGREDIENT-001")
    
    def create_test_formulation(self):
        if not frappe.db.exists("Formulation", "TEST-FORM-001"):
            doc = frappe.get_doc({
                "doctype": "Formulation",
                "formulation_code": "TEST-FORM-001",
                "formulation_name": "Test Formulation",
                "status": "Active"
            }).insert()
    
    def create_test_user(self):
        if not frappe.db.exists("User", "test_rnd_user@example.com"):
            user = frappe.get_doc({
                "doctype": "User",
                "email": "test_rnd_user@example.com",
                "first_name": "Test",
                "last_name": "RND User",
                "roles": [{
                    "role": "RND Manager"
                }]
            }).insert()
    
    def create_test_item(self):
        if not frappe.db.exists("Item", "TEST-INGREDIENT-001"):
            item = frappe.get_doc({
                "doctype": "Item",
                "item_code": "TEST-INGREDIENT-001",
                "item_name": "Test Ingredient",
                "item_group": "Raw Material",
                "stock_uom": "Kg"
            }).insert()
    
    def test_create_change_log(self):
        """Test basic creation of change log"""
        doc = frappe.get_doc({
            "doctype": "Formulation Change Log",
            "formulation": "TEST-FORM-001",
            "date": nowdate(),
            "changed_by": "test_rnd_user@example.com",
            "change_type": "Ingredient Change",
            "description": "Test change description",
            "status": "Draft",
            "ingredient_changes": [{
                "ingredient": "TEST-INGREDIENT-001",
                "old_quantity": 10,
                "new_quantity": 12,
                "uom": "Kg",
                "reason": "Test reason"
            }]
        }).insert()
        
        self.assertEqual(doc.name, "FL-TEST-001")
        self.assertEqual(doc.status, "Draft")
        self.assertEqual(len(doc.ingredient_changes), 1)
        self.assertEqual(doc.ingredient_changes[0].change_percentage, 20.0)
    
    def test_validation(self):
        """Test validation for required fields"""
        with self.assertRaises(frappe.ValidationError):
            doc = frappe.get_doc({
                "doctype": "Formulation Change Log",
                "formulation": "TEST-FORM-001",
                "date": nowdate()
                # Missing required fields
            }).insert()
    
    def test_status_transitions(self):
        """Test valid status transitions"""
        doc = frappe.get_doc({
            "doctype": "Formulation Change Log",
            "formulation": "TEST-FORM-001",
            "date": nowdate(),
            "changed_by": "test_rnd_user@example.com",
            "change_type": "Process Change",
            "description": "Test process change",
            "status": "Draft"
        }).insert()
        
        # Draft -> Approved
        doc.status = "Approved"
        doc.save()
        self.assertEqual(doc.status, "Approved")
        
        # Approved -> Implemented
        doc.status = "Implemented"
        doc.save()
        self.assertEqual(doc.status, "Implemented")
        
        # Should not allow going back to Draft
        with self.assertRaises(frappe.ValidationError):
            doc.status = "Draft"
            doc.save()
    
    def test_auto_title(self):
        """Test automatic title generation"""
        doc = frappe.get_doc({
            "doctype": "Formulation Change Log",
            "formulation": "TEST-FORM-001",
            "date": nowdate(),
            "changed_by": "test_rnd_user@example.com",
            "change_type": "Quantity Change",
            "description": "Test quantity change",
            "status": "Draft"
        }).insert()
        
        self.assertTrue("Test Formulation - Quantity Change" in doc.title)
    
    def test_notification_on_approval(self):
        """Test email notification when status changes to Approved"""
        # Setup email test
        frappe.flags.mute_emails = False
        frappe.flags.sent_mail = None
        
        doc = frappe.get_doc({
            "doctype": "Formulation Change Log",
            "formulation": "TEST-FORM-001",
            "date": nowdate(),
            "changed_by": "test_rnd_user@example.com",
            "change_type": "Other",
            "description": "Test notification",
            "status": "Draft"
        }).insert()
        
        # Approve the change
        doc.status = "Approved"
        doc.save()
        
        # Check if email was sent
        self.assertTrue(frappe.flags.sent_mail)
        self.assertIn("Formulation Change Approved", frappe.flags.sent_mail.get('subject'))
    
    def test_change_percentage_calculation(self):
        """Test calculation of percentage change in ingredients"""
        doc = frappe.get_doc({
            "doctype": "Formulation Change Log",
            "formulation": "TEST-FORM-001",
            "date": nowdate(),
            "changed_by": "test_rnd_user@example.com",
            "change_type": "Ingredient Change",
            "description": "Test percentage calculation",
            "status": "Draft",
            "ingredient_changes": [
                {
                    "ingredient": "TEST-INGREDIENT-001",
                    "old_quantity": 5,
                    "new_quantity": 6,
                    "uom": "Kg",
                    "reason": "Test increase"
                },
                {
                    "ingredient": "TEST-INGREDIENT-001",
                    "old_quantity": 10,
                    "new_quantity": 8,
                    "uom": "Kg",
                    "reason": "Test decrease"
                }
            ]
        }).insert()
        
        self.assertEqual(doc.ingredient_changes[0].change_percentage, 20.0)  # (6-5)/5 = 20%
        self.assertEqual(doc.ingredient_changes[1].change_percentage, -20.0)  # (8-10)/10 = -20%
    
    def test_future_date_validation(self):
        """Test that future dates are not allowed"""
        with self.assertRaises(frappe.ValidationError):
            doc = frappe.get_doc({
                "doctype": "Formulation Change Log",
                "formulation": "TEST-FORM-001",
                "date": add_days(nowdate(), 1),  # Tomorrow's date
                "changed_by": "test_rnd_user@example.com",
                "change_type": "New Formulation",
                "description": "Test future date",
                "status": "Draft"
            }).insert()

def create_test_data():
    suite = unittest.TestSuite()
    suite.addTest(TestFormulationChangeLog('test_create_change_log'))
    suite.addTest(TestFormulationChangeLog('test_status_transitions'))
    suite.addTest(TestFormulationChangeLog('test_change_percentage_calculation'))
    return suite
