# Copyright (c) 2026, AMB-Wellness and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class BlogContent(Document):
    def before_save(self):
        if not self.schema_markup and self.title:
            self.schema_markup = self.generate_schema()
    
    def generate_schema(self):
        """Generate Schema.org markup for SEO"""
        import json
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": self.title,
            "author": {
                "@type": "Organization",
                "name": "AMB Wellness"
            },
            "publisher": {
                "@type": "Organization",
                "name": "AMB Wellness",
                "logo": {
                    "@type": "ImageObject",
                    "url": "https://ambwellness.com/logo.png"
                }
            },
            "description": self.meta_description or "",
            "keywords": self.keywords or ""
        }
        return json.dumps(schema, indent=2)
    
    @frappe.whitelist()
    def publish_to_wordpress(self):
        """Publish this blog content to WordPress"""
        from rnd_nutrition.rnd_nutrition.utils.wordpress_api import WordPressAPI
        
        wp = WordPressAPI()
        result = wp.create_post(
            title=self.title,
            content=self.content,
            schema_markup=self.schema_markup,
            meta_description=self.meta_description
        )
        
        if result.get("id"):
            self.wp_post_id = result.get("id")
            self.status = "Published"
            self.save()
            
        return result
		
    @frappe.whitelist()
    def update_wordpress_post(docname, post_id=None, title=None, content=None):
        """Update an existing WordPress post"""
        try:
            from rnd_nutrition.rnd_nutrition.wordpress_api import WordPressAPI
            
            wp = WordPressAPI()
            doc = frappe.get_doc("Blog Content", docname)
            
            # Use provided post_id or get from document
            post_id_to_update = post_id or doc.wp_post_id
            
            if not post_id_to_update:
                return {
                    "success": False,
                    "message": "No WordPress post ID found. Publish the post first."
                }
            
            result = wp.update_post(
                post_id=int(post_id_to_update),
                title=title or doc.title,
                content=content or doc.content
            )
            
            if result.get("success"):
                return {
                    "success": True,
                    "message": f"? WordPress post updated successfully!"
                }
            else:
                error_msg = result.get("error", "Unknown error")
                return {
                    "success": False,
                    "message": f"Failed to update WordPress post: {error_msg}"
                }
                
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "WordPress Update Error")
            return {
                "success": False,
                "message": f"Error updating WordPress post: {str(e)}"
            }
