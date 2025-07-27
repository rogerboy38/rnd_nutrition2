frappe.ui.form.on('Formulation Change Log', {
    refresh: function(frm) {
        if (!frm.doc.__islocal) {
            frm.add_custom_button(__('View Formulation'), function() {
                frappe.set_route('Form', 'Formulation', frm.doc.formulation);
            });
        }
        
        // Add dashboard for changes
        if (frm.doc.ingredient_changes && frm.doc.ingredient_changes.length > 0) {
            frm.dashboard.add_section(
                frappe.render_template('ingredient_changes_summary', {
                    changes: frm.doc.ingredient_changes
                })
            );
        }
    },
    
    formulation: function(frm) {
        if (frm.doc.formulation) {
            frappe.call({
                method: 'rnd_nutrition.rnd_nutrition.doctype.formulation_change_log.formulation_change_log.get_formulation_details',
                args: {
                    formulation: frm.doc.formulation
                },
                callback: function(r) {
                    if (r.message) {
                        frm.set_df_property('description', 'description', 
                            `Current Formulation Details:\n${JSON.stringify(r.message, null, 2)}`);
                    }
                }
            });
        }
    },
    
    change_type: function(frm) {
        if (frm.doc.change_type === 'Ingredient Change') {
            frm.set_value('description', 'Please list all ingredient changes in the table below.');
        }
    }
});

frappe.templates['ingredient_changes_summary'] = `
<div class="ingredient-changes-summary">
    <h5>Ingredient Changes Summary</h5>
    <table class="table table-bordered">
        <thead>
            <tr>
                <th>Ingredient</th>
                <th>Old Qty</th>
                <th>New Qty</th>
                <th>Unit</th>
                <th>Change</th>
            </tr>
        </thead>
        <tbody>
            {% for change in changes %}
            <tr>
                <td>{{ change.ingredient }}</td>
                <td>{{ change.old_quantity }}</td>
                <td>{{ change.new_quantity }}</td>
                <td>{{ change.uom }}</td>
                <td>{{ ((change.new_quantity - change.old_quantity) / change.old_quantity * 100).toFixed(2) }}%</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
`;
