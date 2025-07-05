from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class NutritionRecipe(Document):
    def validate(self):
        self.calculate_nutritional_values()
    
    def calculate_nutritional_values(self):
        """Calculate total nutritional values based on ingredients"""
        total_calories = 0
        total_protein = 0
        
        for item in self.nutrition_items:
            nutrition_item = frappe.get_doc("Nutrition Item", item.nutrition_item)
            
            # Calculate based on quantity used
            quantity = item.quantity or 1
            standard_quantity = nutrition_item.standard_quantity or 1
            multiplier = quantity / standard_quantity
            
            if nutrition_item.calories:
                total_calories += nutrition_item.calories * multiplier
            if nutrition_item.protein:
                total_protein += nutrition_item.protein * multiplier
        
        self.total_calories = total_calories
        self.total_protein = total_protein
