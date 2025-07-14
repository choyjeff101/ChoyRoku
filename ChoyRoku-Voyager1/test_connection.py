#!/usr/bin/env python3
"""
Connection Test Script
Tests the complete flow from Flask app to Roku device
"""

import requests
import json
import sys

def test_flask_app():
    """Test if Flask app is running and accessible"""
    print("🔍 Testing Flask app...")
    try:
        resp = requests.get("http://localhost:8000", timeout=5)
        if resp.status_code == 200:
            print("   ✅ Flask app is running and accessible")
            return True
        else:
            print(f"   ❌ Flask app returned status {resp.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Flask app not accessible: {e}")
        return False

def test_roku_discovery():
    """Test Roku device discovery"""
    print("\n🔍 Testing Roku discovery...")
    try:
        resp = requests.get("http://localhost:8000", timeout=5)
        if "Circus" in resp.text or "192.168.1.4" in resp.text:
            print("   ✅ Roku device found in Flask app")
            return True
        else:
            print("   ❌ Roku device not found in Flask app")
            return False
    except Exception as e:
        print(f"   ❌ Discovery test failed: {e}")
        return False

def test_roku_connection():
    """Test direct connection to Roku device"""
    print("\n🔍 Testing direct Roku connection...")
    try:
        resp = requests.get("http://192.168.1.4:8060/query/device-info", timeout=5)
        if resp.status_code == 200:
            print("   ✅ Direct connection to Roku successful")
            return True
        else:
            print(f"   ❌ Direct connection failed: {resp.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Direct connection failed: {e}")
        return False

def test_roku_control():
    """Test sending a command to Roku through Flask app"""
    print("\n🔍 Testing Roku control through Flask...")
    try:
        # Create a session to maintain cookies
        session = requests.Session()
        
        # First select the Roku device
        select_data = {"roku_ip": "192.168.1.4"}
        resp = session.post("http://localhost:8000/select", data=select_data, timeout=5)
        
        if resp.status_code in [200, 302]:  # Both OK and redirect are acceptable
            # Now test sending a command
            key_data = {"key": "Home"}
            resp = session.post("http://localhost:8000/send", data=key_data, timeout=5)
            
            if resp.status_code == 200:
                print("   ✅ Roku control through Flask successful")
                return True
            else:
                print(f"   ❌ Roku control failed: {resp.status_code}")
                return False
        else:
            print(f"   ❌ Device selection failed: {resp.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Roku control test failed: {e}")
        return False

def get_network_info():
    """Get network information for troubleshooting"""
    print("\n🌐 Network Information:")
    print("=" * 30)
    
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        print(f"Local IP: {local_ip}")
        print(f"Flask app: http://{local_ip}:8000")
        print(f"Roku device: 192.168.1.4 (Circus)")
    except Exception as e:
        print(f"Could not determine network info: {e}")

def main():
    print("🎯 ChoyRoku Connection Test")
    print("=" * 40)
    
    get_network_info()
    
    # Run tests
    tests = [
        ("Flask App", test_flask_app),
        ("Roku Discovery", test_roku_discovery),
        ("Direct Roku Connection", test_roku_connection),
        ("Roku Control via Flask", test_roku_control),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   ❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 TEST RESULTS")
    print("=" * 50)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("Your ChoyRoku setup is working correctly.")
        print("\n📱 To access from your iPhone:")
        print("   Open Safari and go to: http://[your-ip]:8000")
    else:
        print("⚠️  SOME TESTS FAILED")
        print("\n🔧 Troubleshooting steps:")
        print("   1. Make sure Flask app is running: python3 ChoyRoku.py")
        print("   2. Check Roku device is powered on and connected")
        print("   3. Verify network connectivity")
        print("   4. Run: python3 find_rokus.py")
        print("   5. Check firewall settings")

if __name__ == "__main__":
    main() 