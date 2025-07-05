from __future__ import unicode_literals
import frappe
from frappe.utils import nowdate

def daily_nutrition_update():
    """Daily task to update nutrition data"""
    try:
        # Get all active nutrition items
        nutrition_items = frappe.get_all("Nutrition Item", 
                                      filters={"disabled": 0},
                                      fields=["name", "item_name"])
        
        for item in nutrition_items:
            # Update each item's nutrition data
            update_item_nutrition(item["name"])
            
        frappe.db.commit()
        frappe.logger().info(f"Daily nutrition update completed for {len(nutrition_items)} items")
        
    except Exception as e:
        frappe.log_error(f"Daily Nutrition Update failed: {str(e)}")
        frappe.db.rollback()

def update_item_nutrition(item_name):
    """Update nutrition data for a single item"""
    doc = frappe.get_doc("Nutrition Item", item_name)
    
    # Add your nutrition update logic here
    # Example: Fetch from API or recalculate values
    # doc.calories = calculate_calories(doc)
    # doc.protein = calculate_protein(doc)
    
    doc.save(ignore_permissions=True)
