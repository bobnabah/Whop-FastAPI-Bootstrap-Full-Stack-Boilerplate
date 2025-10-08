from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from ..database import get_db
from ..models import Transaction
from ..services.user_tracking import user_tracking
from ..services.whop_service import whop_service
from ..services.invoice_service import invoice_service
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from fastapi.responses import StreamingResponse
import json
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class TransactionCreate(BaseModel):
    amount: float
    plan_id: str
    customer_email: Optional[EmailStr] = None
    customer_name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class CheckoutSessionCreate(BaseModel):
    plan_id: str
    amount: float
    customer_email: Optional[EmailStr] = None
    customer_name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@router.post("/create-cerebra-checkout")
async def create_cerebra_checkout(
    checkout_data: CheckoutSessionCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Create a checkout record and return Whop checkout URL"""
    try:
        # Extract user information from request
        user_info = user_tracking.extract_user_info(request)
        
        # Create user identifier
        user_id = user_tracking.create_user_identifier(
            email=checkout_data.customer_email,
            name=checkout_data.customer_name
        )
        
        # Check for existing completed transactions (prevent duplicates)
        existing_transaction = db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.status == "completed"
        ).first()
        
        if existing_transaction:
            raise HTTPException(status_code=400, detail="User has already purchased this plan")
        
        # Generate checkout URL with tracking
        checkout_url = whop_service.get_checkout_url(
            user_id=user_id,
            metadata={
                "tier": "premium",
                "source": "cerebra_app",
                **(checkout_data.metadata or {})
            }
        )
        
        # Create transaction record
        db_transaction = Transaction(
            plan_id=checkout_data.plan_id,
            checkout_link=whop_service.checkout_link,
            amount=checkout_data.amount,
            customer_email=checkout_data.customer_email,
            customer_name=checkout_data.customer_name,
            user_id=user_id,
            session_id=user_info["session_id"],
            whop_checkout_url=checkout_url,
            ip_address=user_info["ip_address"],
            user_agent=user_info["user_agent"],
            status='pending',
            extra_data=json.dumps({
                **(checkout_data.metadata or {}),
                "user_fingerprint": user_info["user_fingerprint"],
                "tracking_data": user_info
            })
        )
        
        db.add(db_transaction)
        db.commit()
        db.refresh(db_transaction)
        
        return {
            "checkout_url": checkout_url,
            "transaction_id": db_transaction.id,
            "user_id": user_id,
            "status": "created"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Checkout creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create checkout: {str(e)}")


@router.post("/transactions/")
async def create_transaction(
    transaction: TransactionCreate, 
    request: Request,
    db: Session = Depends(get_db)
):
    """Create a transaction record for the $5 plan with user tracking (legacy endpoint)"""
    try:
        # Extract user information from request
        user_info = user_tracking.extract_user_info(request)
        
        # Create user identifier
        user_id = user_tracking.create_user_identifier(
            email=transaction.customer_email,
            name=transaction.customer_name
        )
        
        # Create transaction record with user tracking
        db_transaction = Transaction(
            plan_id=transaction.plan_id,
            checkout_link="plan_oPKqUgfiFWUVO",  # Your checkout link
            amount=transaction.amount,
            customer_email=transaction.customer_email,
            customer_name=transaction.customer_name,
            user_id=user_id,
            session_id=user_info["session_id"],
            ip_address=user_info["ip_address"],
            user_agent=user_info["user_agent"],
            status='pending',
            extra_data=json.dumps({
                **(transaction.metadata or {}),
                "user_fingerprint": user_info["user_fingerprint"],
                "tracking_data": user_info
            })
        )
        
        db.add(db_transaction)
        db.commit()
        db.refresh(db_transaction)
        
        return {
            "id": db_transaction.id,
            "plan_id": db_transaction.plan_id,
            "checkout_link": db_transaction.checkout_link,
            "amount": db_transaction.amount,
            "status": db_transaction.status,
            "customer_email": db_transaction.customer_email,
            "user_id": db_transaction.user_id,
            "session_id": db_transaction.session_id
        }
        
    except Exception as e:
        logger.error(f"Transaction creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create transaction: {str(e)}")


@router.get("/transactions/{transaction_id}")
def read_transaction(transaction_id: int, db: Session = Depends(get_db)):
    """Get transaction details"""
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return {
        "id": transaction.id,
        "plan_id": transaction.plan_id,
        "checkout_link": transaction.checkout_link,
        "amount": transaction.amount,
        "status": transaction.status,
        "customer_email": transaction.customer_email,
        "customer_name": transaction.customer_name,
        "user_id": transaction.user_id,
        "session_id": transaction.session_id,
        "ip_address": transaction.ip_address,
        "created_at": transaction.created_at,
        "completed_at": transaction.completed_at
    }


@router.get("/transactions/")
def list_transactions(
    skip: int = 0, 
    limit: int = 100, 
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List transactions with optional filtering"""
    query = db.query(Transaction)
    
    if status:
        query = query.filter(Transaction.status == status)
    
    transactions = query.offset(skip).limit(limit).all()
    
    return [
        {
            "id": t.id,
            "plan_id": t.plan_id,
            "amount": t.amount,
            "status": t.status,
            "customer_email": t.customer_email,
            "customer_name": t.customer_name,
            "user_id": t.user_id,
            "session_id": t.session_id,
            "ip_address": t.ip_address,
            "created_at": t.created_at,
            "completed_at": t.completed_at
        }
        for t in transactions
    ]


@router.get("/transactions/user/{user_id}")
def get_user_transactions(user_id: str, db: Session = Depends(get_db)):
    """Get all transactions for a specific user"""
    transactions = db.query(Transaction).filter(Transaction.user_id == user_id).all()
    
    return [
        {
            "id": t.id,
            "plan_id": t.plan_id,
            "amount": t.amount,
            "status": t.status,
            "customer_email": t.customer_email,
            "customer_name": t.customer_name,
            "session_id": t.session_id,
            "ip_address": t.ip_address,
            "created_at": t.created_at,
            "completed_at": t.completed_at
        }
        for t in transactions
    ]


@router.get("/transactions/session/{session_id}")
def get_session_transactions(session_id: str, db: Session = Depends(get_db)):
    """Get all transactions for a specific session"""
    transactions = db.query(Transaction).filter(Transaction.session_id == session_id).all()
    
    return [
        {
            "id": t.id,
            "plan_id": t.plan_id,
            "amount": t.amount,
            "status": t.status,
            "customer_email": t.customer_email,
            "customer_name": t.customer_name,
            "user_id": t.user_id,
            "ip_address": t.ip_address,
            "created_at": t.created_at,
            "completed_at": t.completed_at
        }
        for t in transactions
    ]


@router.get("/validate-session/{whop_session_id}")
async def validate_whop_session(
    whop_session_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Validate that a user can access a specific Whop session"""
    try:
        # Get user info from current request
        user_info = user_tracking.extract_user_info(request)
        current_ip = user_info["ip_address"]
        current_fingerprint = user_info["user_fingerprint"]
        
        # Find transaction with this Whop session ID
        transaction = db.query(Transaction).filter(
            Transaction.whop_session_id == whop_session_id
        ).first()
        
        if not transaction:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Parse stored tracking data
        try:
            extra_data = json.loads(transaction.extra_data or "{}")
            stored_fingerprint = extra_data.get("user_fingerprint")
        except:
            stored_fingerprint = None
        
        # Validate session ownership
        is_valid = (
            transaction.ip_address == current_ip or 
            stored_fingerprint == current_fingerprint
        )
        
        if not is_valid:
            raise HTTPException(status_code=403, detail="Unauthorized access to payment session")
        
        # Get session status from Whop
        session_status = await whop_service.get_session_status(whop_session_id)
        
        return {
            "valid": True,
            "transaction_id": transaction.id,
            "user_id": transaction.user_id,
            "session_status": session_status.get("status", "unknown"),
            "amount": transaction.amount,
            "plan_id": transaction.plan_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Session validation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Session validation failed")


@router.get("/checkout-access/{user_id}")
async def check_checkout_access(
    user_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Check if a user has access to create checkout sessions"""
    try:
        user_info = user_tracking.extract_user_info(request)
        
        # Check for recent pending transactions from this user
        recent_pending = db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.status == "pending"
        ).count()
        
        # Check for completed transactions (prevent duplicate purchases)
        completed_transactions = db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.status == "completed"
        ).count()
        
        return {
            "can_checkout": recent_pending == 0 and completed_transactions == 0,
            "pending_transactions": recent_pending,
            "completed_transactions": completed_transactions,
            "message": (
                "Access granted" if recent_pending == 0 and completed_transactions == 0
                else "Pending transaction exists" if recent_pending > 0
                else "Already purchased"
            )
        }
        
    except Exception as e:
        logger.error(f"Checkout access check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Access check failed")


