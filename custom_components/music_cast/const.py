"""Constants for the MusicCast integration."""

DOMAIN = "musiccast"

DEFAULT_PORT = 8000
DEFAULT_HOST = "localhost"
DEFAULT_SCAN_INTERVAL = 30

# Configuration keys
CONF_HOST = "host"
CONF_PORT = "port"
CONF_SCAN_INTERVAL = "scan_interval"

# Error messages
ERROR_CANNOT_CONNECT = "cannot_connect"
ERROR_INVALID_HOST = "invalid_host"
ERROR_TIMEOUT = "timeout"

# Audio threshold limits
AUDIO_THRESHOLD_MIN = 0.001
AUDIO_THRESHOLD_MAX = 1.0

# Silence timeout limits
SILENCE_TIMEOUT_MIN = 1.0
SILENCE_TIMEOUT_MAX = 300.0

# Volume limits
VOLUME_MIN = 0.0
VOLUME_MAX = 1.0