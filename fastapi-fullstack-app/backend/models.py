from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.sql import func
from .database import Base


class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(String, index=True, nullable=False)
    checkout_link = Column(String, index=True, nullable=False)
    amount = Column(Float, nullable=False)
    
    # Payment status and metadata
    status = Column(String, default='pending', index=True)  # pending, completed, failed, cancelled
    payment_method = Column(String)
    currency = Column(String, default='USD')
    
    # User information
    customer_email = Column(String, index=True)
    customer_name = Column(String)
    user_id = Column(String, index=True)  # Unique user identifier
    session_id = Column(String, index=True)  # Internal session tracking
    whop_session_id = Column(String, index=True)  # Whop checkout session ID (ch_abc123)
    whop_checkout_url = Column(String)  # Whop hosted checkout URL
    ip_address = Column(String)  # User's IP address
    user_agent = Column(String)  # Browser information
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Additional metadata
    extra_data = Column(Text)  # JSON string for additional data
    webhook_received = Column(Boolean, default=False)
    
    # Error handling
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)

    def __repr__(self):
        return f"<Transaction(id={self.id}, plan_id={self.plan_id}, status={self.status}, amount={self.amount})>"