#!/usr/bin/env python3
"""
Project setup script for Whop + FastAPI + Bootstrap Boilerplate
This script helps set up the project for first-time use.
"""

import os
import sys
import secrets
import subprocess
from pathlib import Path

def print_header():
    print("🚀 Whop + FastAPI + Bootstrap Boilerplate Setup")
    print("=" * 50)

def check_python_version():
    """Check if Python version is 3.8+"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def setup_virtual_environment():
    """Set up Python virtual environment"""
    print("\n📦 Setting up virtual environment...")
    
    if not Path("venv").exists():
        try:
            subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
            print("✅ Virtual environment created")
        except subprocess.CalledProcessError:
            print("❌ Failed to create virtual environment")
            return False
    else:
        print("✅ Virtual environment already exists")
    
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("\n📚 Installing dependencies...")
    
    # Determine pip path
    if os.name == 'nt':  # Windows
        pip_path = Path("venv/Scripts/pip")
    else:  # macOS/Linux
        pip_path = Path("venv/bin/pip")
    
    try:
        subprocess.run([str(pip_path), "install", "-r", "backend/requirements.txt"], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def setup_environment_file():
    """Set up .env file from template"""
    print("\n⚙️ Setting up environment file...")
    
    env_path = Path("backend/.env")
    env_example_path = Path("backend/.env.example")
    
    if env_path.exists():
        print("✅ .env file already exists")
        return True
    
    if not env_example_path.exists():
        print("❌ .env.example file not found")
        return False
    
    # Read template
    with open(env_example_path, 'r') as f:
        content = f.read()
    
    # Generate secure secret key
    secret_key = secrets.token_urlsafe(32)
    content = content.replace("your_secure_random_secret_key_here", secret_key)
    
    # Write .env file
    with open(env_path, 'w') as f:
        f.write(content)
    
    print("✅ .env file created with secure secret key")
    print("⚠️  Please update Whop configuration in .env file")
    return True

def setup_database():
    """Set up database"""
    print("\n🗄️ Setting up database...")
    
    try:
        # Change to backend directory
        os.chdir("backend")
        
        # Run migration script
        if Path("migrate_db.py").exists():
            subprocess.run([sys.executable, "migrate_db.py"], check=True)
            print("✅ Database migration completed")
        else:
            print("⚠️  Migration script not found - database will be created on first run")
        
        # Change back to root directory
        os.chdir("..")
        return True
    except subprocess.CalledProcessError:
        print("❌ Database setup failed")
        os.chdir("..")
        return False

def print_next_steps():
    """Print next steps for the user"""
    print("\n🎯 Next Steps:")
    print("1. Update backend/.env with your Whop configuration:")
    print("   - WHOP_WEBHOOK_SECRET (from Whop dashboard)")
    print("   - WHOP_PLAN_ID (your product ID)")
    print("   - WHOP_CHECKOUT_LINK (your checkout link ID)")
    print("   - COMPANY_NAME, PRODUCT_NAME (optional)")
    
    print("\n2. Start the development server:")
    if os.name == 'nt':  # Windows
        print("   venv\\Scripts\\activate")
    else:  # macOS/Linux
        print("   source venv/bin/activate")
    print("   cd backend")
    print("   uvicorn main:app --reload")
    
    print("\n3. Visit http://localhost:8000 to see your application")
    
    print("\n4. Set up Whop webhook (for production):")
    print("   - Use ngrok for development: ngrok http 8000")
    print("   - Configure webhook in Whop dashboard")
    print("   - Set endpoint: https://your-url.com/api/webhooks/whop")
    
    print("\n📚 Documentation:")
    print("   - README.md - Complete setup guide")
    print("   - CONTRIBUTING.md - How to contribute")
    print("   - Check /admin for transaction management")

def main():
    """Main setup function"""
    print_header()
    
    # Check Python version
    check_python_version()
    
    # Set up virtual environment
    if not setup_virtual_environment():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Set up environment file
    if not setup_environment_file():
        sys.exit(1)
    
    # Set up database
    setup_database()
    
    # Print next steps
    print_next_steps()
    
    print("\n✅ Setup completed successfully!")
    print("🚀 Your Whop + FastAPI + Bootstrap application is ready!")

if __name__ == "__main__":
    main()