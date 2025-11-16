import frappe
from frappe.model.document import Document

class FormulationIngredient(Document):
    def validate(self):
        """Validate ingredient data"""
        self.fetch_nutritional_data()
    
    def fetch_nutritional_data(self):
        """Fetch nutritional data from Nutrition Item"""
        if self.ingredient_name:
            nutrition_item = frappe.get_doc("Nutrition Item", self.ingredient_name)
            self.calories = nutrition_item.calories or 0
            self.protein = nutrition_item.protein or 0
            self.carbohydrates = nutrition_item.carbohydrates or 0
            self.fat = nutrition_item.fat or 0
