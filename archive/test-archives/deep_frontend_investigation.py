#!/usr/bin/env python3

"""
Deep Frontend Investigation - Find the EXACT reason why QR URLs don't work
"""

import requests
import subprocess
import time
import os

def check_all_ports():
    """Check what's actually running on all relevant ports"""
    print("🔍 STEP 1: Checking All Ports")
    print("=" * 50)
    
    ports_to_check = [3000, 5173, 5174, 8000, 8080]
    
    for port in ports_to_check:
        try:
            result = subprocess.run(['lsof', '-i', f':{port}'], 
                                  capture_output=True, text=True, timeout=5)
            if result.stdout.strip():
                print(f"✅ Port {port}: OCCUPIED")
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 2:
                        print(f"   Process: {parts[0]} (PID: {parts[1]})")
            else:
                print(f"❌ Port {port}: FREE")
        except Exception as e:
            print(f"⚠️  Port {port}: Error checking - {e}")

def check_frontend_processes():
    """Check what frontend processes are actually running"""
    print("\n🔍 STEP 2: Frontend Process Investigation")
    print("=" * 50)
    
    try:
        # Check for npm processes
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        npm_processes = [line for line in lines if 'npm' in line and 'dev' in line]
        vite_processes = [line for line in lines if 'vite' in line]
        node_processes = [line for line in lines if 'node' in line and ('vite' in line or 'dev' in line)]
        
        print(f"NPM dev processes: {len(npm_processes)}")
        for proc in npm_processes:
            print(f"  {proc}")
            
        print(f"\nVite processes: {len(vite_processes)}")
        for proc in vite_processes:
            print(f"  {proc}")
            
        print(f"\nNode dev processes: {len(node_processes)}")
        for proc in node_processes:
            print(f"  {proc}")
            
    except Exception as e:
        print(f"Error checking processes: {e}")

def test_direct_curl():
    """Test direct curl to different ports and URLs"""
    print("\n🔍 STEP 3: Direct URL Testing")
    print("=" * 50)
    
    test_urls = [
        "http://localhost:3000",
        "http://localhost:3000/apply/prop_test_001",
        "http://localhost:5173",
        "http://localhost:5173/apply/prop_test_001", 
        "http://localhost:5174",
        "http://localhost:5174/apply/prop_test_001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5174"
    ]
    
    for url in test_urls:
        try:
            print(f"\nTesting: {url}")
            result = subprocess.run(['curl', '-s', '-I', '--connect-timeout', '3', url], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                status_line = result.stdout.split('\n')[0] if result.stdout else "No response"
                print(f"  ✅ Response: {status_line}")
            else:
                print(f"  ❌ Failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print(f"  ⏰ Timeout")
        except Exception as e:
            print(f"  ❌ Error: {e}")

def check_vite_config_and_package():
    """Check Vite configuration and package.json"""
    print("\n🔍 STEP 4: Configuration Investigation")
    print("=" * 50)
    
    # Check package.json
    try:
        with open("hotel-onboarding-frontend/package.json", "r") as f:
            package_content = f.read()
        
        print("📄 package.json dev script:")
        if '"dev":' in package_content:
            dev_line = [line.strip() for line in package_content.split('\n') if '"dev":' in line][0]
            print(f"  {dev_line}")
        else:
            print("  ❌ No dev script found")
            
    except Exception as e:
        print(f"❌ Error reading package.json: {e}")
    
    # Check vite.config.ts
    try:
        with open("hotel-onboarding-frontend/vite.config.ts", "r") as f:
            vite_content = f.read()
            
        print("\n📄 vite.config.ts server config:")
        if "server:" in vite_content:
            print("  ✅ Server config found")
            # Extract server config
            lines = vite_content.split('\n')
            in_server = False
            for line in lines:
                if 'server:' in line:
                    in_server = True
                if in_server:
                    print(f"    {line.strip()}")
                    if '}' in line and in_server:
                        break
        else:
            print("  ⚠️  No server config in vite.config.ts")
            
    except Exception as e:
        print(f"❌ Error reading vite.config.ts: {e}")

def check_frontend_logs():
    """Check for frontend logs and errors"""
    print("\n🔍 STEP 5: Log Investigation")
    print("=" * 50)
    
    log_files = [
        "hotel-onboarding-frontend/frontend.log",
        "hotel-onboarding-frontend/npm-debug.log",
        "hotel-onboarding-frontend/vite.log"
    ]
    
    for log_file in log_files:
        if os.path.exists(log_file):
            print(f"\n📄 {log_file}:")
            try:
                with open(log_file, "r") as f:
                    content = f.read()
                    # Show last 10 lines
                    lines = content.split('\n')[-10:]
                    for line in lines:
                        if line.strip():
                            print(f"  {line}")
            except Exception as e:
                print(f"  ❌ Error reading log: {e}")
        else:
            print(f"❌ {log_file} not found")

def test_frontend_startup():
    """Test if we can start frontend manually"""
    print("\n🔍 STEP 6: Manual Frontend Startup Test")
    print("=" * 50)
    
    print("Attempting to start frontend manually...")
    
    try:
        # Change to frontend directory and try to start
        os.chdir("hotel-onboarding-frontend")
        
        # Try npm run dev
        print("Running: npm run dev")
        result = subprocess.run(['npm', 'run', 'dev'], 
                              capture_output=True, text=True, timeout=10)
        
        print(f"Exit code: {result.returncode}")
        print(f"Stdout: {result.stdout}")
        print(f"Stderr: {result.stderr}")
        
    except subprocess.TimeoutExpired:
        print("⏰ Frontend startup timed out (this might be normal)")
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")
    finally:
        os.chdir("..")

def main():
    print("🚨 DEEP FRONTEND INVESTIGATION")
    print("Finding the EXACT reason why QR URLs don't work")
    print("=" * 60)
    
    check_all_ports()
    check_frontend_processes()
    test_direct_curl()
    check_vite_config_and_package()
    check_frontend_logs()
    
    print("\n" + "=" * 60)
    print("🎯 INVESTIGATION COMPLETE")
    print("Check the output above to identify the exact issue")

if __name__ == "__main__":
    main()