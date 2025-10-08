# 🚀 Whop + FastAPI + Bootstrap Full-Stack Boilerplate

A complete, production-ready boilerplate for building payment-enabled web applications using Whop payments, FastAPI backend, and Bootstrap frontend.

## ✨ Features

- 🔐 **Secure Whop Payment Integration** with webhook verification
- 🎯 **Session-bound Transactions** with user tracking
- 📄 **PDF Invoice Generation** with real customer data
- 🎨 **Beautiful Bootstrap UI** with responsive design
- 🔒 **User Access Control** and duplicate purchase prevention
- 📊 **Admin Dashboard** for transaction management
- 🧾 **Real-time Receipt System** with downloadable invoices
- 🔧 **Easy Configuration** via environment variables

## 🏗️ Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: Bootstrap 5 + Vanilla JavaScript
- **Database**: SQLite (development) / PostgreSQL (production)
- **Payments**: Whop API with webhooks
- **PDF Generation**: ReportLab
- **Authentication**: Session-based user tracking

## 📋 Prerequisites

- Python 3.8+
- Whop seller account
- Basic knowledge of FastAPI and Bootstrap

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd fastapi-fullstack-app
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
cd backend
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your actual values (see Configuration section below)
```

### 4. Set Up Database

```bash
# Run database migration
python migrate_db.py

# Or start the server (it will create tables automatically)
uvicorn main:app --reload
```

### 5. Start the Application

```bash
# Start the FastAPI server
uvicorn main:app --reload --port 8000
```

Visit `http://localhost:8000` to see your application!

## ⚙️ Configuration

### Step-by-Step Whop Setup

#### 1. Create Your Product in Whop

