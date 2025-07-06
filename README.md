# ChoyRoku - Multi Roku Remote Control

A Flask web application that allows you to control multiple Roku devices from a single web interface.

## Features

- **Multi-device support**: Control multiple Roku devices from one interface
- **Automatic device discovery**: Automatically finds Roku devices on your network
- **Manual device configuration**: Fallback to manually configured IP addresses
- **Remote control**: Send key commands (Home, Up, Down, Left, Right, Select, Back, Play, Pause, Volume)
- **App launching**: Launch YouTube and other apps directly
- **Playlist support**: Launch custom YouTube playlists
- **Mobile-friendly interface**: Responsive design that works on phones and tablets
- **Real-time status monitoring**: Check connection status and device availability

## Requirements

- Python 3.7+
- Flask
- requests

## Quick Setup

### Option 1: Automated Setup (Recommended)

```bash
python3 setup.py
```

This will:

- Check and install dependencies
- Discover Roku devices on your network
- Configure the application
- Create startup scripts
- Provide access instructions

### Option 2: Manual Setup

1. **Install dependencies**:

```bash
pip install -r requirements.txt
```

2. **Discover Roku devices**:

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
   - Apps: Launch YouTube, Netflix, or custom playlist

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

- Change the Flask secret key before deploying
- Consider adding authentication for production use
- The application runs on all interfaces (0.0.0.0) - restrict access as needed
- Use HTTPS in production environments

## Advanced Configuration

### Custom App IDs

Add more apps to the launch section:

```python
# Common Roku App IDs
NETFLIX_APP_ID = "12"
YOUTUBE_APP_ID = "837"
HULU_APP_ID = "2285"
```

### Custom Playlist

Update your YouTube playlist ID:

```python
playlist_id = "YOUR_PLAYLIST_ID_HERE"
```

### Multiple Roku Devices

Add more Roku devices:

```python
ROKU1_IP = "192.168.1.100"
ROKU2_IP = "192.168.1.101"
ROKU3_IP = "192.168.1.102"
```

## API Endpoints

- `GET /` - Main interface
- `POST /select` - Select Roku device
- `POST /send` - Send key command
- `POST /launch` - Launch app
- `POST /launch_playlist` - Launch YouTube playlist
- `GET /status` - Health check

## License

This project is open source and available under the MIT License.
