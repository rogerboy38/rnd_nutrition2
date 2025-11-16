from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class NutritionItem(Document):
    def validate(self):
        self.validate_nutrition_values()
        self.set_defaults()
    
    def validate_nutrition_values(self):
        """Validate all nutrition values are positive numbers"""
        nutrition_fields = [
            'calories', 'protein', 'carbohydrates', 'sugars',
            'dietary_fiber', 'total_fat', 'saturated_fat', 'trans_fat',
            'vitamin_a', 'vitamin_c', 'calcium', 'iron'
        ]
        
        for field in nutrition_fields:
            if self.get(field) and float(self.get(field)) < 0:
                frappe.throw(f"{frappe.unscrub(field)} cannot be negative")
    
    def set_defaults(self):
        """Set default values"""
        if not self.standard_quantity:
            self.standard_quantity = 1
