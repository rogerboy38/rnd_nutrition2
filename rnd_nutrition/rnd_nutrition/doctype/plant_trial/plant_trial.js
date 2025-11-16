frappe.ui.form.on('Plant Trial', {
    refresh: function(frm) {
        // Add custom buttons
        frm.add_custom_button(__('Create from Formulation'), function() {
            frm.trigger('create_from_formulation');
        });
        
        frm.add_custom_button(__('Trial Summary'), function() {
            frm.trigger('show_trial_summary');
        });
        
        // Add complete trial button for draft trials
        if (frm.doc.docstatus === 0) {
            frm.add_custom_button(__('Complete Trial'), function() {
                frm.trigger('complete_trial');
            }).addClass('btn-primary');
        }
        
        // Add view formulation button
        if (frm.doc.formulation) {
            frm.add_custom_button(__('View Formulation'), function() {
                frappe.set_route('Form', 'Formulation', frm.doc.formulation);
            });
        }
        
        // Toggle fields based on status
        frm.trigger('toggle_read_only_fields');
    },
    
    create_from_formulation: function(frm) {
        // Open dialog to select formulation
        let d = new frappe.ui.Dialog({
            title: __('Create Plant Trial from Formulation'),
            fields: [
                {
                    label: __('Formulation'),
                    fieldname: 'formulation',
                    fieldtype: 'Link',
                    options: 'Formulation',
                    reqd: 1
                },
                {
                    label: __('Trial Name'),
                    fieldname: 'trial_name',
                    fieldtype: 'Data',
                    placeholder: __('Auto-generated if empty'),
                    description: __('Leave empty to auto-generate from formulation name')
                }
            ],
            primary_action_label: __('Create'),
            primary_action: function(values) {
                frappe.call({
                    method: 'rnd_nutrition.rnd_nutrition.doctype.plant_trial.plant_trial.create_trial_from_formulation',
                    args: {
                        formulation_name: values.formulation,
                        trial_name: values.trial_name || null
                    },
                    callback: function(r) {
                        if (r.message) {
                            frappe.msgprint(__('Plant Trial {0} created successfully', [r.message]));
                            frappe.set_route('Form', 'Plant Trial', r.message);
                        }
                    }
                });
                d.hide();
            }
        });
        d.show();
    },
    
    show_trial_summary: function(frm) {
        if (!frm.doc.name) {
            frappe.msgprint(__('Please save the document first'));
            return;
        }
        
        frappe.call({
            method: 'rnd_nutrition.rnd_nutrition.doctype.plant_trial.plant_trial.get_trial_summary',
            args: {
                plant_trial_name: frm.doc.name
            },
            callback: function(r) {
                if (r.message) {
                    let summary = r.message;
                    let message = `
                        <h4>Trial Summary</h4>
                        <p><strong>Trial Name:</strong> ${summary.trial_name}</p>
                        <p><strong>Formulation:</strong> ${summary.formulation}</p>
                        <p><strong>Start Date:</strong> ${summary.start_date}</p>
                        <p><strong>Status:</strong> ${summary.status}</p>
                        <p><strong>Has Results:</strong> ${summary.has_results ? 'Yes' : 'No'}</p>
                    `;
                    
                    frappe.msgprint({
                        title: __('Trial Summary'),
                        message: message,
                        indicator: 'blue'
                    });
                }
            }
        });
    },
    
    complete_trial: function(frm) {
        if (frm.doc.docstatus !== 0) {
            frappe.msgprint(__('Only draft trials can be completed'));
            return;
        }
        
        let d = new frappe.ui.Dialog({
            title: __('Complete Plant Trial'),
            fields: [
                {
                    label: __('Results'),
                    fieldname: 'results',
                    fieldtype: 'Text Editor',
                    default: frm.doc.results,
                    description: __('Add trial results and observations')
                }
            ],
            primary_action_label: __('Complete Trial'),
            primary_action: function(values) {
                frappe.call({
                    method: 'rnd_nutrition.rnd_nutrition.doctype.plant_trial.plant_trial.complete_trial',
                    args: {
                        plant_trial_name: frm.doc.name,
                        results: values.results
                    },
                    callback: function(r) {
                        if (r.message) {
                            frappe.msgprint(__('Trial completed successfully'));
                            frm.reload_doc();
                        }
                    }
                });
                d.hide();
            }
        });
        d.show();
    },
    
    toggle_read_only_fields: function(frm) {
        // Make certain fields read-only based on docstatus
        let read_only = frm.doc.docstatus === 1;
        
        let fields = ['trial_name', 'formulation', 'start_date'];
        fields.forEach(function(field) {
            frm.set_df_property(field, 'read_only', read_only);
        });
    },
    
    formulation: function(frm) {
        // Auto-fill trial name when formulation is selected
        if (frm.doc.formulation && !frm.doc.trial_name) {
            frappe.db.get_value('Formulation', frm.doc.formulation, 'formulation_name')
                .then(r => {
                    if (r.message && r.message.formulation_name) {
                        frm.set_value('trial_name', 
                            `Plant Trial - ${r.message.formulation_name}`);
                    }
                });
        }
        
        // Fetch formulation details
        if (frm.doc.formulation) {
            frm.trigger('fetch_formulation_details');
        }
    },
    
    fetch_formulation_details: function(frm) {
        // You can extend this to fetch and display formulation details
        // in a custom HTML section or dashboard
        frappe.call({
            method: 'frappe.client.get',
            args: {
                doctype: 'Formulation',
                name: frm.doc.formulation
            },
            callback: function(r) {
                if (r.message) {
                    // Store formulation data for potential use
                    frm.formulation_data = r.message;
                }
            }
        });
    },
    
    start_date: function(frm) {
        // Validate date if both start and end dates are set
        if (frm.doc.start_date && frm.doc.end_date) {
            frm.trigger('validate_dates');
        }
    },
    
    end_date: function(frm) {
        // Validate date if both start and end dates are set
        if (frm.doc.start_date && frm.doc.end_date) {
            frm.trigger('validate_dates');
        }
    },
    
    validate_dates: function(frm) {
        if (frm.doc.start_date && frm.doc.end_date) {
            let start_date = new Date(frm.doc.start_date);
            let end_date = new Date(frm.doc.end_date);
            
            if (start_date > end_date) {
                frappe.msgprint({
                    title: __('Invalid Dates'),
                    message: __('Start Date cannot be after End Date'),
                    indicator: 'red'
                });
                frm.fields_dict.end_date.set_value('');
            }
        }
    }
});

// Add a dashboard section for plant trials
frappe.provide('rnd_nutrition.utils');

rnd_nutrition.utils.PlantTrialDashboard = class PlantTrialDashboard {
    constructor(frm) {
        this.frm = frm;
        this.make();
    }
    
    make() {
        let me = this;
        this.dashboard = this.frm.dashboard;
        
        // Add a custom section to the dashboard
        this.section = this.dashboard.add_section(
            __('Trial Information'),
            this.frm.doc.__onload && this.frm.doc.__onload.dashboard_info
        );
        
        this.refresh();
    }
    
    refresh() {
        // Refresh dashboard content
        if (this.frm.doc.formulation) {
            this.show_formulation_info();
        }
    }
    
    show_formulation_info() {
        // Show formulation information in dashboard
        let html = `
            <div class="formulation-info">
                <h5>Formulation Details</h5>
                <p><strong>Linked Formulation:</strong> ${this.frm.doc.formulation}</p>
            </div>
        `;
        
        this.section.html(html);
    }
};
