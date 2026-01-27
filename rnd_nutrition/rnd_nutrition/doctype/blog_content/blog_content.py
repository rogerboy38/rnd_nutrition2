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
    
       # ===== STANDALONE FUNCTIONS FOR JAVASCRIPT =====
    
    @frappe.whitelist()
    def publish_to_wordpress(docname):
        """Standalone function for publishing to WordPress (called from JavaScript)"""
        try:
            doc = frappe.get_doc("Blog Content", docname)
            
            # Check if WordPressAPI exists
            try:
                from rnd_nutrition.rnd_nutrition.wordpress_api import WordPressAPI
                wp = WordPressAPI()
                
                # Prepare categories if they exist
                categories = []
                if hasattr(doc, 'categories') and doc.categories:
                    categories = [cat.strip() for cat in doc.categories.split(',') if cat.strip()]
                
                result = wp.create_post(
                    title=doc.title,
                    content=doc.content,
                    status="publish",
                    categories=categories
                )
                
                if result.get("success") and result.get("post_id"):
                    doc.wp_post_id = result.get("post_id")
                    doc.wordpress_url = result.get("url")
                    doc.published_on_wordpress = 1
                    doc.status = "Published"
                    doc.save()
                    frappe.db.commit()
                    
                    return {
                        "success": True,
                        "message": f"? Published to WordPress! Post ID: {result.get('post_id')}",
                        "post_id": result.get("post_id"),
                        "post_url": result.get("url")
                    }
                else:
                    error_msg = result.get("error", "Unknown error")
                    return {
                        "success": False,
                        "message": f"Failed to publish to WordPress: {error_msg}"
                    }
                    
            except ImportError:
                # Fallback to class method if WordPressAPI not available
                return doc.publish_to_wordpress()
                
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "WordPress Publish Error")
            return {
                "success": False,
                "message": f"Error publishing to WordPress: {str(e)}"
            }
    
    @frappe.whitelist()
    def get_wordpress_categories():
        """Get categories from WordPress"""
        try:
            # First try to use the WordPressAPI class
            from rnd_nutrition.rnd_nutrition.wordpress_api import WordPressAPI
            wp = WordPressAPI()
            
            # Check if WordPress settings are configured
            if not hasattr(wp, 'base_url') or not wp.base_url:
                return {"categories": []}
            
            # Make request to get categories
            result = wp._make_request("GET", "categories?per_page=100")
            
            if result.get("success") and result.get("data"):
                categories_data = result.get("data", [])
                categories_list = []
                
                for cat in categories_data:
                    categories_list.append({
                        "id": cat.get("id"),
                        "name": cat.get("name"),
                        "count": cat.get("count", 0)
                    })
                
                return {"categories": categories_list}
            else:
                return {"categories": []}
                
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "WordPress Categories Error")
            return {"categories": []}
    
    @frappe.whitelist()
    def update_wordpress_post(docname):
        """Update an existing WordPress post"""
        try:
            doc = frappe.get_doc("Blog Content", docname)
            
            if not doc.wp_post_id:
                return {
                    "success": False,
                    "message": "This blog hasn't been published to WordPress yet."
                }
            
            # Use the WordPressAPI class
            from rnd_nutrition.rnd_nutrition.wordpress_api import WordPressAPI
            wp = WordPressAPI()
            
            result = wp.update_post(
                post_id=int(doc.wp_post_id),
                title=doc.title,
                content=doc.content
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

    
