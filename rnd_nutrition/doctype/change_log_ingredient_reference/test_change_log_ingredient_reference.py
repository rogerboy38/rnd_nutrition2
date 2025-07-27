import frappe
import unittest
from frappe.utils import nowdate
from rnd_nutrition.rnd_nutrition.doctype.change_log_ingredient_reference.change_log_ingredient_reference import ChangeLogIngredientReference

class TestChangeLogIngredientReference(unittest.TestCase):
    def setUp(self):
        # Create test data
        self.create_test_item()
        self.create_test_uom()
        
    def tearDown(self):
        # Clean up test data
        frappe.delete_doc_if_exists("Item", "TEST-INGREDIENT-001")
        frappe.delete_doc_if_exists("UOM", "TEST-UOM")
    
    def create_test_item(self):
        if not frappe.db.exists("Item", "TEST-INGREDIENT-001"):
            doc = frappe.get_doc({
                "doctype": "Item",
                "item_code": "TEST-INGREDIENT-001",
                "item_name": "Test Ingredient",
                "item_group": "Raw Material",
                "stock_uom": "Kg"
            }).insert()
    
    def create_test_uom(self):
        if not frappe.db.exists("UOM", "TEST-UOM"):
            doc = frappe.get_doc({
                "doctype": "UOM",
                "uom_name": "TEST-UOM",
                "must_be_whole_number": 0
            }).insert()
    
    def test_create_ingredient_reference(self):
        """Test basic creation of ingredient reference"""
        doc = frappe.get_doc({
            "doctype": "Change Log Ingredient Reference",
            "ingredient": "TEST-INGREDIENT-001",
            "old_quantity": 10,
            "new_quantity": 12,
            "uom": "Kg",
            "reason": "Test reason"
        }).insert()
        
        self.assertEqual(doc.ingredient_name, "Test Ingredient")
        self.assertEqual(doc.change_percentage, 20.0)
    
    def test_validation(self):
        """Test validation for required fields"""
        with self.assertRaises(frappe.ValidationError):
            doc = frappe.get_doc({
                "doctype": "Change Log Ingredient Reference",
                # Missing required fields
            }).insert()
    
    def test_percentage_calculation(self):
        """Test calculation of percentage change"""
        test_cases = [
            # (old_qty, new_qty, expected_percentage)
            (10, 12, 20.0),    # Increase
            (10, 8, -20.0),     # Decrease
            (5, 5, 0.0),       # No change
            (0.5, 0.75, 50.0),  # Fractional values
            (100, 150, 50.0),   # Large numbers
            (0, 10, None)       # Division by zero (should not calculate)
        ]
        
        for old_qty, new_qty, expected in test_cases:
            with self.subTest(old_qty=old_qty, new_qty=new_qty):
                doc = frappe.get_doc({
                    "doctype": "Change Log Ingredient Reference",
                    "ingredient": "TEST-INGREDIENT-001",
                    "old_quantity": old_qty,
                    "new_quantity": new_qty,
                    "uom": "Kg",
                    "reason": "Test calculation"
                }).insert()
                
                if old_qty != 0:
                    self.assertEqual(doc.change_percentage, expected)
                else:
                    self.assertIsNone(doc.change_percentage)
    
    def test_ingredient_name_fetch(self):
        """Test automatic fetching of ingredient name"""
        doc = frappe.get_doc({
            "doctype": "Change Log Ingredient Reference",
            "ingredient": "TEST-INGREDIENT-001",
            "old_quantity": 10,
            "new_quantity": 12,
            "uom": "Kg"
        })
        
        # Name should be fetched before save
        self.assertEqual(doc.ingredient_name, "Test Ingredient")
        
        # Change ingredient and verify name updates
        doc.ingredient = "TEST-INGREDIENT-001"
        doc.save()
        self.assertEqual(doc.ingredient_name, "Test Ingredient")
    
    def test_uom_validation(self):
        """Test validation for UOM field"""
        # Valid UOM
        doc = frappe.get_doc({
            "doctype": "Change Log Ingredient Reference",
            "ingredient": "TEST-INGREDIENT-001",
            "old_quantity": 10,
            "new_quantity": 12,
            "uom": "TEST-UOM"
        }).insert()
        self.assertEqual(doc.uom, "TEST-UOM")
        
        # Invalid UOM
        with self.assertRaises(frappe.ValidationError):
            doc = frappe.get_doc({
                "doctype": "Change Log Ingredient Reference",
                "ingredient": "TEST-INGREDIENT-001",
                "old_quantity": 10,
                "new_quantity": 12,
                "uom": "INVALID-UOM"
            }).insert()
    
    def test_table_behavior_in_parent(self):
        """Test the behavior when used as a child table"""
        # Create parent doc
        parent = frappe.get_doc({
            "doctype": "Formulation Change Log",
            "formulation": "TEST-FORM-001",
            "date": nowdate(),
            "changed_by": "Administrator",
            "change_type": "Ingredient Change",
            "description": "Test parent-child relationship",
            "status": "Draft",
            "ingredient_changes": [
                {
                    "ingredient": "TEST-INGREDIENT-001",
                    "old_quantity": 5,
                    "new_quantity": 6,
                    "uom": "Kg",
                    "reason": "Test in parent"
                }
            ]
        }).insert()
        
        # Verify child table values
        self.assertEqual(len(parent.ingredient_changes), 1)
        child = parent.ingredient_changes[0]
        self.assertEqual(child.ingredient_name, "Test Ingredient")
        self.assertEqual(child.change_percentage, 20.0)
        
        # Test adding another row
        parent.append("ingredient_changes", {
            "ingredient": "TEST-INGREDIENT-001",
            "old_quantity": 10,
            "new_quantity": 8,
            "uom": "Kg",
            "reason": "Second test"
        })
        parent.save()
        
        self.assertEqual(len(parent.ingredient_changes), 2)
        self.assertEqual(parent.ingredient_changes[1].change_percentage, -20.0)

def create_test_data():
    suite = unittest.TestSuite()
    suite.addTest(TestChangeLogIngredientReference('test_create_ingredient_reference'))
    suite.addTest(TestChangeLogIngredientReference('test_percentage_calculation'))
    suite.addTest(TestChangeLogIngredientReference('test_table_behavior_in_parent'))
    return suite
