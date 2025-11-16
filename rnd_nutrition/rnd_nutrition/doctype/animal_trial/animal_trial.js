frappe.ui.form.on('Animal Trial', {
    refresh: function(frm) {
        // Add custom buttons
        frm.add_custom_button(__('Create from Formulation'), function() {
            frm.trigger('create_from_formulation');
        });
        
        frm.add_custom_button(__('Trial Summary'), function() {
            frm.trigger('show_trial_summary');
        });
        
        frm.add_custom_button(__('Generate Report'), function() {
            frm.trigger('generate_report');
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
        
        // Initialize dashboard
        if (!frm.dashboard_initialized) {
            new rnd_nutrition.utils.AnimalTrialDashboard(frm);
            frm.dashboard_initialized = true;
        }
    },
    
    create_from_formulation: function(frm) {
        // Open dialog to select formulation
        let d = new frappe.ui.Dialog({
            title: __('Create Animal Trial from Formulation'),
            fields: [
                {
                    label: __('Formulation'),
                    fieldname: 'formulation',
                    fieldtype: 'Link',
                    options: 'Formulation',
                    reqd: 1,
                    get_query: function() {
                        return {
                            filters: {
                                'purpose': 'Animal Nutrition'
                            }
                        };
                    }
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
                    method: 'rnd_nutrition.rnd_nutrition.doctype.animal_trial.animal_trial.create_animal_trial_from_formulation',
                    args: {
                        formulation_name: values.formulation,
                        trial_name: values.trial_name || null
                    },
                    callback: function(r) {
                        if (r.message) {
                            frappe.msgprint(__('Animal Trial {0} created successfully', [r.message]));
                            frappe.set_route('Form', 'Animal Trial', r.message);
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
            method: 'rnd_nutrition.rnd_nutrition.doctype.animal_trial.animal_trial.get_animal_trial_summary',
            args: {
                animal_trial_name: frm.doc.name
            },
            callback: function(r) {
                if (r.message) {
                    let summary = r.message;
                    let message = `
                        <h4>Animal Trial Summary</h4>
                        <p><strong>Trial Name:</strong> ${summary.trial_name}</p>
                        <p><strong>Formulation:</strong> ${summary.formulation}</p>
                        <p><strong>Start Date:</strong> ${summary.start_date}</p>
                        <p><strong>Status:</strong> ${summary.status}</p>
                        <p><strong>Has Results:</strong> ${summary.has_results ? 'Yes' : 'No'}</p>
                        <p><strong>Type:</strong> ${summary.trial_type}</p>
                    `;
                    
                    frappe.msgprint({
                        title: __('Animal Trial Summary'),
                        message: message,
                        indicator: 'blue'
                    });
                }
            }
        });
    },
    
    generate_report: function(frm) {
        if (!frm.doc.name) {
            frappe.msgprint(__('Please save the document first'));
            return;
        }
        
        frappe.call({
            method: 'rnd_nutrition.rnd_nutrition.doctype.animal_trial.animal_trial.get_animal_trial_report',
            args: {
                animal_trial_name: frm.doc.name
            },
            callback: function(r) {
                if (r.message) {
                    let report = r.message;
                    let message = `
                        <h4>Animal Trial Report</h4>
                        <div style="border: 1px solid #d1d8dd; padding: 15px; border-radius: 5px;">
                            <h5>Trial Information</h5>
                            <p><strong>Name:</strong> ${report.trial_info.name}</p>
                            <p><strong>Trial Name:</strong> ${report.trial_info.trial_name}</p>
                            <p><strong>Start Date:</strong> ${report.trial_info.start_date}</p>
                            <p><strong>Status:</strong> ${report.trial_info.status}</p>
                            <p><strong>Results Summary:</strong> ${report.trial_info.results_summary || 'No results yet'}</p>
                    `;
                    
                    if (report.formulation_info) {
                        message += `
                            <h5>Formulation Information</h5>
                            <p><strong>Formulation:</strong> ${report.formulation_info.formulation_name}</p>
                            <p><strong>Purpose:</strong> ${report.formulation_info.purpose}</p>
                        `;
                    }
                    
                    message += `</div>`;
                    
                    frappe.msgprint({
                        title: __('Animal Trial Report'),
                        message: message,
                        indicator: 'green',
                        wide: true
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
            title: __('Complete Animal Trial'),
            fields: [
                {
                    label: __('Results'),
                    fieldname: 'results',
                    fieldtype: 'Text Editor',
                    default: frm.doc.results,
                    description: __('Add trial results, observations, and animal health data')
                }
            ],
            primary_action_label: __('Complete Trial'),
            primary_action: function(values) {
                frappe.call({
                    method: 'rnd_nutrition.rnd_nutrition.doctype.animal_trial.animal_trial.complete_animal_trial',
                    args: {
                        animal_trial_name: frm.doc.name,
                        results: values.results
                    },
                    callback: function(r) {
                        if (r.message) {
                            frappe.msgprint(__('Animal Trial completed successfully'));
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
                            `Animal Trial - ${r.message.formulation_name}`);
                    }
                });
        }
        
        // Validate formulation purpose
        if (frm.doc.formulation) {
            frm.trigger('validate_formulation_purpose');
        }
    },
    
    validate_formulation_purpose: function(frm) {
        // Check if formulation is for animal nutrition
        frappe.db.get_value('Formulation', frm.doc.formulation, 'purpose')
            .then(r => {
                if (r.message && r.message.purpose !== 'Animal Nutrition') {
                    frappe.msgprint({
                        title: __('Invalid Formulation'),
                        message: __('Selected formulation is not intended for Animal Nutrition'),
                        indicator: 'red'
                    });
                    frm.set_value('formulation', '');
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

// Animal Trial Dashboard
rnd_nutrition.utils.AnimalTrialDashboard = class AnimalTrialDashboard {
    constructor(frm) {
        this.frm = frm;
        this.make();
    }
    
    make() {
        let me = this;
        this.dashboard = this.frm.dashboard;
        
        // Add a custom section to the dashboard
        this.section = this.dashboard.add_section(
            __('Animal Trial Information'),
            this.frm.doc.__onload && this.frm.doc.__onload.dashboard_info
        );
        
        this.refresh();
    }
    
    refresh() {
        // Refresh dashboard content
        if (this.frm.doc.formulation) {
            this.show_formulation_info();
        }
        
        this.show_trial_status();
    }
    
    show_formulation_info() {
        // Show formulation information in dashboard
        let html = `
            <div class="formulation-info">
                <h5>Formulation Details</h5>
                <p><strong>Linked Formulation:</strong> ${this.frm.doc.formulation}</p>
                <p><strong>Trial Type:</strong> Animal Nutrition</p>
            </div>
        `;
        
        this.section.html(html);
    }
    
    show_trial_status() {
        // Show trial status information
        let status_html = `
            <div class="trial-status">
                <h5>Trial Status</h5>
                <p><strong>Current Status:</strong> ${this.frm.doc.docstatus === 0 ? 'Draft' : 'Completed'}</p>
                <p><strong>Results:</strong> ${this.frm.doc.results ? 'Available' : 'Not Available'}</p>
            </div>
        `;
        
        this.section.append(status_html);
    }
};
