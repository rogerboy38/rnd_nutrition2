import frappe
import unittest
from frappe.utils import nowdate, add_days
from rnd_nutrition.rnd_nutrition.doctype.animal_trial.animal_trial import (
    create_animal_trial_from_formulation,
    get_animal_trial_summary,
    get_active_animal_trials,
    complete_animal_trial,
    get_animal_trial_report
)

class TestAnimalTrial(unittest.TestCase):
    def setUp(self):
        """Create test data"""
        # Create a test formulation for animal nutrition
        self.formulation = frappe.get_doc({
            "doctype": "Formulation",
            "formulation_name": "Test Animal Formulation",
            "purpose": "Animal Nutrition",
            "description": "Test formulation for animal trials"
        })
        self.formulation.insert()
        
        # Create test animal trial
        self.animal_trial = frappe.get_doc({
            "doctype": "Animal Trial",
            "trial_name": "Test Animal Trial",
            "formulation": self.formulation.name,
            "start_date": nowdate()
        })
    
    def tearDown(self):
        """Clean up test data"""
        # Delete in correct order to maintain referential integrity
        if frappe.db.exists("Animal Trial", self.animal_trial.name):
            # Unlink before deleting
            self.animal_trial.docstatus = 0
            self.animal_trial.save()
            frappe.delete_doc("Animal Trial", self.animal_trial.name)
        
        if frappe.db.exists("Formulation", self.formulation.name):
            frappe.delete_doc("Formulation", self.formulation.name)
    
    def test_animal_trial_creation(self):
        """Test creating a new animal trial"""
        self.animal_trial.insert()
        self.assertTrue(frappe.db.exists("Animal Trial", self.animal_trial.name))
    
    def test_animal_trial_validation(self):
        """Test animal trial validation"""
        self.animal_trial.insert()
        
        # Test date validation
        self.animal_trial.start_date = nowdate()
        self.animal_trial.end_date = add_days(nowdate(), -1)  # End before start
        
        with self.assertRaises(frappe.ValidationError):
            self.animal_trial.save()
    
    def test_formulation_purpose_validation(self):
        """Test formulation purpose validation"""
        # Create a non-animal formulation
        plant_formulation = frappe.get_doc({
            "doctype": "Formulation",
            "formulation_name": "Test Plant Formulation",
            "purpose": "Plant Nutrition"
        })
        plant_formulation.insert()
        
        invalid_trial = frappe.get_doc({
            "doctype": "Animal Trial",
            "trial_name": "Invalid Animal Trial",
            "formulation": plant_formulation.name
        })
        
        with self.assertRaises(frappe.ValidationError):
            invalid_trial.insert()
        
        # Clean up
        frappe.delete_doc("Formulation", plant_formulation.name)
    
    def test_create_animal_trial_from_formulation_method(self):
        """Test create_animal_trial_from_formulation whitelisted method"""
        # Test with auto-generated name
        trial_name = create_animal_trial_from_formulation(self.formulation.name)
        self.assertTrue(frappe.db.exists("Animal Trial", trial_name))
        
        # Clean up
        frappe.delete_doc("Animal Trial", trial_name)
        
        # Test with custom name
        custom_trial_name = "Custom Animal Trial"
        trial_name = create_animal_trial_from_formulation(
            self.formulation.name, 
            custom_trial_name
        )
        trial = frappe.get_doc("Animal Trial", trial_name)
        self.assertEqual(trial.trial_name, custom_trial_name)
        
        # Clean up
        frappe.delete_doc("Animal Trial", trial_name)
    
    def test_get_animal_trial_summary_method(self):
        """Test get_animal_trial_summary whitelisted method"""
        self.animal_trial.insert()
        
        summary = get_animal_trial_summary(self.animal_trial.name)
        
        self.assertEqual(summary["trial_name"], self.animal_trial.trial_name)
        self.assertEqual(summary["formulation"], self.animal_trial.formulation)
        self.assertEqual(summary["status"], "Draft")
        self.assertFalse(summary["has_results"])
        self.assertEqual(summary["trial_type"], "Animal Trial")
    
    def test_complete_animal_trial_method(self):
        """Test complete_animal_trial whitelisted method"""
        self.animal_trial.insert()
        
        results = "Test results: Animals showed improved health and growth rates."
        success = complete_animal_trial(self.animal_trial.name, results)
        
        self.assertTrue(success)
        
        # Verify trial was submitted
        updated_trial = frappe.get_doc("Animal Trial", self.animal_trial.name)
        self.assertEqual(updated_trial.docstatus, 1)
        self.assertEqual(updated_trial.results, results)
    
    def test_get_active_animal_trials_method(self):
        """Test get_active_animal_trials whitelisted method"""
        self.animal_trial.insert()
        
        active_trials = get_active_animal_trials()
        
        # Should find our test trial in active trials
        trial_found = any(trial["name"] == self.animal_trial.name 
                         for trial in active_trials)
        self.assertTrue(trial_found)
    
    def test_get_animal_trial_report_method(self):
        """Test get_animal_trial_report whitelisted method"""
        self.animal_trial.insert()
        
        report = get_animal_trial_report(self.animal_trial.name)
        
        self.assertEqual(report["trial_info"]["name"], self.animal_trial.name)
        self.assertEqual(report["trial_info"]["trial_name"], self.animal_trial.trial_name)
        self.assertIsNotNone(report["formulation_info"])
    
    def test_on_submit_behavior(self):
        """Test behavior when animal trial is submitted"""
        self.animal_trial.insert()
        
        # Add results and submit
        self.animal_trial.results = "Successful animal trial with positive health outcomes"
        self.animal_trial.submit()
        
        # Verify submission
        self.assertEqual(self.animal_trial.docstatus, 1)
    
    def test_on_cancel_behavior(self):
        """Test behavior when animal trial is cancelled"""
        self.animal_trial.insert()
        self.animal_trial.submit()
        
        # Verify can be cancelled
        self.animal_trial.cancel()
        self.assertEqual(self.animal_trial.docstatus, 2)
    
    def test_animal_trial_workflow(self):
        """Test complete animal trial workflow"""
        # Create
        self.animal_trial.insert()
        self.assertEqual(self.animal_trial.docstatus, 0)
        
        # Add results and submit
        self.animal_trial.results = "Final animal trial results"
        self.animal_trial.submit()
        self.assertEqual(self.animal_trial.docstatus, 1)
        
        # Cancel
        self.animal_trial.cancel()
        self.assertEqual(self.animal_trial.docstatus, 2)

