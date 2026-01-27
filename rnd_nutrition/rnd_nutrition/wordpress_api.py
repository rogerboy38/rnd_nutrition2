# Copyright (c) 2024, AMB Wellness and contributors
# For license information, please see license.txt

import frappe
import requests
import base64
from frappe import _

class WordPressAPI:
    """WordPress REST API wrapper for blog operations"""
    
    def __init__(self):
        self.settings = self._get_settings()
        self.base_url = self.settings.get("site_url", "").rstrip("/")
        self.api_url = f"{self.base_url}/wp-json/wp/v2"
        self.auth = self._get_auth()
    
    def _get_settings(self):
        """Get WordPress settings from DocType"""
        try:
            settings = frappe.get_single("WordPress Settings")
            return {
                "site_url": settings.site_url,
                "username": settings.username,
                "app_password": settings.get_password("app_password")
            }
        except Exception as e:
            frappe.log_error(f"Failed to get WordPress settings: {e}")
            return {}
    
    def _get_auth(self):
        """Generate Basic Auth header"""
        username = self.settings.get("username", "")
        password = self.settings.get("app_password", "")
        if username and password:
            credentials = f"{username}:{password}"
            encoded = base64.b64encode(credentials.encode()).decode()
            return {"Authorization": f"Basic {encoded}"}
        return {}
    
    def _make_request(self, method, endpoint, data=None):
        """Make API request to WordPress"""
        url = f"{self.api_url}/{endpoint}"
        headers = {
            "Content-Type": "application/json",
			            "Accept": "application/json, text/plain, */*",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": self.base_url,
            "Referer": f"{self.base_url}/wp-admin/",
            **self.auth
        }
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=30)
            elif method == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == "PUT":
                response = requests.put(url, json=data, headers=headers, timeout=30)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                return {"success": False, "error": f"Unsupported method: {method}"}
            
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        
        except requests.exceptions.RequestException as e:
            frappe.log_error(f"WordPress API error: {e}")
            return {"success": False, "error": str(e)}
    
    def create_post(self, title, content, status="draft", categories=None, tags=None):
        """Create a new WordPress post"""
        data = {
            "title": title,
            "content": content,
            "status": status
        }
        
        if categories:
            cat_ids = self._get_or_create_terms("categories", categories)
            data["categories"] = cat_ids
        
        if tags:
            tag_ids = self._get_or_create_terms("tags", tags)
            data["tags"] = tag_ids
        
        result = self._make_request("POST", "posts", data)
        
        if result.get("success"):
            post_data = result.get("data", {})
            return {
                "success": True,
                "post_id": post_data.get("id"),
                "url": post_data.get("link")
            }
        
        return result
    
    def update_post(self, post_id, title=None, content=None, status=None):
        """Update an existing WordPress post"""
        data = {}
        if title:
            data["title"] = title
        if content:
            data["content"] = content
        if status:
            data["status"] = status
        
        if not data:
            return {"success": False, "error": "No update data provided"}
        
        return self._make_request("PUT", f"posts/{post_id}", data)
    
    def get_post(self, post_id):
        """Get a WordPress post by ID"""
        return self._make_request("GET", f"posts/{post_id}")
    
    def delete_post(self, post_id):
        """Delete a WordPress post"""
        return self._make_request("DELETE", f"posts/{post_id}")
    
    def _get_or_create_terms(self, taxonomy, terms):
        """Get or create taxonomy terms (categories/tags)"""
        endpoint = taxonomy
        term_ids = []
        
        for term_name in terms:
            search_result = self._make_request("GET", f"{endpoint}?search={term_name}")
            
            if search_result.get("success") and search_result.get("data"):
                existing = search_result.get("data", [])
                if existing:
                    term_ids.append(existing[0].get("id"))
                    continue
            
            create_result = self._make_request("POST", endpoint, {"name": term_name})
            if create_result.get("success"):
                term_ids.append(create_result.get("data", {}).get("id"))
        
        return term_ids


@frappe.whitelist()
def publish_to_wordpress(title, content, status="draft"):
    """Publish content to WordPress (whitelisted for frontend)"""
    wp = WordPressAPI()
    return wp.create_post(title, content, status)

@frappe.whitelist()
def update_wordpress_post(post_id, title=None, content=None, status=None):
    """Update WordPress post (whitelisted for frontend)"""
    wp = WordPressAPI()
    return wp.update_post(int(post_id), title, content, status)
