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
