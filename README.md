# ChoyRoku - Multi Roku Remote Control

A Flask web application that allows you to control multiple Roku devices from a single web interface.

## Features

- **Multi-device support**: Control multiple Roku devices from one interface
- **Automatic device discovery**: Automatically finds Roku devices on your network
- **Manual device configuration**: Fallback to manually configured IP addresses
- **Remote control**: Send key commands (Home, Up, Down, Left, Right, Select, Back, Play, Pause, Volume)
- **App launching**: Launch YouTube and other apps directly
- **Playlist support**: Launch custom YouTube playlists

## Requirements

- Python 3.7+
- Flask
- requests

## Installation

1. Clone the repository:

```bash
git clone <your-github-repo-url>
cd ChoyRoku
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

1. Update the Roku IP addresses in `ChoyRoku.py`:

```python
ROKU1_IP = "192.168.1.129"  # Replace with your first Roku's IP
ROKU2_IP = "192.168.1.8"    # Replace with your second Roku's IP
```

2. Update your YouTube playlist ID in the `launch_playlist` function:

```python
playlist_id = "PLob1mZcVWOagE6k45H8o_FndW1eqNht00"  # Replace with your playlist ID
```

3. Change the secret key for security:

```python
app.secret_key = "change_this_to_something_secure"  # Replace with a secure key
```

## Usage

1. Run the application:

```bash
python ChoyRoku.py
```

2. Open your web browser and navigate to `http://localhost:8000`

3. Select a Roku device from the dropdown menu

4. Use the interface to:
   - Send remote control commands
   - Launch YouTube
   - Launch your custom playlist

## Network Requirements

- Your computer and Roku devices must be on the same network
- Roku devices must have network discovery enabled
- Port 8060 must be accessible on your Roku devices

## Security Notes

- Change the Flask secret key before deploying
- Consider adding authentication for production use
- The application runs on all interfaces (0.0.0.0) - restrict access as needed

## Troubleshooting

- If automatic discovery fails, ensure your Roku devices are on the same network
- Check that your firewall allows communication on port 8060
- Verify the IP addresses in the configuration are correct

## License

This project is open source and available under the MIT License.
