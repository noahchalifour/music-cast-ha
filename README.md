[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg)](https://github.com/hacs/integration)

# MusicCast Home Assistant Integration

This integration allows you to control and configure a MusicCast server from Home Assistant.

## Features

### Media Player
- Main control interface for MusicCast
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
3. Search for "MusicCast" in HACS and install
4. Restart Home Assistant
5. Go to Configuration > Integrations
6. Click "Add Integration" and search for "MusicCast"
7. Enter your MusicCast server's host and port (default: localhost:8000)

## Manual Installation

1. Download the latest release from GitHub
2. Copy the `musiccast` folder to your Home Assistant `custom_components` directory
3. Restart Home Assistant
4. Follow steps 5-7 from HACS installation

## Configuration

The integration requires:
- **Host**: IP address or hostname of your MusicCast server
- **Port**: Port number (default: 8000)
- **Scan Interval**: How often to poll the server for updates (default: 30 seconds)

## Services

The integration provides several services for automation:

- `musiccast.set_audio_device`: Set the audio input device
- `musiccast.connect_cast_device`: Connect to a specific cast device
- `musiccast.start_auto_detection`: Start auto detection
- `musiccast.stop_auto_detection`: Stop auto detection
- `musiccast.start_streaming`: Start manual streaming
- `musiccast.stop_streaming`: Stop streaming
- `musiccast.refresh_cast_devices`: Refresh cast devices list

## Example Automation

```yaml
# Start streaming when motion is detected
automation:
  - alias: "Start audio streaming on motion"
    trigger:
      - platform: state
        entity_id: binary_sensor.motion_detector
        to: "on"
    action:
      - service: switch.turn_on
        entity_id: switch.musiccast_auto_detection

# Stop streaming when no motion for 10 minutes
  - alias: "Stop audio streaming after motion timeout"
    trigger:
      - platform: state
        entity_id: binary_sensor.motion_detector
        to: "off"
        for:
          minutes: 10
    action:
      - service: switch.turn_off
        entity_id: switch.musiccast_auto_detection
```

## Troubleshooting

### Connection Issues
- Ensure your MusicCast server is running and accessible
- Check that the host and port are correct
- Verify firewall settings allow connections to the server

### Auto Detection Not Working
- Check that an audio input device is selected
- Verify a Google Cast device is connected
- Adjust the audio threshold if needed
- Check the MusicCast server logs for errors

### Cast Device Not Found
- Use the "Refresh Cast Devices" button to rediscover devices
- Ensure your cast devices are on the same network
- Check that the devices are powered on and not in use by another application