# tasks.py
from frappe.utils.background_jobs import enqueue
import frappe

def daily_nutrition_update():
    """Your task implementation here"""
    frappe.log_error("Daily Nutrition Update executed")  # Example
    # Add your actual task logic here
