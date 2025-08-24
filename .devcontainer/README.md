# MusicCast HA Integration - Dev Container

This dev container provides a complete development environment for the MusicCast Home Assistant integration.

## What's Included

- Python 3.11
- Home Assistant core
- Testing framework (pytest with HA custom component support)
- Code formatting and linting tools (black, flake8, pylint, isort)
- VS Code extensions for Python development
- Pre-commit hooks support

## Getting Started

1. Open this project in VS Code
2. When prompted, click "Reopen in Container" or use Command Palette: "Dev Containers: Reopen in Container"
3. Wait for the container to build and install dependencies
4. Start developing!

## Available Commands

```bash
# Format code
black custom_components/

# Run linting
flake8 custom_components/
pylint custom_components/

# Sort imports
isort custom_components/

# Run tests
pytest tests/

# Install pre-commit hooks
pre-commit install
```

## Testing with Home Assistant

The container includes Home Assistant core, so you can test your integration directly:

```bash
# Create a test Home Assistant configuration
mkdir -p config/custom_components
cp -r custom_components/music_cast config/custom_components/

# Run Home Assistant (in background)
hass -c config &

# Access at http://localhost:8123
```

## Port Forwarding

- Port 8123 is automatically forwarded for Home Assistant web interface
- You can add additional ports in devcontainer.json if needed

## VS Code Configuration

The container includes pre-configured VS Code settings for:
- Python development with proper interpreter
- Auto-formatting on save with black
- Import organization with isort
- Linting with pylint and flake8
- YAML syntax highlighting