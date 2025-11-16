import frappe
from frappe.model.document import Document
from frappe import _

class PlantTrial(Document):
    def validate(self):
        """Validate plant trial data before saving"""
        self.validate_dates()
        self.validate_formulation()
    
    def validate_dates(self):
        """Ensure start date is before end date if both are provided"""
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                frappe.throw(_("Start Date cannot be after End Date"))
    
    def validate_formulation(self):
        """Validate that the formulation exists"""
        if self.formulation:
            if not frappe.db.exists("Formulation", self.formulation):
                frappe.throw(_("Formulation {0} does not exist").format(self.formulation))
    
    def on_submit(self):
        """Actions when plant trial is submitted"""
        # Update formulation status or create a record of trial completion
        self.update_formulation_trial_status()
    
    def on_cancel(self):
        """Actions when plant trial is cancelled"""
        # Remove trial reference from formulation
        self.clear_formulation_trial_status()
    
    def update_formulation_trial_status(self):
        """Update the formulation with trial information"""
        if self.formulation:
            try:
                formulation = frappe.get_doc("Formulation", self.formulation)
                # Add trial information to formulation
                if not hasattr(formulation, 'plant_trials'):
                    formulation.plant_trials = []
                
                formulation.append("plant_trials", {
                    "plant_trial": self.name,
                    "trial_name": self.trial_name,
                    "start_date": self.start_date,
                    "status": "Completed" if self.docstatus == 1 else "In Progress"
                })
                
                formulation.save()
                frappe.db.commit()
                
            except Exception as e:
                frappe.log_error(f"Error updating formulation trial status: {str(e)}")
    
    def clear_formulation_trial_status(self):
        """Remove trial reference from formulation when cancelled"""
        if self.formulation:
            try:
                formulation = frappe.get_doc("Formulation", self.formulation)
                if hasattr(formulation, 'plant_trials'):
                    # Remove this trial from formulation's plant_trials child table
                    formulation.plant_trials = [trial for trial in formulation.plant_trials 
                                              if trial.plant_trial != self.name]
                    formulation.save()
                    frappe.db.commit()
                    
            except Exception as e:
                frappe.log_error(f"Error clearing formulation trial status: {str(e)}")

@frappe.whitelist()
def get_trial_summary(plant_trial_name):
    """Get summary information for a plant trial"""
    trial = frappe.get_doc("Plant Trial", plant_trial_name)
    
    summary = {
        "trial_name": trial.trial_name,
        "formulation": trial.formulation,
        "start_date": trial.start_date,
        "status": "Completed" if trial.docstatus == 1 else "Draft",
        "has_results": bool(trial.results)
    }
    
    return summary

@frappe.whitelist()
def create_trial_from_formulation(formulation_name, trial_name=None):
    """Create a new plant trial from a formulation"""
    if not frappe.db.exists("Formulation", formulation_name):
        frappe.throw(_("Formulation {0} does not exist").format(formulation_name))
    
    formulation = frappe.get_doc("Formulation", formulation_name)
    
    if not trial_name:
        trial_name = f"Plant Trial - {formulation.formulation_name}"
    
    # Create new plant trial
    plant_trial = frappe.new_doc("Plant Trial")
    plant_trial.trial_name = trial_name
    plant_trial.formulation = formulation_name
    plant_trial.start_date = frappe.utils.nowdate()
    
    plant_trial.insert()
    
    frappe.msgprint(_("Plant Trial {0} created successfully").format(plant_trial.name))
    return plant_trial.name

@frappe.whitelist()
def get_active_trials():
    """Get all active plant trials"""
    active_trials = frappe.get_all("Plant Trial",
        filters={"docstatus": 0},  # Draft status
        fields=["name", "trial_name", "formulation", "start_date"]
    )
    
    return active_trials

@frappe.whitelist()
def complete_trial(plant_trial_name, results=None):
    """Mark a plant trial as completed"""
    trial = frappe.get_doc("Plant Trial", plant_trial_name)
    
    if results:
        trial.results = results
    
    trial.submit()
    
    frappe.msgprint(_("Plant Trial {0} marked as completed").format(plant_trial_name))
    return True
