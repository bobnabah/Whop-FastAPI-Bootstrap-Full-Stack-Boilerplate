from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

# Import helpers and router in a flexible way so main.py can be run as:
#  - uvicorn main:app (from backend/)
#  - uvicorn backend.main:app (from project root)
try:
    # when run as package from project root
    from backend.database import init_db
    from backend.api.routes import router as api_router
    from backend.database import get_db
except Exception:
    # when run from backend directory
    from .database import init_db
    from .api.routes import router as api_router
    from .database import get_db

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    # ensure tables exist
    init_db()


@app.on_event("shutdown")
def shutdown():
    pass


app.include_router(api_router, prefix="/api")

# Mount frontend static files (serves JS/CSS under /static)
static_dir = Path(__file__).resolve().parent.parent / "frontend" / "public"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Templates directory inside backend package
templates_dir = Path(__file__).resolve().parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, db=Depends(get_db)):
    """Render the main checkout page for the $5 plan with access validation."""
    try:
        # Import here to avoid circular imports
        try:
            # when running as package (project root)
            from backend.services.user_tracking import user_tracking
            from backend.models import Transaction
        except Exception:
            # when running from backend directory
            from .services.user_tracking import user_tracking
            from .models import Transaction
        
        # Extract user info for tracking
        user_info = user_tracking.extract_user_info(request)
        user_fingerprint = user_info["user_fingerprint"]
        ip_address = user_info["ip_address"]
        
        # Check for existing completed transactions from this user/IP
        existing_transaction = db.query(Transaction).filter(
            Transaction.status == "completed"
        ).filter(
            (Transaction.ip_address == ip_address) |
            (Transaction.extra_data.contains(user_fingerprint))
        ).first()
        
        # If user already purchased, redirect to success page
        if existing_transaction:
            return RedirectResponse(url="/payment/success", status_code=302)
        
        return templates.TemplateResponse("index.html", {
            "request": request,
            "user_id": user_tracking.create_user_identifier(),
            "session_id": user_info["session_id"]
        })
        
    except Exception as e:
        # If there's any error with validation, still show the page
        return templates.TemplateResponse("index.html", {"request": request})


@app.get("/payment/success", response_class=HTMLResponse)
def payment_success(request: Request, transaction_id: int = None, db=Depends(get_db)):
    """Payment success page with real receipt data"""
    return templates.TemplateResponse("success.html", {
        "request": request,
        "message": "Payment completed successfully!"
    })


@app.get("/payment/cancel", response_class=HTMLResponse)
def payment_cancel(request: Request):
    """Payment cancelled page"""
    return templates.TemplateResponse("cancel.html", {
        "request": request,
        "message": "Payment was cancelled. You can try again anytime."
    })


@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request, db=Depends(get_db)):
    """Admin dashboard for transaction management"""
    try:
        # when running as package (project root)
        from backend.models import Transaction
    except Exception:
        # when running from backend directory
        from .models import Transaction
    
    # Get recent transactions
    transactions = db.query(Transaction).order_by(Transaction.created_at.desc()).limit(50).all()
    
    return templates.TemplateResponse("admin.html", {
        "request": request, 
        "transactions": transactions
    })


@app.get("/transactions/{transaction_id}/success", response_class=HTMLResponse)
def transaction_success(request: Request, transaction_id: int, db=Depends(get_db)):
    """Legacy transaction success page"""
    try:
        # when running as package (project root)
        from backend.models import Transaction
    except Exception:
        # when running from backend directory
        from .models import Transaction

    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        return HTMLResponse("<h1>Transaction not found</h1>", status_code=404)
    return templates.TemplateResponse("success.html", {"request": request, "transaction": transaction})