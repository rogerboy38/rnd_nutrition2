import frappe
import unittest
from frappe.utils import nowdate, add_days
from rnd_nutrition.rnd_nutrition.doctype.plant_trial.plant_trial import (
    create_trial_from_formulation,
    get_trial_summary,
    get_active_trials,
    complete_trial
)

class TestPlantTrial(unittest.TestCase):
    def setUp(self):
        """Create test data"""
        # Create a test formulation first
        self.formulation = frappe.get_doc({
            "doctype": "Formulation",
            "formulation_name": "Test Plant Formulation",
            "purpose": "Plant Nutrition",
            "description": "Test formulation for plant trials"
        })
        self.formulation.insert()
        
        # Create test plant trial
        self.plant_trial = frappe.get_doc({
            "doctype": "Plant Trial",
            "trial_name": "Test Plant Trial",
            "formulation": self.formulation.name,
            "start_date": nowdate()
        })
    
    def tearDown(self):
        """Clean up test data"""
        # Delete in correct order to maintain referential integrity
        if frappe.db.exists("Plant Trial", self.plant_trial.name):
            # Unlink before deleting
            self.plant_trial.docstatus = 0
            self.plant_trial.save()
            frappe.delete_doc("Plant Trial", self.plant_trial.name)
        
        if frappe.db.exists("Formulation", self.formulation.name):
            frappe.delete_doc("Formulation", self.formulation.name)
    
    def test_plant_trial_creation(self):
        """Test creating a new plant trial"""
        self.plant_trial.insert()
        self.assertTrue(frappe.db.exists("Plant Trial", self.plant_trial.name))
    
    def test_plant_trial_validation(self):
        """Test plant trial validation"""
        self.plant_trial.insert()
        
        # Test date validation
        self.plant_trial.start_date = nowdate()
        self.plant_trial.end_date = add_days(nowdate(), -1)  # End before start
        
        with self.assertRaises(frappe.ValidationError):
            self.plant_trial.save()
    
    def test_formulation_validation(self):
        """Test formulation existence validation"""
        invalid_trial = frappe.get_doc({
            "doctype": "Plant Trial",
            "trial_name": "Invalid Trial",
            "formulation": "NONEXISTENT_FORMULATION"
        })
        
        with self.assertRaises(frappe.ValidationError):
            invalid_trial.insert()
    
    def test_create_trial_from_formulation_method(self):
        """Test create_trial_from_formulation whitelisted method"""
        # Test with auto-generated name
        trial_name = create_trial_from_formulation(self.formulation.name)
        self.assertTrue(frappe.db.exists("Plant Trial", trial_name))
        
        # Clean up
        frappe.delete_doc("Plant Trial", trial_name)
        
        # Test with custom name
        custom_trial_name = "Custom Plant Trial"
        trial_name = create_trial_from_formulation(
            self.formulation.name, 
            custom_trial_name
        )
        trial = frappe.get_doc("Plant Trial", trial_name)
        self.assertEqual(trial.trial_name, custom_trial_name)
        
        # Clean up
        frappe.delete_doc("Plant Trial", trial_name)
    
    def test_get_trial_summary_method(self):
        """Test get_trial_summary whitelisted method"""
        self.plant_trial.insert()
        
        summary = get_trial_summary(self.plant_trial.name)
        
        self.assertEqual(summary["trial_name"], self.plant_trial.trial_name)
        self.assertEqual(summary["formulation"], self.plant_trial.formulation)
        self.assertEqual(summary["status"], "Draft")
        self.assertFalse(summary["has_results"])
    
    def test_complete_trial_method(self):
        """Test complete_trial whitelisted method"""
        self.plant_trial.insert()
        
        results = "Test results: Plant showed significant growth improvement."
        success = complete_trial(self.plant_trial.name, results)
        
        self.assertTrue(success)
        
        # Verify trial was submitted
        updated_trial = frappe.get_doc("Plant Trial", self.plant_trial.name)
        self.assertEqual(updated_trial.docstatus, 1)
        self.assertEqual(updated_trial.results, results)
    
    def test_get_active_trials_method(self):
        """Test get_active_trials whitelisted method"""
        self.plant_trial.insert()
        
        active_trials = get_active_trials()
        
        # Should find our test trial in active trials
        trial_found = any(trial["name"] == self.plant_trial.name 
                         for trial in active_trials)
        self.assertTrue(trial_found)
    
    def test_on_submit_behavior(self):
        """Test behavior when plant trial is submitted"""
        self.plant_trial.insert()
        
        # Add results and submit
        self.plant_trial.results = "Successful trial with positive results"
        self.plant_trial.submit()
        
        # Verify submission
        self.assertEqual(self.plant_trial.docstatus, 1)
    
    def test_on_cancel_behavior(self):
        """Test behavior when plant trial is cancelled"""
        self.plant_trial.insert()
        self.plant_trial.submit()
        
        # Verify can be cancelled
        self.plant_trial.cancel()
        self.assertEqual(self.plant_trial.docstatus, 2)
    
    def test_trial_workflow(self):
        """Test complete plant trial workflow"""
        # Create
        self.plant_trial.insert()
        self.assertEqual(self.plant_trial.docstatus, 0)
        
        # Add results and submit
        self.plant_trial.results = "Final trial results"
        self.plant_trial.submit()
        self.assertEqual(self.plant_trial.docstatus, 1)
        
        # Cancel
        self.plant_trial.cancel()
        self.assertEqual(self.plant_trial.docstatus, 2)

def create_test_plant_trial():
    """Create a test plant trial for manual testing"""
    try:
        # First create a formulation
        formulation = frappe.get_doc({
            "doctype": "Formulation",
            "formulation_name": "Sample Plant Formulation",
            "purpose": "Plant Nutrition",
            "description": "Sample formulation for manual testing"
        })
        formulation.insert()
        
        # Create plant trial
        plant_trial = frappe.get_doc({
            "doctype": "Plant Trial",
            "trial_name": "Sample Plant Growth Trial",
            "formulation": formulation.name,
            "start_date": nowdate(),
            "results": "Sample results: Plants showed 25% growth improvement."
        })
        
        plant_trial.insert()
        frappe.db.commit()
        
        print(f"Test plant trial created: {plant_trial.name}")
        print(f"Linked formulation: {formulation.name}")
        
        return plant_trial.name
        
    except Exception as e:
        print(f"Error creating test plant trial: {str(e)}")
        frappe.db.rollback()

if __name__ == "__main__":
    # Run specific tests
    import frappe
    frappe.init(site="your-site.local")
    frappe.connect()
    
    try:
        # Create test data
        test_trial_name = create_test_plant_trial()
        print(f"Created test trial: {test_trial_name}")
        
        # Run tests
        unittest.main()
        
    finally:
        frappe.destroy()
