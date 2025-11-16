import frappe
from frappe.model.document import Document
from frappe import _

class AnimalTrial(Document):
    def validate(self):
        """Validate animal trial data before saving"""
        self.validate_dates()
        self.validate_formulation()
        self.validate_animal_specific_requirements()
    
    def validate_dates(self):
        """Ensure start date is before end date if both are provided"""
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                frappe.throw(_("Start Date cannot be after End Date"))
    
    def validate_formulation(self):
        """Validate that the formulation exists and is for animal nutrition"""
        if self.formulation:
            if not frappe.db.exists("Formulation", self.formulation):
                frappe.throw(_("Formulation {0} does not exist").format(self.formulation))
            
            # Check if formulation is intended for animal nutrition
            formulation_doc = frappe.get_doc("Formulation", self.formulation)
            if formulation_doc.purpose != "Animal Nutrition":
                frappe.throw(_("Formulation {0} is not intended for Animal Nutrition").format(self.formulation))
    
    def validate_animal_specific_requirements(self):
        """Validate animal-specific requirements"""
        # Add any animal-specific validation logic here
        # For example: animal species, dosage calculations, safety checks
        pass
    
    def on_submit(self):
        """Actions when animal trial is submitted"""
        # Update formulation status or create a record of trial completion
        self.update_formulation_trial_status()
        
        # Log trial completion
        self.log_trial_completion()
    
    def on_cancel(self):
        """Actions when animal trial is cancelled"""
        # Remove trial reference from formulation
        self.clear_formulation_trial_status()
        
        # Log trial cancellation
        self.log_trial_cancellation()
    
    def update_formulation_trial_status(self):
        """Update the formulation with trial information"""
        if self.formulation:
            try:
                formulation = frappe.get_doc("Formulation", self.formulation)
                # Add trial information to formulation
                if not hasattr(formulation, 'animal_trials'):
                    formulation.animal_trials = []
                
                formulation.append("animal_trials", {
                    "animal_trial": self.name,
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
                if hasattr(formulation, 'animal_trials'):
                    # Remove this trial from formulation's animal_trials child table
                    formulation.animal_trials = [trial for trial in formulation.animal_trials 
                                               if trial.animal_trial != self.name]
                    formulation.save()
                    frappe.db.commit()
                    
            except Exception as e:
                frappe.log_error(f"Error clearing formulation trial status: {str(e)}")
    
    def log_trial_completion(self):
        """Log trial completion for auditing"""
        frappe.logger().info(f"Animal Trial {self.name} completed for formulation {self.formulation}")
    
    def log_trial_cancellation(self):
        """Log trial cancellation for auditing"""
        frappe.logger().info(f"Animal Trial {self.name} cancelled")

@frappe.whitelist()
def get_animal_trial_summary(animal_trial_name):
    """Get summary information for an animal trial"""
    trial = frappe.get_doc("Animal Trial", animal_trial_name)
    
    summary = {
        "trial_name": trial.trial_name,
        "formulation": trial.formulation,
        "start_date": trial.start_date,
        "status": "Completed" if trial.docstatus == 1 else "Draft",
        "has_results": bool(trial.results),
        "trial_type": "Animal Trial"
    }
    
    return summary

@frappe.whitelist()
def create_animal_trial_from_formulation(formulation_name, trial_name=None):
    """Create a new animal trial from a formulation"""
    if not frappe.db.exists("Formulation", formulation_name):
        frappe.throw(_("Formulation {0} does not exist").format(formulation_name))
    
    formulation = frappe.get_doc("Formulation", formulation_name)
    
    # Verify formulation is for animal nutrition
    if formulation.purpose != "Animal Nutrition":
        frappe.throw(_("Formulation {0} is not intended for Animal Nutrition").format(formulation_name))
    
    if not trial_name:
        trial_name = f"Animal Trial - {formulation.formulation_name}"
    
    # Create new animal trial
    animal_trial = frappe.new_doc("Animal Trial")
    animal_trial.trial_name = trial_name
    animal_trial.formulation = formulation_name
    animal_trial.start_date = frappe.utils.nowdate()
    
    animal_trial.insert()
    
    frappe.msgprint(_("Animal Trial {0} created successfully").format(animal_trial.name))
    return animal_trial.name

@frappe.whitelist()
def get_active_animal_trials():
    """Get all active animal trials"""
    active_trials = frappe.get_all("Animal Trial",
        filters={"docstatus": 0},  # Draft status
        fields=["name", "trial_name", "formulation", "start_date"]
    )
    
    return active_trials

@frappe.whitelist()
def complete_animal_trial(animal_trial_name, results=None):
    """Mark an animal trial as completed"""
    trial = frappe.get_doc("Animal Trial", animal_trial_name)
    
    if results:
        trial.results = results
    
    trial.submit()
    
    frappe.msgprint(_("Animal Trial {0} marked as completed").format(animal_trial_name))
    return True

@frappe.whitelist()
def get_animal_trial_report(animal_trial_name):
    """Generate a comprehensive report for animal trial"""
    trial = frappe.get_doc("Animal Trial", animal_trial_name)
    formulation = frappe.get_doc("Formulation", trial.formulation) if trial.formulation else None
    
    report = {
        "trial_info": {
            "name": trial.name,
            "trial_name": trial.trial_name,
            "start_date": trial.start_date,
            "status": "Completed" if trial.docstatus == 1 else "Draft",
            "results_summary": trial.results[:500] + "..." if trial.results and len(trial.results) > 500 else trial.results
        },
        "formulation_info": {
            "name": formulation.name if formulation else None,
            "formulation_name": formulation.formulation_name if formulation else None,
            "purpose": formulation.purpose if formulation else None
        } if formulation else None
    }
    
    return report
