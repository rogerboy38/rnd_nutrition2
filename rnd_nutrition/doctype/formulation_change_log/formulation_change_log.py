import frappe
from frappe.model.document import Document

class FormulationChangeLog(Document):
    def before_save(self):
        self.validate_changes()
        self.set_title()
    
    def validate_changes(self):
        if not self.description and not self.ingredient_changes:
            frappe.throw("Please provide either a description or ingredient changes")
    
    def set_title(self):
        if self.formulation and not self.is_new():
            formulation_name = frappe.db.get_value("Formulation", self.formulation, "formulation_name")
            self.title = f"{formulation_name} - {self.change_type}"

    def on_update(self):
        self.notify_concerned_parties()
    
    def notify_concerned_parties(self):
        if self.status == "Approved":
            recipients = frappe.db.sql_list("""
                SELECT DISTINCT parent 
                FROM `tabHas Role` 
                WHERE role IN ('RND Manager', 'Quality Manager')
            """)
            
            message = f"""
                Formulation Change {self.name} has been approved.
                Change Type: {self.change_type}
                Description: {self.description}
            """
            
            frappe.sendmail(
                recipients=recipients,
                subject=f"Formulation Change Approved: {self.name}",
                message=message,
                reference_doctype=self.doctype,
                reference_name=self.name
            )

@frappe.whitelist()
def get_formulation_details(formulation):
    return frappe.get_doc("Formulation", formulation).as_dict()