1. **Login to Whop**: Go to [whop.com](https://whop.com)
2. **Create Product**: 
   - Go to "Products" → "Create Product"
   - Set your product name, description, and price
   - Save the product

#### 2. Get Your Product ID

1. **Go to Products**: In your Whop dashboard
2. **Select Your Product**: Click on the product you created
3. **Copy Product ID**: Look for the Product ID (format: `prod_xxxxxxxxxxxxxxxxx`)
4. **Add to .env**: Set `WHOP_PLAN_ID=prod_your_product_id_here`

#### 3. Create Checkout Link

1. **In Your Product**: Go to "Checkout Links" tab
2. **Create Checkout Link**: Click "Create Checkout Link"
3. **Copy Link ID**: Copy the checkout link ID (format: `plan_xxxxxxxxxxxxxxxxx`)
4. **Add to .env**: Set `WHOP_CHECKOUT_LINK=plan_your_checkout_link_id_here`

#### 4. Set Up Webhook

1. **Go to Webhooks**: In Whop dashboard → "Developer" → "Webhooks"
2. **Create Webhook**: Click "Create Webhook"
3. **Set Endpoint URL**: 
   - Development: `https://your-ngrok-url.ngrok.io/api/webhooks/whop`
   - Production: `https://yourdomain.com/api/webhooks/whop`
4. **Select Events**:
   - ✅ `payment_succeeded`
   - ✅ `payment_failed`
   - ✅ `payment_pending`
   - ✅ `membership_went_valid`
   - ✅ `membership_went_invalid`
5. **Copy Webhook Secret**: After creating, copy the webhook secret
6. **Add to .env**: Set `WHOP_WEBHOOK_SECRET=whsec_your_webhook_secret_here`

### Environment Variables Reference

```bash
# =============================================================================
# REQUIRED CONFIGURATION
# =============================================================================

# Whop Integration
WHOP_WEBHOOK_SECRET=whsec_your_webhook_secret_here
WHOP_PLAN_ID=prod_your_product_id_here
WHOP_CHECKOUT_LINK=plan_your_checkout_link_id_here

# Application Security
SECRET_KEY=your_secure_random_secret_key_here

# =============================================================================
# OPTIONAL CONFIGURATION
# =============================================================================

# Database (SQLite for dev, PostgreSQL for production)
DATABASE_URL=sqlite:///./app.db

# Company Information (used in invoices and UI)
COMPANY_NAME=Your Company Name
COMPANY_ADDRESS=Your Company Address
PRODUCT_NAME=Your Product Name
PRODUCT_PRICE=5.00

# Environment
ENVIRONMENT=development
DEBUG_MODE=false
```

### Generate Secure Secret Key

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 🔧 Development Setup

### Using ngrok for Webhook Testing

1. **Install ngrok**: Download from [ngrok.com](https://ngrok.com)

2. **Start your FastAPI server**:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

3. **Start ngrok** (in another terminal):
   ```bash
   ngrok http 8000
   ```

4. **Copy the HTTPS URL**: Use this URL in your Whop webhook configuration

5. **Update Whop webhook**: Set endpoint to `https://your-ngrok-url.ngrok.io/api/webhooks/whop`

## 📁 Project Structure

```
fastapi-fullstack-app/
├── backend/
│   ├── api/
│   │   └── routes.py          # API endpoints
│   ├── services/
│   │   ├── whop_service.py    # Whop integration
│   │   ├── invoice_service.py # PDF invoice generation
│   │   └── user_tracking.py   # User session tracking
│   ├── templates/
│   │   ├── index.html         # Main checkout page
│   │   ├── success.html       # Payment success page
│   │   ├── admin.html         # Admin dashboard
│   │   └── cancel.html        # Payment cancelled page
│   ├── models.py              # Database models
│   ├── database.py            # Database configuration
│   ├── main.py                # FastAPI application
│   ├── requirements.txt       # Python dependencies
│   └── .env.example           # Environment variables template
├── frontend/
│   └── public/
│       ├── app.js             # Frontend JavaScript
│       └── index.html         # Alternative frontend
└── README.md                  # This file
```

## 🔌 API Endpoints

### Public Endpoints

- `GET /` - Main checkout page
- `POST /api/create-cerebra-checkout` - Create checkout session
- `POST /api/webhooks/whop` - Whop webhook handler
- `GET /payment/success` - Payment success page
- `GET /payment/cancel` - Payment cancelled page

### Admin Endpoints

- `GET /admin` - Admin dashboard
- `GET /api/transactions/` - List all transactions
- `GET /api/transactions/{transaction_id}` - Get transaction details
- `GET /api/admin/payment-status/{transaction_id}` - Check payment status
- `GET /api/invoice/{transaction_id}` - Get invoice data
- `GET /api/invoice/{transaction_id}/download` - Download PDF invoice

### Debug Endpoints (Development Only)

- `POST /api/admin/test-webhook` - Test webhook processing
- `GET /api/transactions/user/{user_id}` - Get user transactions
- `GET /api/validate-session/{session_id}` - Validate session

## 🧪 Testing

### Test the Application

1. **Start the server**:
   ```bash
   uvicorn main:app --reload
   ```

2. **Visit the checkout page**: `http://localhost:8000`

3. **Test checkout flow**: Click "Get Premium Access"

4. **Complete payment**: Use Whop's test payment methods

5. **Check webhook**: Monitor server logs for webhook events

6. **Verify transaction**: Check admin dashboard at `http://localhost:8000/admin`

### Manual Testing Commands

```bash
# Test webhook endpoint (should return 401)
curl -X POST http://localhost:8000/api/webhooks/whop

# Test transaction creation
curl -X POST http://localhost:8000/api/create-cerebra-checkout \
  -H "Content-Type: application/json" \
  -d '{"plan_id": "your_plan_id", "amount": 5.00}'

# Check transactions
curl http://localhost:8000/api/transactions/

# Test manual transaction update
curl -X POST http://localhost:8000/api/admin/test-webhook
```

## 🚀 Production Deployment

### 1. Environment Setup

```bash
# Update environment variables for production
ENVIRONMENT=production
DATABASE_URL=postgresql://user:password@host:port/database
DEBUG_MODE=false
```

### 2. Database Migration

```bash
# For PostgreSQL, install psycopg2
pip install psycopg2-binary

# Run migrations
python migrate_db.py
```

### 3. Webhook Configuration

- Update Whop webhook URL to your production domain
- Ensure HTTPS is properly configured
- Test webhook delivery in production

### 4. Security Checklist

- [ ] Use strong `SECRET_KEY`
- [ ] Enable HTTPS
- [ ] Set `DEBUG_MODE=false`
- [ ] Use production database
- [ ] Configure proper CORS settings
- [ ] Set up monitoring and logging

## 🎨 Customization

### Branding and UI

1. **Update Company Information**:
   ```bash
   COMPANY_NAME=Your Company Name
   COMPANY_ADDRESS=Your Company Address
   PRODUCT_NAME=Your Product Name
   ```

2. **Customize Templates**:
   - Edit `templates/index.html` for main page
   - Edit `templates/success.html` for success page
   - Update CSS styles and colors

3. **Update Product Information**:
   - Change product name and description
   - Update feature list
   - Modify pricing display

### Adding Features

1. **User Authentication**: Add login/signup system
2. **Email Notifications**: Send confirmation emails
3. **Subscription Management**: Handle recurring payments
4. **Analytics**: Add tracking and analytics
5. **Multi-product Support**: Support multiple products

## 🐛 Troubleshooting

### Common Issues

#### Webhook Not Working
- ✅ Check webhook URL is publicly accessible
- ✅ Verify webhook secret is correct
- ✅ Check server logs for webhook events
- ✅ Test with ngrok for development

#### Transaction Status Not Updating
- ✅ Check webhook events are being received
- ✅ Verify webhook signature verification
- ✅ Check database for pending transactions
- ✅ Use debug endpoints to test manually

#### PDF Generation Errors
- ✅ Ensure ReportLab is installed: `pip install reportlab`
- ✅ Check file permissions for PDF generation
- ✅ Verify transaction has required data

#### Environment Variables Not Loading
- ✅ Check `.env` file exists in backend directory
- ✅ Verify environment variable names are correct
- ✅ Restart server after changing `.env`

### Debug Mode

Enable debug mode for detailed logging:

```bash
DEBUG_MODE=true
```

This will:
- Enable detailed webhook logging
- Disable webhook signature verification
- Show more error details

## 📚 Documentation

### Key Components

1. **WhopService** (`services/whop_service.py`):
   - Handles webhook signature verification
   - Manages checkout URL generation
   - Processes webhook events

2. **InvoiceService** (`services/invoice_service.py`):
   - Generates PDF invoices
   - Formats receipt data
   - Handles customer information

3. **UserTracking** (`services/user_tracking.py`):
   - Tracks user sessions
   - Prevents duplicate purchases
   - Creates user fingerprints

4. **Transaction Model** (`models.py`):
   - Stores payment data
   - Tracks transaction status
   - Maintains audit trail

### Webhook Events

The application handles these Whop webhook events:

- `payment_succeeded`: Payment completed successfully
- `payment_failed`: Payment failed or declined
- `payment_pending`: Payment is being processed
- `membership_went_valid`: Membership activated
- `membership_went_invalid`: Membership cancelled/expired

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Add tests if applicable
5. Commit your changes: `git commit -am 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Whop](https://whop.com) for payment processing
- [FastAPI](https://fastapi.tiangolo.com/) for the amazing web framework
- [Bootstrap](https://getbootstrap.com/) for the UI components
- [ReportLab](https://www.reportlab.com/) for PDF generation

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Review the [Whop Documentation](https://docs.whop.com)
3. Create an issue in this repository
4. Join the community discussions

---

**Happy coding!** 🚀 Build amazing payment-enabled applications with this boilerplate!