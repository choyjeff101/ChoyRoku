# Controku Multi Roku - Flask App
# Requirements: flask, requests
# Run: pip install flask requests

from flask import Flask, render_template_string, request, session, redirect, jsonify
import requests
import socket
import re
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = "change_this_to_something_secure"

# Define manual Roku IPs - Update these with your actual Roku IP addresses
ROKU1_IP = "192.168.1.4"
ROKU2_IP = "192.168.1.8"  # Add second Roku if you have one

# Network configuration
FLASK_HOST = "0.0.0.0"  # Listen on all interfaces
FLASK_PORT = 8000

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>ChoyRoku</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .device-select { margin: 20px 0; }
        .control-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin: 20px 0; }
        button { padding: 15px; font-size: 16px; border: none; border-radius: 5px; cursor: pointer; }
        .nav-btn { background: #007bff; color: white; }
        .media-btn { background: #28a745; color: white; }
        .volume-btn { background: #ffc107; color: black; }
        .app-btn { background: #dc3545; color: white; }
        .status { margin: 10px 0; padding: 10px; border-radius: 5px; }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
        select { padding: 10px; font-size: 16px; margin-right: 10px; }
    </style>
</head>
<body>
  <h2>ChoyRoku: Multi Roku Remote</h2>

  <div class="device-select">
    <h3>Select a Roku Device</h3>
    <form method="post" action="/select">
      <select name="roku_ip">
        {% for ip, name in devices.items() %}
          <option value="{{ ip }}" {% if selected == ip %}selected{% endif %}>{{ name }} ({{ ip }})</option>
        {% endfor %}
      </select>
      <button type="submit" class="nav-btn">Select Device</button>
    </form>
  </div>

  {% if selected %}
  <div class="status success">
    Connected to: {{ devices[selected] }} ({{ selected }})
  </div>

  <h3>Navigation Controls</h3>
  <div class="control-grid">
    <form method="post" action="/send" style="grid-column: 2;">
      <input type="hidden" name="key" value="Up">
      <button type="submit" class="nav-btn">▲ Up</button>
    </form>
    <form method="post" action="/send" style="grid-column: 1;">
      <input type="hidden" name="key" value="Left">
      <button type="submit" class="nav-btn">◀ Left</button>
    </form>
    <form method="post" action="/send" style="grid-column: 2;">
      <input type="hidden" name="key" value="Select">
      <button type="submit" class="nav-btn">OK</button>
    </form>
    <form method="post" action="/send" style="grid-column: 3;">
      <input type="hidden" name="key" value="Right">
      <button type="submit" class="nav-btn">Right ▶</button>
    </form>
    <form method="post" action="/send" style="grid-column: 2;">
      <input type="hidden" name="key" value="Down">
      <button type="submit" class="nav-btn">▼ Down</button>
    </form>
  </div>

  <h3>Media Controls</h3>
  <div class="control-grid">
    <form method="post" action="/send">
      <input type="hidden" name="key" value="Play">
      <button type="submit" class="media-btn">▶ Play</button>
    </form>
    <form method="post" action="/send">
      <input type="hidden" name="key" value="Pause">
      <button type="submit" class="media-btn">⏸ Pause</button>
    </form>
    <form method="post" action="/send">
      <input type="hidden" name="key" value="Back">
      <button type="submit" class="media-btn">◀ Back</button>
    </form>
    <form method="post" action="/send">
      <input type="hidden" name="key" value="Home">
      <button type="submit" class="media-btn">🏠 Home</button>
    </form>
  </div>

  <h3>Volume Controls</h3>
  <div class="control-grid">
    <form method="post" action="/send">
      <input type="hidden" name="key" value="VolumeUp">
      <button type="submit" class="volume-btn">🔊 Vol+</button>
    </form>
    <form method="post" action="/send">
      <input type="hidden" name="key" value="VolumeDown">
      <button type="submit" class="volume-btn">🔉 Vol-</button>
    </form>
  </div>

  <h3>Quick Launch Apps</h3>
  <div class="control-grid">
    <form method="post" action="/launch">
      <input type="hidden" name="app_id" value="837">
      <button type="submit" class="app-btn">📺 YouTube</button>
    </form>
    <form method="post" action="/launch">
      <input type="hidden" name="app_id" value="12">
      <button type="submit" class="app-btn">📺 Netflix</button>
    </form>

  </div>

  {% if error_message %}
  <div class="status error">
    Error: {{ error_message }}
  </div>
  {% endif %}

  {% else %}
  <div class="status error">
    Please select a Roku device to start controlling it.
  </div>
  {% endif %}

  <div style="margin-top: 30px; font-size: 12px; color: #666;">
    <p>Server: {{ server_info }}</p>
    <p>Available devices: {{ device_count }}</p>
  </div>
</body>
</html>
'''

def discover_rokus(timeout=3):
    """Discover Roku devices on the network"""
    fallback_ips = [ROKU1_IP]
    if ROKU2_IP:
        fallback_ips.append(ROKU2_IP)
    
    found = {}
    
    # Try SSDP discovery first
    try:
        logger.info("Attempting SSDP discovery...")
        message = (
            'M-SEARCH * HTTP/1.1\r\n'
            'Host:239.255.255.250:1900\r\n'
            'Man:"ssdp:discover"\r\n'
            'ST:roku:ecp\r\n'
            'MX:2\r\n\r\n'
        )
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(timeout)
        sock.sendto(message.encode('utf-8'), ('239.255.255.250', 1900))

        while True:
            data, addr = sock.recvfrom(1024)
            ip = addr[0]
            if ip not in found:
                name = re.search(r"FriendlyName: (.*?)\r\n", data.decode(), re.IGNORECASE)
                found[ip] = name.group(1) if name else "Roku Device"
                logger.info(f"Found Roku via SSDP: {ip} - {found[ip]}")
    except socket.timeout:
        logger.info("SSDP discovery timed out")
    except Exception as e:
        logger.error(f"SSDP discovery failed: {e}")

    # Fallback to manual IP checking
    if not found:
        logger.info("Trying manual IP discovery...")
        for ip in fallback_ips:
            try:
                resp = requests.get(f"http://{ip}:8060/query/device-info", timeout=2)
                if resp.status_code == 200:
                    name_match = re.search(r"<user-device-name>(.*?)</user-device-name>", resp.text)
                    found[ip] = name_match.group(1) if name_match else f"Roku ({ip})"
                    logger.info(f"Found Roku via manual check: {ip} - {found[ip]}")
            except Exception as e:
                logger.error(f"Manual check failed for {ip}: {e}")

    return found

def test_roku_connection(roku_ip):
    """Test if a Roku device is reachable"""
    try:
        resp = requests.get(f"http://{roku_ip}:8060/query/device-info", timeout=3)
        return resp.status_code == 200
    except Exception as e:
        logger.error(f"Connection test failed for {roku_ip}: {e}")
        return False

@app.route("/", methods=["GET"])
def index():
    keys = ["Home", "Up", "Down", "Left", "Right", "Select", "Back", "Play", "Pause", "VolumeUp", "VolumeDown"]
    devices = discover_rokus()
    selected = session.get("roku_ip")
    
    # Test connection to selected device
    error_message = None
    if selected and selected not in devices:
        error_message = f"Selected device {selected} is no longer available"
        session.pop("roku_ip", None)
        selected = None
    elif selected and not test_roku_connection(selected):
        error_message = f"Cannot connect to {selected}. Please check network connection."
    
    server_info = f"{FLASK_HOST}:{FLASK_PORT}"
    device_count = len(devices)
    
    return render_template_string(HTML, keys=keys, devices=devices, selected=selected, 
                                error_message=error_message, server_info=server_info, 
                                device_count=device_count)

@app.route("/select", methods=["POST"])
def select():
    selected_ip = request.form["roku_ip"]
    if test_roku_connection(selected_ip):
        session["roku_ip"] = selected_ip
        logger.info(f"Selected Roku device: {selected_ip}")
        return redirect("/")
    else:
        logger.error(f"Failed to connect to selected device: {selected_ip}")
        return redirect("/")

@app.route("/send", methods=["POST"])
def send():
    key = request.form["key"]
    roku_ip = session.get("roku_ip")
    if not roku_ip:
        return jsonify({"error": "No Roku selected"}), 400
    
    try:
        logger.info(f"Sending key '{key}' to {roku_ip}")
        r = requests.post(f"http://{roku_ip}:8060/keypress/{key}", timeout=5)
        if r.status_code == 200:
            logger.info(f"Successfully sent {key} to {roku_ip}")
            return jsonify({"success": True, "message": f"Sent {key}"}), 200
        else:
            logger.error(f"Failed to send {key} to {roku_ip}. Status: {r.status_code}")
            return jsonify({"error": f"Failed to send {key}. Status: {r.status_code}"}), 500
    except Exception as e:
        logger.error(f"Error sending {key} to {roku_ip}: {e}")
        return jsonify({"error": f"Error sending {key}: {str(e)}"}), 500

@app.route("/launch", methods=["POST"])
def launch():
    app_id = request.form["app_id"]
    roku_ip = session.get("roku_ip")
    if not roku_ip:
        return jsonify({"error": "No Roku selected"}), 400
    
    try:
        logger.info(f"Launching app {app_id} on {roku_ip}")
        r = requests.post(f"http://{roku_ip}:8060/launch/{app_id}", timeout=5)
        if r.status_code in [200, 204]:
            logger.info(f"Successfully launched app {app_id} on {roku_ip}")
            return jsonify({"success": True, "message": f"Launched app {app_id}"}), 200
        else:
            logger.error(f"Failed to launch app {app_id} on {roku_ip}. Status: {r.status_code}")
            return jsonify({"error": f"Failed to launch app {app_id}. Status: {r.status_code}"}), 500
    except Exception as e:
        logger.error(f"Error launching app {app_id} on {roku_ip}: {e}")
        return jsonify({"error": f"Error launching app {app_id}: {str(e)}"}), 500



@app.route("/status", methods=["GET"])
def status():
    """Health check endpoint"""
    roku_ip = session.get("roku_ip")
    if roku_ip and test_roku_connection(roku_ip):
        return jsonify({"status": "connected", "roku_ip": roku_ip}), 200
    else:
        return jsonify({"status": "disconnected", "roku_ip": roku_ip}), 200

if __name__ == "__main__":
    logger.info(f"Starting ChoyRoku server on {FLASK_HOST}:{FLASK_PORT}")
    logger.info("Make sure your Roku devices are on the same network and accessible")
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=False)