@router.get("/admin/payment-status/{transaction_id}")
async def check_payment_status(transaction_id: int, db: Session = Depends(get_db)):
    """Check payment status for a specific transaction (admin endpoint)"""
    try:
        transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
        
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        result = {
            "transaction_id": transaction.id,
            "current_status": transaction.status,
            "whop_session_id": transaction.whop_session_id,
            "whop_checkout_url": transaction.whop_checkout_url,
            "webhook_received": transaction.webhook_received,
            "created_at": transaction.created_at,
            "completed_at": transaction.completed_at,
            "user_id": transaction.user_id,
            "amount": transaction.amount
        }
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Payment status check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Status check failed")


@router.get("/invoice/{transaction_id}")
async def get_invoice_data(transaction_id: int, db: Session = Depends(get_db)):
    """Get invoice/receipt data for a completed transaction"""
    try:
        transaction = db.query(Transaction).filter(
            Transaction.id == transaction_id,
            Transaction.status == "completed"
        ).first()
        
        if not transaction:
            raise HTTPException(status_code=404, detail="Completed transaction not found")
        
        receipt_data = invoice_service.get_receipt_data(transaction)
        return receipt_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Invoice data retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get invoice data")


@router.get("/invoice/{transaction_id}/download")
async def download_invoice_pdf(transaction_id: int, db: Session = Depends(get_db)):
    """Download PDF invoice for a completed transaction"""
    try:
        transaction = db.query(Transaction).filter(
            Transaction.id == transaction_id,
            Transaction.status == "completed"
        ).first()
        
        if not transaction:
            raise HTTPException(status_code=404, detail="Completed transaction not found")
        
        # Generate PDF
        pdf_buffer = invoice_service.generate_invoice_pdf(transaction)
        
        # Return as downloadable file
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=cerebra-invoice-{transaction.id:06d}.pdf"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"PDF generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate PDF invoice")


