/**
 * RND Nutrition Bundle
 * Auto-generated to resolve 404 errors
 */

(function() {
    'use strict';
    
    console.log('RND Nutrition bundle loaded');
    
    // Add any RND Nutrition specific JavaScript here
    frappe.provide('rnd_nutrition');
    
    // Example: Custom formatter for RND Nutrition doctypes
    rnd_nutrition.format_nutrition_value = function(value, precision) {
        if (value === null || value === undefined) return '-';
        return flt(value, precision || 2);
    };
    
    // Example: Custom validation
    rnd_nutrition.validate_nutrition_input = function(frm, fieldname) {
        var value = frm.doc[fieldname];
        if (value && value < 0) {
            frappe.msgprint(__('Nutrition values cannot be negative'));
            frappe.validated = false;
        }
    };
    
    // Hook into form events if needed
    frappe.ui.form.on('Item', {
        refresh: function(frm) {
            // Add custom buttons or logic for items related to nutrition
            if (frm.doc.item_group === 'Nutrition') {
                frm.add_custom_button(__('Nutrition Analysis'), function() {
                    frappe.call({
                        method: 'rnd_nutrition.api.analyze_nutrition',
                        args: {
                            item_code: frm.doc.name
                        }
                    });
                });
            }
        }
    });
    
})();
