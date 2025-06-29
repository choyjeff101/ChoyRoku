# Controku Multi Roku - Flask App
# Requirements: flask, requests
# Run: pip install flask requests

from flask import Flask, render_template_string, request, session, redirect
import requests
import socket
import re

app = Flask(__name__)
app.secret_key = "change_this_to_something_secure"

# Define manual Roku IPs
ROKU1_IP = "192.168.1.129"
ROKU2_IP = "192.168.1.8"

HTML = '''
<!DOCTYPE html>
<html>
<head><title>Choyku - Multi Roku Remote</title></head>
<body>
  <h2>Choyku: Multi Roku Remote</h2>

  <h3>Select a Roku Device</h3>
  <form method="post" action="/select">
    <select name="roku_ip">
      {% for ip, name in devices.items() %}
        <option value="{{ ip }}" {% if selected == ip %}selected{% endif %}>{{ name }} ({{ ip }})</option>
      {% endfor %}
    </select>
    <button type="submit">Select</button>
  </form>

  {% if selected %}
  <h3>Key Commands for {{ devices[selected] }} ({{ selected }})</h3>
  {% for key in keys %}
    <form method="post" action="/send">
      <input type="hidden" name="key" value="{{ key }}">
      <button type="submit">{{ key }}</button>
    </form>
  {% endfor %}

  <h3>Launch Apps</h3>
  <form method="post" action="/launch">
    <input type="hidden" name="app_id" value="837">
    <button type="submit">Launch YouTube</button>
  </form>

  <h3>Launch Custom Playlist</h3>
  <form method="post" action="/launch_playlist">
    <button type="submit">Play My YouTube Playlist</button>
  </form>
  {% endif %}
</body>
</html>
'''

def discover_rokus(timeout=2):
    fallback_ips = [ROKU1_IP, ROKU2_IP]
    found = {}

    try:
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
    except socket.timeout:
        pass
    except Exception as e:
        print("SSDP discovery failed:", e)

    if not found:
        for ip in fallback_ips:
            try:
                resp = requests.get(f"http://{ip}:8060/query/device-info", timeout=2)
                name_match = re.search(r"<user-device-name>(.*?)</user-device-name>", resp.text)
                found[ip] = name_match.group(1) if name_match else f"Roku ({ip})"
            except Exception as e:
                print(f"Manual check failed for {ip}: {e}")

    return found

@app.route("/", methods=["GET"])
def index():
    keys = ["Home", "Up", "Down", "Left", "Right", "Select", "Back", "Play", "Pause", "VolumeUp", "VolumeDown"]
    devices = discover_rokus()
    selected = session.get("roku_ip")
    return render_template_string(HTML, keys=keys, devices=devices, selected=selected)

@app.route("/select", methods=["POST"])
def select():
    selected_ip = request.form["roku_ip"]
    session["roku_ip"] = selected_ip
    return redirect("/")

@app.route("/send", methods=["POST"])
def send():
    key = request.form["key"]
    roku_ip = session.get("roku_ip")
    if not roku_ip:
        return "No Roku selected", 400
    try:
        r = requests.post(f"http://{roku_ip}:8060/keypress/{key}")
        return f"Sent {key}. Status: {r.status_code}", 200
    except Exception as e:
        return f"Error sending {key}: {e}", 500

@app.route("/launch", methods=["POST"])
def launch():
    app_id = request.form["app_id"]
    roku_ip = session.get("roku_ip")
    if not roku_ip:
        return "No Roku selected", 400
    try:
        r = requests.post(f"http://{roku_ip}:8060/launch/{app_id}")
        return f"Launched app {app_id}. Status: {r.status_code}", 200
    except Exception as e:
        return f"Error launching app {app_id}: {e}", 500

@app.route("/launch_playlist", methods=["POST"])
def launch_playlist():
    roku_ip = session.get("roku_ip")
    if not roku_ip:
        return "No Roku selected", 400
    try:
        playlist_id = "PLob1mZcVWOagE6k45H8o_FndW1eqNht00"  # Replace with your actual unlisted playlist ID
        r = requests.post(f"http://{roku_ip}:8060/launch/837?contentID={playlist_id}")
        return f"Launched YouTube playlist {playlist_id}. Status: {r.status_code}", 200
    except Exception as e:
        return f"Error launching playlist: {e}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
