from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import nowdate

class NutritionUtils(Document):
    def validate(self):
        self.validate_daily_values()
        
    def validate_daily_values(self):
        """Ensure daily values are positive"""
        daily_fields = [
            'daily_calories', 'daily_protein',
            'daily_carbs', 'daily_fat'
        ]
        
        for field in daily_fields:
            if self.get(field) and float(self.get(field)) <= 0:
                frappe.throw(f"Daily {frappe.unscrub(field)} must be greater than zero")

    @staticmethod
    def get_utils():
        """Get or create the single Nutrition Utils record"""
        if not frappe.db.exists("Nutrition Utils", "Nutrition Utils"):
            utils = frappe.new_doc("Nutrition Utils")
            utils.save()
            frappe.db.commit()
        
        return frappe.get_doc("Nutrition Utils", "Nutrition Utils")

    @staticmethod
    def calculate_daily_percentage(value, nutrient_type):
        """Calculate percentage of daily recommended value"""
        utils = NutritionUtils.get_utils()
        daily_value = getattr(utils, f"daily_{nutrient_type}", 1)
        
        if not daily_value or daily_value == 0:
            return 0
            
        return round((value / daily_value) * 100, 1)

    @staticmethod
    def normalize_nutrition_values(values_dict, quantity=100):
        """Normalize nutrition values to standard quantity"""
        utils = NutritionUtils.get_utils()
        standard_quantity = utils.default_serving_size or 100
        multiplier = quantity / standard_quantity
        
        normalized = {}
        for key, value in values_dict.items():
            if isinstance(value, (int, float)):
                normalized[key] = value * multiplier
        
        return normalized