def create_test_animal_trial():
    """Create a test animal trial for manual testing"""
    try:
        # First create a formulation for animal nutrition
        formulation = frappe.get_doc({
            "doctype": "Formulation",
            "formulation_name": "Sample Animal Formulation",
            "purpose": "Animal Nutrition",
            "description": "Sample formulation for manual animal testing"
        })
        formulation.insert()
        
        # Create animal trial
        animal_trial = frappe.get_doc({
            "doctype": "Animal Trial",
            "trial_name": "Sample Animal Health Trial",
            "formulation": formulation.name,
            "start_date": nowdate(),
            "results": "Sample results: Animals showed 30% improvement in health metrics."
        })
        
        animal_trial.insert()
        frappe.db.commit()
        
        print(f"Test animal trial created: {animal_trial.name}")
        print(f"Linked formulation: {formulation.name}")
        
        return animal_trial.name
        
    except Exception as e:
        print(f"Error creating test animal trial: {str(e)}")
        frappe.db.rollback()

if __name__ == "__main__":
    # Run specific tests
    import frappe
    frappe.init(site="your-site.local")
    frappe.connect()
    
    try:
        # Create test data
        test_trial_name = create_test_animal_trial()
        print(f"Created test animal trial: {test_trial_name}")
        
        # Run tests
        unittest.main()
        
    finally:
        frappe.destroy()
