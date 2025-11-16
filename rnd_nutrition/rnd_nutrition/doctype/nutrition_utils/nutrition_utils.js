frappe.ui.form.on('Nutrition Utils', {
    refresh: function(frm) {
        // Add custom buttons
        frm.add_custom_button(__('Test API Connection'), function() {
            frappe.call({
                method: 'rnd_nutrition.utils.test_api_connection',
                args: {
                    endpoint: frm.doc.api_endpoint,
                    api_key: frm.doc.api_key
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.msgprint(__('API Connection Successful'));
                    } else {
                        frappe.msgprint(__('API Connection Failed'));
                    }
                }
            });
        }).toggle(frm.doc.enable_nutrition_api);
    },
    
    enable_nutrition_api: function(frm) {
        // Toggle API fields visibility
        frm.toggle_display(['api_endpoint', 'api_key'], frm.doc.enable_nutrition_api);
    }
});
