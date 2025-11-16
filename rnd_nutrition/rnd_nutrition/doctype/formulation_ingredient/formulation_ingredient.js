frappe.ui.form.on('Formulation Ingredient', {
    ingredient_name: function(frm) {
        // Auto-fetch nutritional data when ingredient is selected
        if (frm.doc.ingredient_name) {
            frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'Nutrition Item',
                    name: frm.doc.ingredient_name
                },
                callback: function(r) {
                    if (r.message) {
                        frm.set_value('calories', r.message.calories || 0);
                        frm.set_value('protein', r.message.protein || 0);
                        frm.set_value('carbohydrates', r.message.carbohydrates || 0);
                        frm.set_value('fat', r.message.fat || 0);
                    }
                }
            });
        }
    }
});
