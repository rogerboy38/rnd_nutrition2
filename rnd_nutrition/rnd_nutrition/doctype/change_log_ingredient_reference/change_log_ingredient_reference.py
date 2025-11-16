import frappe
from frappe.model.document import Document

class ChangeLogIngredientReference(Document):
    def before_save(self):
        self.calculate_change_percentage()
        self.fetch_ingredient_name()
    
    def calculate_change_percentage(self):
        if self.old_quantity and self.new_quantity and self.old_quantity != 0:
            self.change_percentage = ((self.new_quantity - self.old_quantity) / self.old_quantity) * 100
    
    def fetch_ingredient_name(self):
        if self.ingredient and not self.ingredient_name:
            self.ingredient_name = frappe.db.get_value("Item", self.ingredient, "item_name")
