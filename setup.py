#!/usr/bin/env python3
"""
ChoyRoku Setup Script
This script helps set up and run the ChoyRoku application.
"""

import os
import sys
import subprocess
import socket
import requests
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = ['flask', 'requests']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"   ❌ {package} (missing)")
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
            print("✅ Dependencies installed successfully!")
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies. Please run:")
            print(f"   pip install {' '.join(missing_packages)}")
            return False
    
    return True

def get_raspberry_pi_ip():
    """Get the IP address of the Raspberry Pi"""
    print("\n🌐 Network Configuration:")
    print("=" * 30)
    
    try:
        # Get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        
        print(f"Current device IP: {local_ip}")
        
        # Ask user to confirm if this is the Raspberry Pi
        response = input(f"Is this the Raspberry Pi (pi-choy)? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            return local_ip
        else:
            pi_ip = input("Enter the Raspberry Pi IP address: ").strip()
            return pi_ip
            
    except Exception as e:
        print(f"Could not determine IP: {e}")
        pi_ip = input("Enter the Raspberry Pi IP address: ").strip()
        return pi_ip

def test_roku_connection(roku_ip):
    """Test connection to a Roku device"""
    try:
        resp = requests.get(f"http://{roku_ip}:8060/query/device-info", timeout=3)
        return resp.status_code == 200
    except:
        return False

def configure_roku_ips():
    """Configure Roku IP addresses"""
    print("\n📺 Roku Device Configuration:")
    print("=" * 35)
    
    # Run the discovery tool
    print("Running Roku discovery...")
    try:
        result = subprocess.run([sys.executable, 'find_rokus.py'], 
                              capture_output=True, text=True, timeout=60)
        print(result.stdout)
    except subprocess.TimeoutExpired:
        print("Discovery timed out, continuing with manual configuration...")
    except FileNotFoundError:
        print("Discovery script not found, continuing with manual configuration...")
    
    # Manual configuration
    print("\nManual Roku IP Configuration:")
    roku1_ip = input("Enter first Roku IP (or press Enter to skip): ").strip()
    roku2_ip = input("Enter second Roku IP (or press Enter to skip): ").strip()
    
    # Test connections
    if roku1_ip and test_roku_connection(roku1_ip):
        print(f"✅ Roku 1 ({roku1_ip}) is reachable")
    elif roku1_ip:
        print(f"❌ Roku 1 ({roku1_ip}) is not reachable")
        roku1_ip = ""
    
    if roku2_ip and test_roku_connection(roku2_ip):
        print(f"✅ Roku 2 ({roku2_ip}) is reachable")
    elif roku2_ip:
        print(f"❌ Roku 2 ({roku2_ip}) is not reachable")
        roku2_ip = ""
    
    return roku1_ip, roku2_ip

def update_config(pi_ip, roku1_ip, roku2_ip):
    """Update the ChoyRoku.py configuration"""
    print("\n⚙️  Updating configuration...")
    
    try:
        with open('ChoyRoku.py', 'r') as f:
            content = f.read()
        
        # Update Roku IPs
        if roku1_ip:
            content = content.replace('ROKU1_IP = "192.168.1.4"', f'ROKU1_IP = "{roku1_ip}"')
        
        if roku2_ip:
            content = content.replace('ROKU2_IP = "192.168.1.8"', f'ROKU2_IP = "{roku2_ip}"')
        else:
            # Remove ROKU2_IP if not provided
            content = content.replace('ROKU2_IP = "192.168.1.8"  # Add second Roku if you have one', 'ROKU2_IP = None  # No second Roku configured')
        
        with open('ChoyRoku.py', 'w') as f:
            f.write(content)
        
        print("✅ Configuration updated successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to update configuration: {e}")
        return False

def create_startup_script(pi_ip):
    """Create a startup script for the Raspberry Pi"""
    print("\n📝 Creating startup script...")
    
    startup_script = f"""#!/bin/bash
# ChoyRoku Startup Script for Raspberry Pi
# Run this script to start the ChoyRoku server

cd /home/pi/ChoyRoku  # Adjust path as needed
python3 ChoyRoku.py
"""
    
    try:
        with open('start_choyroku.sh', 'w') as f:
            f.write(startup_script)
        
        # Make it executable
        os.chmod('start_choyroku.sh', 0o755)
        print("✅ Startup script created: start_choyroku.sh")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create startup script: {e}")
        return False

def print_instructions(pi_ip):
    """Print setup instructions"""
    print("\n" + "=" * 60)
    print("🎉 SETUP COMPLETE!")
    print("=" * 60)
    
    print(f"\n📱 To access ChoyRoku from your iPhone (uranus):")
    print(f"   1. Make sure your iPhone is on the same network as pi-choy")
    print(f"   2. Open Safari and go to: http://{pi_ip}:8000")
    print(f"   3. Select your Roku device from the dropdown")
    print(f"   4. Use the control buttons to control your Roku")
    
    print(f"\n🖥️  To start the server on Raspberry Pi (pi-choy):")
    print(f"   1. Copy ChoyRoku.py to your Raspberry Pi")
    print(f"   2. Run: python3 ChoyRoku.py")
    print(f"   3. Or use the startup script: ./start_choyroku.sh")
    
    print(f"\n🔧 Troubleshooting:")
    print(f"   • If connection fails, check that pi-choy and uranus are on the same network")
    print(f"   • Verify the Roku IP addresses are correct")
    print(f"   • Make sure port 8000 is not blocked by firewall")
    print(f"   • Run 'python3 find_rokus.py' to rediscover Roku devices")
    
    print(f"\n📞 Access URLs:")
    print(f"   • Local access: http://localhost:8000")
    print(f"   • Network access: http://{pi_ip}:8000")
    print(f"   • Status check: http://{pi_ip}:8000/status")

def main():
    print("🎯 ChoyRoku Setup Wizard")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Setup failed due to missing dependencies")
        return
    
    # Get Raspberry Pi IP
    pi_ip = get_raspberry_pi_ip()
    if not pi_ip:
        print("❌ Setup failed: No Raspberry Pi IP provided")
        return
    
    # Configure Roku IPs
    roku1_ip, roku2_ip = configure_roku_ips()
    if not roku1_ip and not roku2_ip:
        print("❌ Setup failed: No Roku devices configured")
        return
    
    # Update configuration
    if not update_config(pi_ip, roku1_ip, roku2_ip):
        print("❌ Setup failed: Could not update configuration")
        return
    
    # Create startup script
    create_startup_script(pi_ip)
    
    # Print instructions
    print_instructions(pi_ip)

if __name__ == "__main__":
    main() 