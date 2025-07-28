#!/usr/bin/env python3

"""
EMERGENCY PORT FIX - No bullshit, just fix the fucking ports
"""

import subprocess
import os
import time

def kill_all_dev_processes():
    """Kill all development processes"""
    print("🔥 KILLING ALL DEV PROCESSES")
    
    commands = [
        "pkill -f 'npm.*dev'",
        "pkill -f 'vite'", 
        "pkill -f 'node.*vite'",
        "lsof -ti:3000,3001,5173,5174 | xargs kill -9 2>/dev/null || true"
    ]
    
    for cmd in commands:
        try:
            subprocess.run(cmd, shell=True, timeout=5)
            print(f"✅ {cmd}")
        except:
            print(f"⚠️  {cmd} - failed but continuing")

def set_standard_ports():
    """Set standard ports everywhere"""
    print("\n🔧 SETTING STANDARD PORTS")
    
    # 1. Fix package.json - FORCE port 3000
    package_file = "hotel-onboarding-frontend/package.json"
    try:
        with open(package_file, 'r') as f:
            content = f.read()
        
        # Replace any dev script with forced port 3000
        content = content.replace('"dev": "vite --port 5173",', '"dev": "vite --port 3000 --host",')
        content = content.replace('"dev": "vite --port 3000",', '"dev": "vite --port 3000 --host",')
        content = content.replace('"dev": "vite",', '"dev": "vite --port 3000 --host",')
        
        with open(package_file, 'w') as f:
            f.write(content)
        print("✅ Fixed package.json - port 3000")
    except Exception as e:
        print(f"❌ Failed to fix package.json: {e}")
    
    # 2. Fix QR service - FORCE port 3000
    qr_file = "hotel-onboarding-backend/app/qr_service.py"
    try:
        with open(qr_file, 'r') as f:
            content = f.read()
        
        # Replace any localhost URL with port 3000
        content = content.replace('self.base_url = "http://localhost:5173"', 'self.base_url = "http://localhost:3000"')
        content = content.replace('self.base_url = "http://localhost:5174"', 'self.base_url = "http://localhost:3000"')
        
        with open(qr_file, 'w') as f:
            f.write(content)
        print("✅ Fixed qr_service.py - port 3000")
    except Exception as e:
        print(f"❌ Failed to fix qr_service.py: {e}")
    
    # 3. Add --host flag to vite config for network access
    vite_config = "hotel-onboarding-frontend/vite.config.ts"
    try:
        with open(vite_config, 'r') as f:
            content = f.read()
        
        if 'port:' not in content:
            # Add port config to server section
            content = content.replace(
                'server: {',
                'server: {\n    port: 3000,\n    host: true,'
            )
        
        with open(vite_config, 'w') as f:
            f.write(content)
        print("✅ Fixed vite.config.ts - port 3000")
    except Exception as e:
        print(f"❌ Failed to fix vite.config.ts: {e}")

def start_servers():
    """Start servers with proper ports"""
    print("\n🚀 STARTING SERVERS")
    
    # Start backend on port 8000
    print("Starting backend on port 8000...")
    try:
        os.chdir("hotel-onboarding-backend")
        subprocess.Popen(["python3", "-m", "app.main_enhanced"], 
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.chdir("..")
        print("✅ Backend started")
    except Exception as e:
        print(f"❌ Backend failed: {e}")
        os.chdir("..")
    
    # Wait a bit
    time.sleep(2)
    
    # Start frontend on port 3000
    print("Starting frontend on port 3000...")
    try:
        os.chdir("hotel-onboarding-frontend")
        subprocess.Popen(["npm", "run", "dev"], 
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.chdir("..")
        print("✅ Frontend started")
    except Exception as e:
        print(f"❌ Frontend failed: {e}")
        os.chdir("..")

def test_everything():
    """Test if everything works"""
    print("\n🧪 TESTING EVERYTHING")
    
    # Wait for servers to start
    print("Waiting 5 seconds for servers to start...")
    time.sleep(5)
    
    # Test backend
    try:
        result = subprocess.run(["curl", "-s", "-I", "http://127.0.0.1:8000/docs"], 
                              capture_output=True, text=True, timeout=5)
        if "200 OK" in result.stdout:
            print("✅ Backend working on port 8000")
        else:
            print("❌ Backend not responding")
    except:
        print("❌ Backend test failed")
    
    # Test frontend
    try:
        result = subprocess.run(["curl", "-s", "-I", "http://localhost:3000"], 
                              capture_output=True, text=True, timeout=5)
        if "200 OK" in result.stdout:
            print("✅ Frontend working on port 3000")
        else:
            print("❌ Frontend not responding")
    except:
        print("❌ Frontend test failed")
    
    # Test QR URL
    try:
        result = subprocess.run(["curl", "-s", "-I", "http://localhost:3000/apply/prop_test_001"], 
                              capture_output=True, text=True, timeout=5)
        if "200 OK" in result.stdout:
            print("✅ QR URL working")
        else:
            print("❌ QR URL not working")
    except:
        print("❌ QR URL test failed")

def main():
    print("🚨 EMERGENCY PORT STANDARDIZATION")
    print("=" * 50)
    
    kill_all_dev_processes()
    set_standard_ports()
    start_servers()
    test_everything()
    
    print("\n" + "=" * 50)
    print("🎯 STANDARD PORTS:")
    print("   Backend: http://127.0.0.1:8000")
    print("   Frontend: http://localhost:3000")
    print("   QR URLs: http://localhost:3000/apply/{propertyId}")
    print("=" * 50)

if __name__ == "__main__":
    main()