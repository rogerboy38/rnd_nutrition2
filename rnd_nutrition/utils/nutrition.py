import frappe
from frappe import _
from frappe.utils import cint, flt

def test_api_connection(endpoint, api_key):
    """Test connection to nutrition API"""
    # Implement actual API test logic here
    return True

def get_daily_values():
    """Return all daily recommended values"""
    utils = frappe.get_doc("Nutrition Utils", "Nutrition Utils")
    return {
        'calories': utils.daily_calories,
        'protein': utils.daily_protein,
        'carbs': utils.daily_carbs,
        'fat': utils.daily_fat
    }

def calculate_nutrition_totals(items):
    """Calculate totals from a list of nutrition items"""
    totals = {
        'calories': 0,
        'protein': 0,
        'carbs': 0,
        'fat': 0
    }
    
    for item in items:
        nutrition_item = frappe.get_doc("Nutrition Item", item.nutrition_item)
        quantity = flt(item.quantity) or 1
        
        for field in totals.keys():
            if hasattr(nutrition_item, field):
                totals[field] += flt(getattr(nutrition_item, field)) * quantity
    
    return totals

@frappe.whitelist()
def get_normalized_nutrition(nutrition_item, quantity=100):
    """Get normalized nutrition values for a given quantity"""
    doc = frappe.get_doc("Nutrition Item", nutrition_item)
    utils = frappe.get_doc("Nutrition Utils", "Nutrition Utils")
    
    fields = [
        'calories', 'protein', 'carbohydrates',
        'sugars', 'dietary_fiber', 'total_fat',
        'saturated_fat', 'trans_fat'
    ]
    
    values = {field: getattr(doc, field, 0) for field in fields}
    return utils.normalize_nutrition_values(values, quantity)
def update_nutrition_data(doc, method):
    """Update nutrition data when any document is updated"""
    # Add your nutrition update logic here
    # For now we'll just log it
    frappe.logger().info(f"Nutrition data update triggered for {doc.doctype} {doc.name}")
