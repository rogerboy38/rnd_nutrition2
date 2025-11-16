frappe.ui.form.on('Research Project', {
    refresh: function(frm) {
        // Add custom buttons
        frm.add_custom_button(__('Set Active'), function() {
            frm.set_value('status', 'Active');
            frm.save();
        });
        
        frm.add_custom_button(__('Mark Completed'), function() {
            frm.set_value('status', 'Completed');
            frm.save();
        });
        
        // Add timeline button if project has related trials
        if (frm.doc.name) {
            frm.add_custom_button(__('View Related Trials'), function() {
                frappe.set_route('List', 'Plant Trial', {
                    'research_project': frm.doc.name
                });
            });
        }
    },
    
    start_date: function(frm) {
        // Validate dates
        if (frm.doc.start_date && frm.doc.end_date) {
            frm.trigger('validate_dates');
        }
    },
    
    end_date: function(frm) {
        // Validate dates
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
    },
    
    status: function(frm) {
        // Update description based on status
        if (frm.doc.status === 'Completed' && frm.doc.end_date === null) {
            frm.set_value('end_date', frappe.datetime.get_today());
        }
    }
});
