"""
Feature Flags for AI Integration
Enables gradual rollout of AI features
"""

import frappe
from frappe import _

class AIFeatureFlags:
    """Manage AI feature flags for safe rollout"""
    
    def __init__(self):
        self.flags = {
            "ai_recommendations": False,
            "predictive_analytics": False,
            "conversational_ai": False,
            "vector_search": False,
            "auto_formulation": False
        }
        self.load_flags()
    
    def load_flags(self):
        """Load feature flags from database or environment"""
        try:
            # Try to load from site config first
            site_config = frappe.get_site_config()
            ai_flags = site_config.get("ai_feature_flags", {})
            
            # Update flags with configuration
            for flag in self.flags:
                if flag in ai_flags:
                    self.flags[flag] = ai_flags[flag]
            
            # Environment variable override
            import os
            for flag in self.flags:
                env_var = f"AI_{flag.upper()}"
                if os.getenv(env_var):
                    self.flags[flag] = os.getenv(env_var).lower() in ['true', '1', 'yes']
                    
        except Exception as e:
            frappe.log_error(f"Failed to load AI feature flags: {e}")
    
    def is_enabled(self, feature_name):
        """Check if a specific AI feature is enabled"""
        return self.flags.get(feature_name, False)
    
    def enable_feature(self, feature_name):
        """Enable a specific AI feature"""
        if feature_name in self.flags:
            self.flags[feature_name] = True
            frappe.logger().info(f"AI feature enabled: {feature_name}")
    
    def disable_feature(self, feature_name):
        """Disable a specific AI feature"""
        if feature_name in self.flags:
            self.flags[feature_name] = False
            frappe.logger().info(f"AI feature disabled: {feature_name}")
    
    def get_status(self):
        """Get status of all AI features"""
        return self.flags

# Global feature flags instance
ai_feature_flags = AIFeatureFlags()
