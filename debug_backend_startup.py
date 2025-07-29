#!/usr/bin/env python3
"""
Debug Backend Startup Issues
Find out why the backend won't start
"""
import sys
import os
import traceback

def test_imports():
    """Test if all imports work"""
    print("🔍 Testing Backend Imports")
    print("=" * 50)
    
    try:
        # Add backend to path
        backend_path = os.path.join(os.getcwd(), 'hotel-onboarding-backend')
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)
        
        print(f"✅ Added to Python path: {backend_path}")
        
        # Test basic imports
        print("\n1️⃣ Testing basic imports...")
        
        try:
            from fastapi import FastAPI
            print("✅ FastAPI import successful")
        except Exception as e:
            print(f"❌ FastAPI import failed: {e}")
            return False
        
        try:
            import uvicorn
            print("✅ Uvicorn import successful")
        except Exception as e:
            print(f"❌ Uvicorn import failed: {e}")
            return False
        
        # Test app imports
        print("\n2️⃣ Testing app module imports...")
        
        try:
            from app.models import User
            print("✅ app.models import successful")
        except Exception as e:
            print(f"❌ app.models import failed: {e}")
            traceback.print_exc()
            return False
        
        try:
            from app.supabase_service_enhanced import EnhancedSupabaseService
            print("✅ app.supabase_service_enhanced import successful")
        except Exception as e:
            print(f"❌ app.supabase_service_enhanced import failed: {e}")
            traceback.print_exc()
            return False
        
        try:
            from app.email_service import email_service
            print("✅ app.email_service import successful")
        except Exception as e:
            print(f"❌ app.email_service import failed: {e}")
            traceback.print_exc()
            return False
        
        # Test main app import
        print("\n3️⃣ Testing main app import...")
        
        try:
            from app.main_enhanced import app
            print("✅ app.main_enhanced import successful")
            print(f"   App type: {type(app)}")
            print(f"   App title: {getattr(app, 'title', 'Unknown')}")
        except Exception as e:
            print(f"❌ app.main_enhanced import failed: {e}")
            traceback.print_exc()
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        traceback.print_exc()
        return False

def test_environment():
    """Test environment setup"""
    print("\n🌍 Testing Environment Setup")
    print("=" * 50)
    
    # Check .env file
    env_path = os.path.join('hotel-onboarding-backend', '.env')
    if os.path.exists(env_path):
        print("✅ .env file exists")
        
        # Read key variables
        try:
            with open(env_path, 'r') as f:
                env_content = f.read()
            
            required_vars = ['SUPABASE_URL', 'SUPABASE_ANON_KEY', 'JWT_SECRET_KEY']
            for var in required_vars:
                if var in env_content:
                    print(f"✅ {var} found in .env")
                else:
                    print(f"⚠️  {var} not found in .env")
        except Exception as e:
            print(f"❌ Error reading .env: {e}")
    else:
        print("❌ .env file not found")
    
    # Check Python version
    print(f"\n🐍 Python version: {sys.version}")
    
    # Check working directory
    print(f"📁 Working directory: {os.getcwd()}")
    
    # Check if backend directory exists
    backend_dir = 'hotel-onboarding-backend'
    if os.path.exists(backend_dir):
        print(f"✅ Backend directory exists: {backend_dir}")
        
        # List key files
        key_files = ['app/main_enhanced.py', 'app/models.py', 'app/supabase_service_enhanced.py']
        for file in key_files:
            file_path = os.path.join(backend_dir, file)
            if os.path.exists(file_path):
                print(f"✅ {file} exists")
            else:
                print(f"❌ {file} missing")
    else:
        print(f"❌ Backend directory not found: {backend_dir}")

def test_direct_startup():
    """Test direct app startup"""
    print("\n🚀 Testing Direct App Startup")
    print("=" * 50)
    
    try:
        # Change to backend directory
        original_cwd = os.getcwd()
        backend_path = os.path.join(original_cwd, 'hotel-onboarding-backend')
        
        if not os.path.exists(backend_path):
            print(f"❌ Backend path doesn't exist: {backend_path}")
            return False
        
        os.chdir(backend_path)
        print(f"✅ Changed to backend directory: {backend_path}")
        
        # Add to Python path
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)
        
        # Import the app
        from app.main_enhanced import app
        print("✅ App imported successfully")
        
        # Test app configuration
        print(f"   App title: {app.title}")
        print(f"   App version: {app.version}")
        
        # Try to start uvicorn programmatically
        import uvicorn
        print("✅ Uvicorn imported")
        
        print("\n🔥 Starting uvicorn server...")
        print("   This should start the server on http://localhost:8000")
        print("   Press Ctrl+C to stop")
        
        # Start the server
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
        
    except KeyboardInterrupt:
        print("\n✅ Server stopped by user")
        return True
    except Exception as e:
        print(f"❌ Direct startup failed: {e}")
        traceback.print_exc()
        return False
    finally:
        # Restore original directory
        os.chdir(original_cwd)

if __name__ == "__main__":
    print("🔧 BACKEND STARTUP DIAGNOSTIC")
    print("=" * 60)
    
    # Test imports
    imports_ok = test_imports()
    
    # Test environment
    test_environment()
    
    if imports_ok:
        print("\n✅ All imports successful - attempting direct startup...")
        test_direct_startup()
    else:
        print("\n❌ Import failures detected - fix imports first")
        
        print("\n🔧 TROUBLESHOOTING STEPS:")
        print("1. Check if you're in the correct directory")
        print("2. Install missing dependencies")
        print("3. Check .env file configuration")
        print("4. Verify Python path setup")