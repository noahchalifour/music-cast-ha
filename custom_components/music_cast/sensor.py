"""Sensor entities for MusicCast integration."""

import logging
from typing import Any, Optional

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import MusicCastCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up MusicCast sensors from a config entry."""
    coordinator: MusicCastCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    async_add_entities([
        MusicCastStatusSensor(coordinator, entry),
        MusicCastAudioDeviceSensor(coordinator, entry),
        MusicCastCastDeviceSensor(coordinator, entry),
        MusicCastConnectedClientsSensor(coordinator, entry),
    ])


class MusicCastSensorBase(CoordinatorEntity, SensorEntity):
    """Base class for MusicCast sensors."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: MusicCastCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=f"MusicCast ({coordinator.host})",
            manufacturer="MusicCast",
            model="Audio Cast Server",
            sw_version="1.0.0",
            configuration_url=coordinator.base_url,
        )

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success


class MusicCastStatusSensor(MusicCastSensorBase):
    """Sensor showing overall MusicCast status."""

    _attr_name = "Status"
    _attr_icon = "mdi:information"

    def __init__(self, coordinator: MusicCastCoordinator, entry: ConfigEntry) -> None:
        """Initialize the status sensor."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_status"

    @property
    def native_value(self) -> Optional[str]:
        """Return the status."""
        if not self.coordinator.last_update_success:
            return "Unavailable"
        
        status = self.coordinator.data.get("status", {})
        cast_device = status.get("cast_device", {})
        
        if not cast_device.get("connected", False):
            return "No Cast Device"
        
        if status.get("streaming", False):
            return "Streaming"
        
        auto_detection = status.get("auto_detection", {})
        if auto_detection.get("running", False):
            return "Auto Detection"
        
        return "Idle"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        status = self.coordinator.data.get("status", {})
        
        return {
            "streaming": status.get("streaming", False),
            "auto_detection_enabled": status.get("auto_detection", {}).get("enabled", False),
            "auto_detection_running": status.get("auto_detection", {}).get("running", False),
            "cast_connected": status.get("cast_device", {}).get("connected", False),
        }


class MusicCastAudioDeviceSensor(MusicCastSensorBase):
    """Sensor showing current audio input device."""

    _attr_name = "Audio Input Device"
    _attr_icon = "mdi:microphone"

    def __init__(self, coordinator: MusicCastCoordinator, entry: ConfigEntry) -> None:
        """Initialize the audio device sensor."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_audio_device"

    @property
    def native_value(self) -> Optional[str]:
        """Return the current audio device name."""
        audio_devices = self.coordinator.data.get("audio_devices", {})
        current_device_index = audio_devices.get("current_device")
        
        if current_device_index is None:
            return "None"
        
        devices = audio_devices.get("devices", [])
        for device in devices:
            if device.get("index") == current_device_index:
                return device.get("name")
        
        return f"Device {current_device_index}"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        audio_devices = self.coordinator.data.get("audio_devices", {})
        current_device_index = audio_devices.get("current_device")
        
        attrs = {
            "device_index": current_device_index,
            "available_devices": len(audio_devices.get("devices", [])),
        }
        
        if current_device_index is not None:
            devices = audio_devices.get("devices", [])
            for device in devices:
                if device.get("index") == current_device_index:
                    attrs.update({
                        "channels": device.get("channels"),
                        "sample_rate": device.get("sample_rate"),
                    })
                    break
        
        return attrs


class MusicCastCastDeviceSensor(MusicCastSensorBase):
    """Sensor showing current cast device."""

    _attr_name = "Cast Device"
    _attr_icon = "mdi:cast"

    def __init__(self, coordinator: MusicCastCoordinator, entry: ConfigEntry) -> None:
        """Initialize the cast device sensor."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_cast_device"

    @property
    def native_value(self) -> Optional[str]:
        """Return the current cast device name."""
        status = self.coordinator.data.get("status", {})
        cast_device = status.get("cast_device", {})
        
        if cast_device.get("connected", False):
            return cast_device.get("device_name", "Unknown")
        
        return "Not Connected"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        status = self.coordinator.data.get("status", {})
        cast_device = status.get("cast_device", {})
        cast_devices = self.coordinator.data.get("cast_devices", {})
        
        attrs = {
            "connected": cast_device.get("connected", False),
            "available_devices": len(cast_devices.get("devices", [])),
        }
        
        if cast_device.get("connected", False):
            attrs.update({
                "model": cast_device.get("device_model"),
                "status": cast_device.get("display_name"),
                "volume": cast_device.get("volume_level"),
                "muted": cast_device.get("is_muted"),
            })
        
        return attrs


class MusicCastConnectedClientsSensor(MusicCastSensorBase):
    """Sensor showing number of connected audio clients."""

    _attr_name = "Connected Clients"
    _attr_icon = "mdi:account-multiple"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "clients"

    def __init__(self, coordinator: MusicCastCoordinator, entry: ConfigEntry) -> None:
        """Initialize the connected clients sensor."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_connected_clients"

    @property
    def native_value(self) -> Optional[int]:
        """Return the number of connected clients."""
        status = self.coordinator.data.get("status", {})
        audio_server = status.get("audio_server", {})
        return audio_server.get("clients_connected", 0)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        status = self.coordinator.data.get("status", {})
        audio_server = status.get("audio_server", {})
        
        return {
            "recording": audio_server.get("recording", False),
            "server_port": audio_server.get("port"),
        }