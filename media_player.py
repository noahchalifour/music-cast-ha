"""Media player entity for PiAudioCast integration."""

import logging
from typing import Any, Dict, Optional

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import PiAudioCastCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up PiAudioCast media player from a config entry."""
    coordinator: PiAudioCastCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    async_add_entities([PiAudioCastMediaPlayer(coordinator, entry)])


class PiAudioCastMediaPlayer(CoordinatorEntity, MediaPlayerEntity):
    """Representation of a PiAudioCast media player."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_supported_features = (
        MediaPlayerEntityFeature.VOLUME_SET
        | MediaPlayerEntityFeature.VOLUME_MUTE
        | MediaPlayerEntityFeature.TURN_ON
        | MediaPlayerEntityFeature.TURN_OFF
    )

    def __init__(self, coordinator: PiAudioCastCoordinator, entry: ConfigEntry) -> None:
        """Initialize the media player."""
        super().__init__(coordinator)
        
        self._attr_unique_id = f"{entry.entry_id}_media_player"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=f"PiAudioCast ({coordinator.host})",
            manufacturer="PiAudioCast",
            model="Audio Cast Server",
            sw_version="1.0.0",
            configuration_url=coordinator.base_url,
        )

    @property
    def state(self) -> MediaPlayerState:
        """Return the state of the media player."""
        if not self.coordinator.last_update_success:
            return MediaPlayerState.UNAVAILABLE

        status = self.coordinator.data.get("status", {})
        cast_device = status.get("cast_device", {})
        
        if not cast_device.get("connected", False):
            return MediaPlayerState.OFF
        
        if status.get("streaming", False):
            return MediaPlayerState.PLAYING
        
        auto_detection = status.get("auto_detection", {})
        if auto_detection.get("running", False):
            return MediaPlayerState.ON
        
        return MediaPlayerState.IDLE

    @property
    def volume_level(self) -> Optional[float]:
        """Volume level of the media player (0..1)."""
        status = self.coordinator.data.get("status", {})
        cast_device = status.get("cast_device", {})
        return cast_device.get("volume_level")

    @property
    def is_volume_muted(self) -> Optional[bool]:
        """Boolean if volume is currently muted."""
        status = self.coordinator.data.get("status", {})
        cast_device = status.get("cast_device", {})
        return cast_device.get("is_muted")

    @property
    def media_title(self) -> Optional[str]:
        """Title of current playing media."""
        status = self.coordinator.data.get("status", {})
        if status.get("streaming", False):
            return "PiAudioCast Stream"
        return None

    @property
    def media_artist(self) -> Optional[str]:
        """Artist of current playing media."""
        status = self.coordinator.data.get("status", {})
        cast_device = status.get("cast_device", {})
        if cast_device.get("connected", False):
            return cast_device.get("device_name")
        return None

    @property
    def source(self) -> Optional[str]:
        """Name of the current input source."""
        audio_devices = self.coordinator.data.get("audio_devices", {})
        current_device_index = audio_devices.get("current_device")
        
        if current_device_index is not None:
            devices = audio_devices.get("devices", [])
            for device in devices:
                if device.get("index") == current_device_index:
                    return device.get("name")
        
        return None

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return additional state attributes."""
        status = self.coordinator.data.get("status", {})
        cast_device = status.get("cast_device", {})
        auto_detection = status.get("auto_detection", {})
        
        attrs = {
            "streaming": status.get("streaming", False),
            "auto_detection_enabled": auto_detection.get("enabled", False),
            "auto_detection_running": auto_detection.get("running", False),
            "audio_threshold": auto_detection.get("threshold", 0),
            "silence_timeout": auto_detection.get("silence_timeout", 0),
        }
        
        if cast_device.get("connected", False):
            attrs.update({
                "cast_device_name": cast_device.get("device_name"),
                "cast_device_model": cast_device.get("device_model"),
                "cast_device_status": cast_device.get("display_name"),
            })
        
        return attrs

    async def async_turn_on(self) -> None:
        """Turn on the media player (start auto detection)."""
        await self.coordinator.async_start_auto_detection()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self) -> None:
        """Turn off the media player (stop auto detection and streaming)."""
        await self.coordinator.async_stop_auto_detection()
        await self.coordinator.async_request_refresh()

    async def async_set_volume_level(self, volume: float) -> None:
        """Set volume level, range 0..1."""
        await self.coordinator.async_set_volume(volume)
        await self.coordinator.async_request_refresh()

    async def async_mute_volume(self, mute: bool) -> None:
        """Mute (true) or unmute (false) media player."""
        if mute:
            await self.coordinator.async_mute()
        else:
            await self.coordinator.async_unmute()
        await self.coordinator.async_request_refresh()