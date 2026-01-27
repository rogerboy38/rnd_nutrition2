frappe.ui.form.on('Blog Content', {
    refresh: function(frm) {
        // Add Publish to WordPress button
        if (!frm.doc.published_on_wordpress) {
            frm.add_custom_button(__('Publish to WordPress'), function() {
                frappe.call({
                    method: 'rnd_nutrition.rnd_nutrition.doctype.blog_content.blog_content.publish_to_wordpress',
                    args: {
                        docname: frm.doc.name
                    },
                    callback: function(r) {
                        if (r.message && r.message.success) {
                            frappe.show_alert({
                                message: r.message.message,
                                indicator: 'green'
                            });
                            frm.reload_doc();
                        } else {
                            frappe.show_alert({
                                message: r.message.message || 'Failed to publish',
                                indicator: 'red'
                            });
                        }
                    },
                    freeze: true,
                    freeze_message: __('Publishing to WordPress...')
                });
            }, __('Actions'));
        } else {
            // Add Update WordPress Post button if already published
            frm.add_custom_button(__('Update WordPress Post'), function() {
                frappe.call({
                    method: 'rnd_nutrition.rnd_nutrition.doctype.blog_content.blog_content.update_wordpress_post',
                    args: {
                        docname: frm.doc.name,
                        post_id: frm.doc.wp_post_id,
                        title: frm.doc.title,
                        content: frm.doc.content
                    },
                    callback: function(r) {
                        if (r.message && r.message.success) {
                            frappe.show_alert({
                                message: r.message.message,
                                indicator: 'green'
                            });
                            frm.reload_doc();
                        } else {
                            frappe.show_alert({
                                message: r.message.message || 'Failed to update',
                                indicator: 'red'
                            });
                        }
                    },
                    freeze: true,
                    freeze_message: __('Updating WordPress post...')
                });
            }, __('Actions'));
        }
        
        // Add Get WordPress Categories button
        frm.add_custom_button(__('Get WordPress Categories'), function() {
            frappe.call({
                method: 'rnd_nutrition.rnd_nutrition.doctype.blog_content.blog_content.get_wordpress_categories',
                callback: function(r) {
                    if (r.message && r.message.categories) {
                        let categories = r.message.categories;
                        let category_list = categories.map(cat => `${cat.name} (${cat.count})`).join(', ');
                        
                        frappe.msgprint({
                            title: __('WordPress Categories'),
                            message: __('Available categories:') + '<br><br>' + category_list
                        });
                    } else {
                        frappe.msgprint(__('No categories found or failed to fetch from WordPress.'));
                    }
                },
                freeze: true,
                freeze_message: __('Fetching categories from WordPress...')
            });
        }, __('Tools'));
        
        // Add link to WordPress post if published
        if (frm.doc.published_on_wordpress && frm.doc.wordpress_url) {
            frm.add_custom_button(__('View on WordPress'), function() {
                window.open(frm.doc.wordpress_url, '_blank');
            }, __('Links'));
            
            if (frm.doc.wp_post_id) {
                let edit_url = `https://acemannan-acetypol.com/wp-admin/post.php?post=${frm.doc.wp_post_id}&action=edit`;
                frm.add_custom_button(__('Edit on WordPress'), function() {
                    window.open(edit_url, '_blank');
                }, __('Links'));
            }
        }
    }
});
