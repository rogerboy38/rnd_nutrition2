frappe.ui.form.on('Change Log Ingredient Reference', {
    refresh: function(frm) {
        // This is a child table, so most logic will be handled by the parent
    },
    
    ingredient: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.ingredient) {
            frappe.call({
                method: 'frappe.client.get_value',
                args: {
                    doctype: 'Item',
                    fieldname: 'item_name',
                    filters: { name: row.ingredient }
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, 'ingredient_name', r.message.item_name);
                    }
                }
            });
        }
    },
    
    old_quantity: function(frm, cdt, cdn) {
        calculate_change_percentage(frm, cdt, cdn);
    },
    
    new_quantity: function(frm, cdt, cdn) {
        calculate_change_percentage(frm, cdt, cdn);
    }
});

function calculate_change_percentage(frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    if (row.old_quantity && row.new_quantity && row.old_quantity != 0) {
        let change = ((row.new_quantity - row.old_quantity) / row.old_quantity) * 100;
        frappe.model.set_value(cdt, cdn, 'change_percentage', change);
    }
}
