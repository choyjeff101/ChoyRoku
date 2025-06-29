# ChoyRoku - Multi Roku Remote Control

A Flask web application that allows you to control multiple Roku devices from a single web interface.

## Features

- Control multiple Roku devices from one interface
- Basic remote control functions (Home, Navigation, Play/Pause, Volume)
- Launch YouTube app
- Launch custom YouTube playlists
- Automatic Roku device discovery via SSDP

## Installation

1. Clone the repository:

```bash
git clone <your-repo-url>
cd ChoyRoku
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the application:

```bash
python ChoyRoku.py
```

4. Open your browser and navigate to `http://localhost:8000`

## Configuration

Update the Roku IP addresses in `ChoyRoku.py`:

```python
ROKU1_IP = "192.168.1.129"  # Replace with your Roku IP
ROKU2_IP = "192.168.1.8"    # Replace with your Roku IP
```

## Usage

1. Select a Roku device from the dropdown
2. Use the remote control buttons to navigate
3. Launch YouTube or custom playlists

## Requirements

- Python 3.6+
- Flask
- requests
- Network access to Roku devices (port 8060)
