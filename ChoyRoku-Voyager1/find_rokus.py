#!/usr/bin/env python3
"""
Roku Device Discovery Utility
This script helps find Roku devices on your network and their IP addresses.
"""

import socket
import requests
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def scan_network_for_rokus():
    """Scan the network for Roku devices using multiple methods"""
    print("🔍 Scanning network for Roku devices...")
    print("=" * 50)
    
    found_devices = {}
    
    # Method 1: SSDP Discovery
    print("1. Trying SSDP discovery...")
    ssdp_devices = discover_via_ssdp()
    found_devices.update(ssdp_devices)
    
    # Method 2: Common IP ranges
    print("\n2. Scanning common IP ranges...")
    common_ips = scan_common_ips()
    found_devices.update(common_ips)
    
    # Method 3: Your router's DHCP range
    print("\n3. Scanning DHCP range...")
    dhcp_devices = scan_dhcp_range()
    found_devices.update(dhcp_devices)
    
    return found_devices

def discover_via_ssdp():
    """Discover Roku devices using SSDP protocol"""
    found = {}
    try:
        message = (
            'M-SEARCH * HTTP/1.1\r\n'
            'Host:239.255.255.250:1900\r\n'
            'Man:"ssdp:discover"\r\n'
            'ST:roku:ecp\r\n'
            'MX:3\r\n\r\n'
        )
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(3)
        sock.sendto(message.encode('utf-8'), ('239.255.255.250', 1900))
        
        start_time = time.time()
        while time.time() - start_time < 3:
            try:
                data, addr = sock.recvfrom(1024)
                ip = addr[0]
                if ip not in found:
                    name = re.search(r"FriendlyName: (.*?)\r\n", data.decode(), re.IGNORECASE)
                    device_name = name.group(1) if name else "Roku Device"
                    found[ip] = device_name
                    print(f"   ✅ Found via SSDP: {ip} - {device_name}")
            except socket.timeout:
                break
    except Exception as e:
        print(f"   ❌ SSDP discovery failed: {e}")
    
    return found

def scan_common_ips():
    """Scan common IP addresses where Roku devices might be"""
    found = {}
    common_ips = [
        "192.168.1.4",   # Your current setting
        "192.168.1.8",   # Your second setting
        "192.168.1.100",
        "192.168.1.101",
        "192.168.1.102",
        "192.168.1.103",
        "192.168.1.104",
        "192.168.1.105",
        "192.168.0.100",
        "192.168.0.101",
        "192.168.0.102",
        "192.168.0.103",
        "192.168.0.104",
        "192.168.0.105",
    ]
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_ip = {executor.submit(check_roku_ip, ip): ip for ip in common_ips}
        for future in as_completed(future_to_ip):
            ip = future_to_ip[future]
            try:
                result = future.result()
                if result:
                    found[ip] = result
                    print(f"   ✅ Found at {ip}: {result}")
            except Exception as e:
                pass
    
    return found

def scan_dhcp_range():
    """Scan typical DHCP range (192.168.1.100-200)"""
    found = {}
    base_ip = "192.168.1."
    
    with ThreadPoolExecutor(max_workers=20) as executor:
        future_to_ip = {}
        for i in range(100, 201):
            ip = base_ip + str(i)
            future_to_ip[executor.submit(check_roku_ip, ip)] = ip
        
        for future in as_completed(future_to_ip):
            ip = future_to_ip[future]
            try:
                result = future.result()
                if result:
                    found[ip] = result
                    print(f"   ✅ Found at {ip}: {result}")
            except Exception as e:
                pass
    
    return found

def check_roku_ip(ip):
    """Check if a specific IP has a Roku device"""
    try:
        resp = requests.get(f"http://{ip}:8060/query/device-info", timeout=1)
        if resp.status_code == 200:
            # Extract device name from XML response
            name_match = re.search(r"<user-device-name>(.*?)</user-device-name>", resp.text)
            if name_match:
                return name_match.group(1)
            else:
                # Try to get model info if no user name
                model_match = re.search(r"<model-name>(.*?)</model-name>", resp.text)
                if model_match:
                    return f"Roku {model_match.group(1)}"
                else:
                    return "Roku Device"
    except:
        pass
    return None

def get_network_info():
    """Get basic network information"""
    print("🌐 Network Information:")
    print("=" * 30)
    
    try:
        # Get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        print(f"Local IP: {local_ip}")
        
        # Extract network prefix
        network_prefix = '.'.join(local_ip.split('.')[:-1])
        print(f"Network: {network_prefix}.0/24")
        
    except Exception as e:
        print(f"Could not determine network info: {e}")

def main():
    print("🎯 Roku Device Discovery Tool")
    print("=" * 40)
    
    get_network_info()
    print()
    
    found_devices = scan_network_for_rokus()
    
    print("\n" + "=" * 50)
    print("📋 DISCOVERY RESULTS")
    print("=" * 50)
    
    if found_devices:
        print(f"Found {len(found_devices)} Roku device(s):")
        for ip, name in found_devices.items():
            print(f"  • {ip} - {name}")
        
        print("\n💡 To use these in ChoyRoku.py, update the IP addresses:")
        print("   ROKU1_IP = \"<first_ip>\"")
        if len(found_devices) > 1:
            print("   ROKU2_IP = \"<second_ip>\"")
    else:
        print("❌ No Roku devices found!")
        print("\n💡 Troubleshooting tips:")
        print("   • Make sure your Roku devices are powered on")
        print("   • Ensure they're connected to the same network")
        print("   • Check that network discovery is enabled on your Roku")
        print("   • Try manually checking common IP addresses")

if __name__ == "__main__":
    main() 