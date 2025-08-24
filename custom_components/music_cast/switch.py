"""Switch entities for MusicCast integration."""

import logging
from typing import Any, Optional

from homeassistant.components.switch import SwitchEntity
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
    """Set up MusicCast switches from a config entry."""
    coordinator: MusicCastCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    async_add_entities([
        MusicCastAutoDetectionSwitch(coordinator, entry),
        MusicCastStreamingSwitch(coordinator, entry),
    ])


class MusicCastSwitchBase(CoordinatorEntity, SwitchEntity):
    """Base class for MusicCast switches."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator: MusicCastCoordinator, entry: ConfigEntry) -> None:
        """Initialize the switch."""
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


class MusicCastAutoDetectionSwitch(MusicCastSwitchBase):
    """Switch to control automatic audio detection."""

    _attr_name = "Auto Detection"
    _attr_icon = "mdi:auto-mode"

    def __init__(self, coordinator: MusicCastCoordinator, entry: ConfigEntry) -> None:
        """Initialize the auto detection switch."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_auto_detection"

    @property
    def is_on(self) -> Optional[bool]:
        """Return true if auto detection is enabled."""
        if not self.coordinator.last_update_success:
            return None
        
        status = self.coordinator.data.get("status", {})
        auto_detection = status.get("auto_detection", {})
        return auto_detection.get("enabled", False)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        status = self.coordinator.data.get("status", {})
        auto_detection = status.get("auto_detection", {})
        
        return {
            "running": auto_detection.get("running", False),
            "threshold": auto_detection.get("threshold", 0),
            "silence_timeout": auto_detection.get("silence_timeout", 0),
        }

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on auto detection."""
        await self.coordinator.async_enable_auto_detection()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off auto detection."""
        await self.coordinator.async_disable_auto_detection()
        await self.coordinator.async_request_refresh()


class MusicCastStreamingSwitch(MusicCastSwitchBase):
    """Switch to control manual streaming."""

    _attr_name = "Manual Streaming"
    _attr_icon = "mdi:cast-audio"

    def __init__(self, coordinator: MusicCastCoordinator, entry: ConfigEntry) -> None:
        """Initialize the streaming switch."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_streaming"

    @property
    def is_on(self) -> Optional[bool]:
        """Return true if streaming is active."""
        if not self.coordinator.last_update_success:
            return None
        
        status = self.coordinator.data.get("status", {})
        return status.get("streaming", False)

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        if not super().available:
            return False
        
        # Only available if not in auto detection mode
        status = self.coordinator.data.get("status", {})
        auto_detection = status.get("auto_detection", {})
        return not auto_detection.get("running", False)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Start manual streaming."""
        await self.coordinator.async_start_streaming()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Stop streaming."""
        await self.coordinator.async_stop_streaming()
        await self.coordinator.async_request_refresh()