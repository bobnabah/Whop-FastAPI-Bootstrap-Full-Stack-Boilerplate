import os
import hmac
import hashlib
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class WhopService:
    """Service for Whop webhook verification and checkout management"""
    
    def __init__(self):
        # Load configuration from environment variables
        self.webhook_secret = os.getenv("WHOP_WEBHOOK_SECRET")
        self.plan_id = os.getenv("WHOP_PLAN_ID")
        self.checkout_link = os.getenv("WHOP_CHECKOUT_LINK")
        
        # Validate required configuration
        if not self.webhook_secret:
            logger.warning("WHOP_WEBHOOK_SECRET not set - webhook verification will fail")
        if not self.plan_id:
            logger.warning("WHOP_PLAN_ID not set - checkout may not work properly")
        if not self.checkout_link:
            logger.warning("WHOP_CHECKOUT_LINK not set - checkout will fail")
    
    def get_checkout_url(self, user_id: str, metadata: Dict[str, Any] = None) -> str:
        """
        Generate Whop checkout URL with user tracking parameters
        No API needed - just direct link with tracking
        """
        base_url = f"https://whop.com/checkout/{self.checkout_link}"
        
        # Add tracking parameters
        params = []
        if user_id:
            params.append(f"user_id={user_id}")
        if metadata:
            for key, value in metadata.items():
                params.append(f"{key}={value}")
        
        if params:
            return f"{base_url}?{'&'.join(params)}"
        return base_url
    
    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """
        Verify Whop webhook signature using HMAC-SHA256
        Based on Whop's webhook security documentation
        """
        try:
            # Remove 'sha256=' prefix if present
            if signature.startswith('sha256='):
                signature = signature[7:]
            
            # Create expected signature
            expected_signature = hmac.new(
                self.webhook_secret.encode('utf-8'),
                payload,
                hashlib.sha256
            ).hexdigest()
            
            # Secure comparison to prevent timing attacks
            return hmac.compare_digest(expected_signature, signature)
            
        except Exception as e:
            logger.error(f"Webhook signature verification failed: {str(e)}")
            return False
    
    def extract_session_id_from_webhook(self, webhook_data: Dict[str, Any]) -> str:
        """Extract session ID from webhook data"""
        data = webhook_data.get("data", {})
        return (
            data.get("checkout_session_id") or 
            data.get("session_id") or 
            data.get("id") or
            webhook_data.get("checkout_session_id") or
            ""
        )

# Global instance
whop_service = WhopService()