@router.post("/admin/test-webhook")
async def test_webhook_processing(db: Session = Depends(get_db)):
    """Test endpoint to manually update most recent pending transaction"""
    try:
        # Find most recent pending transaction
        transaction = db.query(Transaction).filter(
            Transaction.status == "pending"
        ).order_by(Transaction.created_at.desc()).first()
        
        if not transaction:
            return {"message": "No pending transactions found"}
        
        # Update to completed
        transaction.status = "completed"
        transaction.webhook_received = True
        transaction.completed_at = func.now()
        
        # Add test data
        extra_data = json.loads(transaction.extra_data or "{}")
        extra_data["test_update"] = True
        transaction.extra_data = json.dumps(extra_data)
        
        db.commit()
        
        return {
            "message": f"Updated transaction {transaction.id} to completed",
            "transaction_id": transaction.id,
            "status": "completed"
        }
        
    except Exception as e:
        logger.error(f"Test webhook failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Test failed")


@router.post("/webhooks/whop")
async def whop_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle Whop webhooks for payment status updates with signature verification"""
    try:
        # Get raw body for signature verification
        body = await request.body()
        
        # Get signature from headers
        signature = request.headers.get("x-whop-signature") or request.headers.get("whop-signature")
        
        if not signature:
            logger.warning("Webhook received without signature")
            raise HTTPException(status_code=401, detail="Missing webhook signature")
        
        # Verify webhook signature
        if not whop_service.verify_webhook_signature(body, signature):
            logger.warning("Webhook signature verification failed")
            raise HTTPException(status_code=401, detail="Invalid webhook signature")
        
        # Parse webhook data
        webhook_data = json.loads(body)
        
        # Extract webhook data
        event_type = webhook_data.get("type", "")
        data = webhook_data.get("data", {})
        
        # Extract session ID from webhook
        session_id = whop_service.extract_session_id_from_webhook(webhook_data)
        
        logger.info(f"Received Whop webhook: {event_type}")
        
        if event_type == "payment_succeeded":
            # Extract real payment data from Whop webhook
            payment_data = data.get("payment", {}) or data
            customer_data = payment_data.get("customer", {}) or data.get("customer", {})
            
            # Find transaction by user tracking or most recent pending
            transaction = None
            
            # Try to find by session ID if available
            if session_id:
                transaction = db.query(Transaction).filter(
                    Transaction.whop_session_id == session_id,
                    Transaction.status == "pending"
                ).first()
            
            # Fallback: find most recent pending transaction
            if not transaction:
                transaction = db.query(Transaction).filter(
                    Transaction.status == "pending"
                ).order_by(Transaction.created_at.desc()).first()
            
            if transaction:
                # Update with real Whop data
                transaction.status = "completed"
                transaction.webhook_received = True
                transaction.completed_at = func.now()
                
                # Update with real customer data from Whop
                transaction.customer_email = customer_data.get("email") or transaction.customer_email
                transaction.customer_name = customer_data.get("name") or customer_data.get("username") or transaction.customer_name
                
                # Update with real payment amount from Whop
                real_amount = payment_data.get("amount") or payment_data.get("total")
                if real_amount:
                    transaction.amount = float(real_amount) / 100  # Convert from cents
                
                # Store complete webhook data for receipt generation
                extra_data = json.loads(transaction.extra_data or "{}")
                extra_data["webhook_data"] = webhook_data
                extra_data["payment_data"] = payment_data
                extra_data["customer_data"] = customer_data
                extra_data["whop_payment_id"] = payment_data.get("id")
                extra_data["whop_invoice_id"] = payment_data.get("invoice_id")
                transaction.extra_data = json.dumps(extra_data)
                
                db.commit()
                logger.info(f"Payment succeeded: Transaction {transaction.id} for {transaction.customer_name} - ${transaction.amount}")
            else:
                logger.warning("No pending transaction found for payment_succeeded event")
        
        elif event_type == "payment_failed":
            # Find transaction by session ID or most recent pending
            transaction = None
            
            if session_id:
                transaction = db.query(Transaction).filter(
                    Transaction.whop_session_id == session_id,
                    Transaction.status == "pending"
                ).first()
            
            if not transaction:
                transaction = db.query(Transaction).filter(
                    Transaction.status == "pending"
                ).order_by(Transaction.created_at.desc()).first()
            
            if transaction:
                transaction.status = "failed"
                transaction.webhook_received = True
                transaction.error_message = data.get("failure_reason", "Payment failed")
                
                # Store webhook data for audit
                extra_data = json.loads(transaction.extra_data or "{}")
                extra_data["webhook_data"] = webhook_data
                transaction.extra_data = json.dumps(extra_data)
                
                db.commit()
                logger.info(f"❌ Payment failed: Transaction {transaction.id} for user {transaction.user_id}")
            else:
                logger.warning(f"⚠️ No pending transaction found for payment_failed event")
        
        elif event_type == "payment_pending":
            # Handle pending payments (useful for tracking)
            logger.info(f"💰 Payment pending: {data}")
        
        elif event_type == "membership_went_valid":
            # Handle successful membership activation
            transaction = db.query(Transaction).filter(
                Transaction.status == "completed"
            ).order_by(Transaction.created_at.desc()).first()
            
            if transaction:
                # Update extra data to include membership info
                extra_data = json.loads(transaction.extra_data or "{}")
                extra_data["membership_data"] = webhook_data
                transaction.extra_data = json.dumps(extra_data)
                db.commit()
                logger.info(f"🎉 Membership activated for transaction {transaction.id}")
        
        elif event_type == "membership_went_invalid":
            # Handle membership cancellation/expiry
            logger.info(f"⚠️ Membership went invalid: {data}")
        
        else:
            logger.info(f"📝 Unhandled webhook event: {event_type}")
        
        return {"status": "received", "event": event_type}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")