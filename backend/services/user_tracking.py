import uuid
import hashlib
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import Request


class UserTrackingService:
    """Service for tracking user sessions and transactions"""
    
    @staticmethod
    def generate_user_id() -> str:
        """Generate a unique user ID"""
        return str(uuid.uuid4())
    
    @staticmethod
    def generate_session_id() -> str:
        """Generate a unique session ID"""
        return str(uuid.uuid4())
    
    @staticmethod
    def get_user_fingerprint(request: Request) -> str:
        """Create a user fingerprint based on request data"""
        # Combine IP, User-Agent, and other identifying info
        ip = request.client.host
        user_agent = request.headers.get("user-agent", "")
        
        # Create a hash of identifying information
        fingerprint_data = f"{ip}:{user_agent}"
        return hashlib.md5(fingerprint_data.encode()).hexdigest()
    
    @staticmethod
    def extract_user_info(request: Request) -> Dict[str, Any]:
        """Extract user information from request"""
        return {
            "ip_address": request.client.host,
            "user_agent": request.headers.get("user-agent", ""),
            "session_id": UserTrackingService.generate_session_id(),
            "user_fingerprint": UserTrackingService.get_user_fingerprint(request)
        }
    
    @staticmethod
    def create_user_identifier(email: str = None, name: str = None) -> str:
        """Create a user identifier from email or name"""
        if email:
            return f"user_{hashlib.md5(email.encode()).hexdigest()[:8]}"
        elif name:
            return f"user_{hashlib.md5(name.encode()).hexdigest()[:8]}"
        else:
            return f"user_{uuid.uuid4().hex[:8]}"


# Global instance
user_tracking = UserTrackingService()
