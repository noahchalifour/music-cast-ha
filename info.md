[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg)](https://github.com/hacs/integration)

# PiAudioCast Home Assistant Integration

This integration allows you to control and configure a PiAudioCast server from Home Assistant.

## Features

### Media Player
- Main control interface for PiAudioCast
- Turn on/off auto detection
- Volume control and muting
- Shows current streaming status

### Switches
- **Auto Detection**: Enable/disable automatic audio detection and streaming
- **Manual Streaming**: Start/stop manual streaming (only available when auto detection is off)

### Sensors
- **Status**: Overall system status (Streaming, Auto Detection, Idle, etc.)
- **Audio Input Device**: Currently selected audio input device
- **Cast Device**: Currently connected Google Cast device
- **Connected Clients**: Number of clients connected to the audio server

### Number Controls
- **Audio Threshold**: Set the audio detection threshold (0.001-1.0)
- **Silence Timeout**: Set how long to wait before stopping stream after silence (1-300 seconds)

### Select Controls
- **Audio Input Device**: Choose which audio input device to use
- **Cast Device**: Choose which Google Cast device to connect to

### Buttons
- **Refresh Cast Devices**: Force refresh the list of available cast devices

## Installation via HACS

1. Ensure that [HACS](https://hacs.xyz/) is installed
2. Add this repository to HACS as a custom repository (if not in default HACS store)
3. Search for "PiAudioCast" in HACS and install
4. Restart Home Assistant
5. Go to Configuration > Integrations
6. Click "Add Integration" and search for "PiAudioCast"
7. Enter your PiAudioCast server's host and port (default: localhost:8000)

## Manual Installation

1. Download the latest release from GitHub
2. Copy the `piaudiocast` folder to your Home Assistant `custom_components` directory
3. Restart Home Assistant
4. Follow steps 5-7 from HACS installation

## Configuration

The integration requires:
- **Host**: IP address or hostname of your PiAudioCast server
- **Port**: Port number (default: 8000)
- **Scan Interval**: How often to poll the server for updates (default: 30 seconds)