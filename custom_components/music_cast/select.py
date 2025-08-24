"""Select entities for MusicCast integration."""

import logging
from typing import Optional

from homeassistant.components.select import SelectEntity
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
    """Set up MusicCast select entities from a config entry."""
    coordinator: MusicCastCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    async_add_entities([
        MusicCastAudioDeviceSelect(coordinator, entry),
        MusicCastCastDeviceSelect(coordinator, entry),
    ])


class MusicCastSelectBase(CoordinatorEntity, SelectEntity):
    """Base class for MusicCast select entities."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator: MusicCastCoordinator, entry: ConfigEntry) -> None:
        """Initialize the select entity."""
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


class MusicCastAudioDeviceSelect(MusicCastSelectBase):
    """Select entity for audio input device."""

    _attr_name = "Audio Input Device"
    _attr_icon = "mdi:microphone"

    def __init__(self, coordinator: MusicCastCoordinator, entry: ConfigEntry) -> None:
        """Initialize the audio device select."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_audio_device_select"

    @property
    def options(self) -> list[str]:
        """Return available audio devices."""
        audio_devices = self.coordinator.data.get("audio_devices", {})
        devices = audio_devices.get("devices", [])
        
        options = []
        for device in devices:
            device_name = device.get("name", f"Device {device.get('index', 'Unknown')}")
            options.append(device_name)
        
        return options or ["No devices available"]

    @property
    def current_option(self) -> Optional[str]:
        """Return current audio device."""
        audio_devices = self.coordinator.data.get("audio_devices", {})
        current_device_index = audio_devices.get("current_device")
        
        if current_device_index is None:
            return None
        
        devices = audio_devices.get("devices", [])
        for device in devices:
            if device.get("index") == current_device_index:
                return device.get("name", f"Device {current_device_index}")
        
        return None

    async def async_select_option(self, option: str) -> None:
        """Select audio device option."""
        audio_devices = self.coordinator.data.get("audio_devices", {})
        devices = audio_devices.get("devices", [])
        
        # Find device index by name
        device_index = None
        for device in devices:
            if device.get("name") == option:
                device_index = device.get("index")
                break
        
        if device_index is not None:
            await self.coordinator.async_set_audio_device(device_index)
            await self.coordinator.async_request_refresh()


class MusicCastCastDeviceSelect(MusicCastSelectBase):
    """Select entity for cast device."""

    _attr_name = "Cast Device"
    _attr_icon = "mdi:cast"

    def __init__(self, coordinator: MusicCastCoordinator, entry: ConfigEntry) -> None:
        """Initialize the cast device select."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_cast_device_select"

    @property
    def options(self) -> list[str]:
        """Return available cast devices."""
        cast_devices = self.coordinator.data.get("cast_devices", {})
        devices = cast_devices.get("devices", [])
        
        options = ["None"]  # Option to disconnect
        for device in devices:
            device_name = device.get("name", "Unknown Device")
            options.append(device_name)
        
        return options

    @property
    def current_option(self) -> str:
        """Return current cast device."""
        status = self.coordinator.data.get("status", {})
        cast_device = status.get("cast_device", {})
        
        if cast_device.get("connected", False):
            return cast_device.get("device_name", "Unknown")
        
        return "None"

    async def async_select_option(self, option: str) -> None:
        """Select cast device option."""
        if option == "None":
            # Disconnect current device (if any) by stopping auto detection
            await self.coordinator.async_stop_auto_detection()
            await self.coordinator.async_request_refresh()
            return
        
        cast_devices = self.coordinator.data.get("cast_devices", {})
        devices = cast_devices.get("devices", [])
        
        # Find device UUID by name
        device_uuid = None
        for device in devices:
            if device.get("name") == option:
                device_uuid = device.get("uuid")
                break
        
        if device_uuid:
            await self.coordinator.async_connect_cast_device(device_uuid)
            await self.coordinator.async_request_refresh()