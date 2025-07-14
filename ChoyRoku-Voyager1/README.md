# ChoyRoku - Voyager1 Edition

**Voyager1/Windows 10 Configuration**

- This version is configured for the Windows 10 machine 'voyager1' on LAN 'choy'.
- The default Roku device IPs are set to `192.168.1.x` (replace 'x' with your Roku's actual address).
- If you need to change the Roku IPs, edit `ROKU1_IP` and `ROKU2_IP` in `ChoyRoku.py`.

# ChoyRoku - Multi Roku Remote Control

A Flask web application that allows you to control multiple Roku devices from a single web interface.

## Features

- **Multi-device support**: Control multiple Roku devices from one interface
- **Automatic device discovery**: Uses SSDP to automatically find Roku devices on your network
- **Manual device configuration**: Fallback to manually configured IP addresses
- **Remote control**: Send key commands (Home, Up, Down, Left, Right, Select, Back, Play, Pause, Volume)
- **App launching**: Launch YouTube and Netflix directly
- **Playlist support**: Launch custom YouTube playlists
- **Mobile-friendly interface**: Responsive design that works on phones and tablets
- **Real-time status monitoring**: Check connection status and device availability

## Requirements

- Python 3.7+
- Flask 2.3.3
- requests 2.31.0

## Quick Setup

### Option 1: Automated Setup (Recommended)

```bash
python3 setup.py
```

This will:

- Check and install dependencies
- Discover Roku devices on your network
- Configure the application automatically
- Create startup scripts
- Provide access instructions

### Option 2: Manual Setup

1. **Install dependencies**:

```bash
pip install -r requirements.txt
```

2. **Discover Roku devices** (optional):

```bash
python3 find_rokus.py
```

3. **Update configuration** in `ChoyRoku.py`:

```python
ROKU1_IP = "192.x.x.x"  # Replace with your first Roku's IP
ROKU2_IP = "192.x.x.x"  # Replace with your second Roku's IP
```

4. **Run the application**:

```bash
python3 ChoyRoku.py
```

## Network Architecture

```
[iPhone (uranus)] ←→ [Raspberry Pi (pi-choy)] ←→ [Roku Device]
     (Client)              (Flask Server)           (Target)
```

- **iPhone (uranus)**: Accesses the web interface
- **Raspberry Pi (pi-choy)**: Runs the Flask server
- **Roku Device**: Receives control commands

## Usage

1. **Start the server** on your Raspberry Pi:

```bash
python3 ChoyRoku.py
```

2. **Access from your iPhone**:

   - Open Safari
   - Navigate to `http://[pi-choy-ip]:8000`
   - Select your Roku device from the dropdown
   - Use the control buttons to control your Roku

3. **Control your Roku**:
   - Navigation: Up, Down, Left, Right, Select
   - Media: Play, Pause, Back, Home
   - Volume: Volume Up, Volume Down
   - Apps: Launch YouTube, Netflix

## Network Requirements

- All devices must be on the same local network
- Raspberry Pi must be accessible from your iPhone
- Roku devices must have network discovery enabled
- Port 8060 must be accessible on your Roku devices
- Port 8000 must be accessible on your Raspberry Pi

## Troubleshooting

### Connection Issues

**Problem**: iPhone can't connect to the Flask app

- **Solution**: Verify both devices are on the same network
- **Check**: Try accessing `http://[pi-choy-ip]:8000` from a computer on the same network

**Problem**: Flask app can't connect to Roku device

- **Solution**: Run `python3 find_rokus.py` to rediscover devices
- **Check**: Verify Roku IP addresses in `ChoyRoku.py`

**Problem**: Control buttons don't appear after selecting device

- **Solution**: Check the browser console for JavaScript errors
- **Check**: Verify the Flask app is running and accessible

### Network Configuration

**Find your Raspberry Pi IP**:

```bash
hostname -I
```

**Find your Roku IP**:

```bash
python3 find_rokus.py
```

**Test connectivity**:

```bash
# Test Flask app
curl http://localhost:8000

# Test Roku device
curl http://[roku-ip]:8060/query/device-info
```

### Common Issues

1. **Firewall blocking port 8000**:

   ```bash
   # On Raspberry Pi
   sudo ufw allow 8000
   ```

2. **Roku device not responding**:

   - Check Roku is powered on and connected to network
   - Verify network discovery is enabled in Roku settings
   - Try restarting the Roku device

3. **Flask app not starting**:

   - Check Python dependencies are installed
   - Verify port 8000 is not in use
   - Check file permissions

4. **iPhone can't reach Raspberry Pi**:
   - Verify both devices are on same WiFi network
   - Check Raspberry Pi firewall settings
   - Try accessing from a computer first

## Security Notes

- Change the Flask secret key in `ChoyRoku.py` line 16 before deploying
- Consider adding authentication for production use
- The application runs on all interfaces (0.0.0.0) - restrict access as needed
- Use HTTPS in production environments

## Advanced Configuration

### Custom App IDs

The application currently supports these apps:

```python
# Current app IDs in ChoyRoku.py
YOUTUBE_APP_ID = "837"    # Line 124
NETFLIX_APP_ID = "12"     # Line 127
```

To add more apps, modify the HTML template in `ChoyRoku.py` around lines 124-132.

### Adding More Roku Devices

To support more than 2 Roku devices, you'll need to modify the `discover_rokus()` function in `ChoyRoku.py` to include additional IP addresses.

## API Endpoints

- `GET /` - Main web interface
- `POST /select` - Select a Roku device
- `POST /send` - Send a key command to the selected Roku
- `POST /launch` - Launch an app on the selected Roku

- `GET /status` - Health check endpoint

## File Structure

```
ChoyRoku/
├── ChoyRoku.py          # Main Flask application
├── setup.py             # Automated setup script
├── find_rokus.py        # Roku device discovery tool
├── requirements.txt     # Python dependencies
├── start_choyroku.sh    # Startup script (created by setup.py)
└── README.md           # This file
```

## Development

The application uses:

- **Flask** for the web framework
- **requests** for HTTP communication with Roku devices
- **socket** for SSDP device discovery
- **re** for regular expressions
- **logging** for debug output

All configuration is embedded in `ChoyRoku.py` and can be modified directly or through the `setup.py` script.
