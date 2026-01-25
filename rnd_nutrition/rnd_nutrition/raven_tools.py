# Copyright (c) 2024, AMB Wellness and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from raven_ai_agent.tools import register_tool, RavenTool

@register_tool
class WordPressPublishTool(RavenTool):
    """Tool for publishing content to WordPress"""
    
    name = "wordpress_publish"
    description = "Publishes a blog post to WordPress site"
    
    parameters = {
        "title": {"type": "string", "description": "Blog post title", "required": True},
        "content": {"type": "string", "description": "Blog post content in HTML", "required": True},
        "status": {"type": "string", "description": "Post status: draft or publish", "default": "draft"},
        "categories": {"type": "array", "description": "List of category names", "default": []},
        "tags": {"type": "array", "description": "List of tag names", "default": []}
    }
    
    def execute(self, title, content, status="draft", categories=None, tags=None):
        from rnd_nutrition.rnd_nutrition.wordpress_api import WordPressAPI
        
        wp = WordPressAPI()
        result = wp.create_post(
            title=title,
            content=content,
            status=status,
            categories=categories or [],
            tags=tags or []
        )
        
        if result.get("success"):
            # Log to Blog Content DocType
            frappe.get_doc({
                "doctype": "Blog Content",
                "title": title,
                "content": content,
                "wordpress_post_id": str(result.get("post_id")),
                "status": "Published" if status == "publish" else "Draft"
            }).insert(ignore_permissions=True)
            
            return {"success": True, "post_id": result.get("post_id"), "url": result.get("url")}
        
        return {"success": False, "error": result.get("error")}

@register_tool
class WordPressUpdateTool(RavenTool):
    """Tool for updating existing WordPress posts"""
    
    name = "wordpress_update"
    description = "Updates an existing WordPress blog post"
    
    parameters = {
        "post_id": {"type": "integer", "description": "WordPress post ID", "required": True},
        "title": {"type": "string", "description": "New title (optional)"},
        "content": {"type": "string", "description": "New content in HTML (optional)"},
        "status": {"type": "string", "description": "New status: draft or publish (optional)"}
    }
    
    def execute(self, post_id, title=None, content=None, status=None):
        from rnd_nutrition.rnd_nutrition.wordpress_api import WordPressAPI
        
        wp = WordPressAPI()
        result = wp.update_post(post_id, title=title, content=content, status=status)
        
        if result.get("success"):
            # Update local record
            local_post = frappe.get_all("Blog Content", 
                filters={"wordpress_post_id": str(post_id)}, limit=1)
            if local_post:
                doc = frappe.get_doc("Blog Content", local_post[0].name)
                if title:
                    doc.title = title
                if content:
                    doc.content = content
                if status:
                    doc.status = "Published" if status == "publish" else "Draft"
                doc.save(ignore_permissions=True)
            
            return {"success": True, "message": "Post updated successfully"}
        
        return {"success": False, "error": result.get("error")}

@register_tool
class BlogContentSearchTool(RavenTool):
    """Tool for searching blog content in Frappe"""
    
    name = "blog_search"
    description = "Searches for blog content in the local database"
    
    parameters = {
        "query": {"type": "string", "description": "Search query", "required": True},
        "status": {"type": "string", "description": "Filter by status: Draft, Published, Scheduled"}
    }
    
    def execute(self, query, status=None):
        filters = {}
        if status:
            filters["status"] = status
        
        results = frappe.get_all("Blog Content",
            filters=filters,
            or_filters=[
                ["title", "like", f"%{query}%"],
                ["content", "like", f"%{query}%"]
            ],
            fields=["name", "title", "status", "wordpress_post_id", "creation"],
            limit=20
        )
        
        return {"success": True, "results": results, "count": len(results)}
