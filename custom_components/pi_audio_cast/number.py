"""Number entities for PiAudioCast integration."""

import logging
from typing import Optional

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    AUDIO_THRESHOLD_MIN,
    AUDIO_THRESHOLD_MAX,
    SILENCE_TIMEOUT_MIN,
    SILENCE_TIMEOUT_MAX,
)
from .coordinator import PiAudioCastCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up PiAudioCast number entities from a config entry."""
    coordinator: PiAudioCastCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    async_add_entities([
        PiAudioCastAudioThresholdNumber(coordinator, entry),
        PiAudioCastSilenceTimeoutNumber(coordinator, entry),
    ])


class PiAudioCastNumberBase(CoordinatorEntity, NumberEntity):
    """Base class for PiAudioCast number entities."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.CONFIG
    _attr_mode = NumberMode.BOX

    def __init__(self, coordinator: PiAudioCastCoordinator, entry: ConfigEntry) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=f"PiAudioCast ({coordinator.host})",
            manufacturer="PiAudioCast",
            model="Audio Cast Server",
            sw_version="1.0.0",
            configuration_url=coordinator.base_url,
        )

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success


class PiAudioCastAudioThresholdNumber(PiAudioCastNumberBase):
    """Number entity for audio detection threshold."""

    _attr_name = "Audio Threshold"
    _attr_icon = "mdi:volume-high"
    _attr_native_min_value = AUDIO_THRESHOLD_MIN
    _attr_native_max_value = AUDIO_THRESHOLD_MAX
    _attr_native_step = 0.001
    _attr_native_unit_of_measurement = None

    def __init__(self, coordinator: PiAudioCastCoordinator, entry: ConfigEntry) -> None:
        """Initialize the audio threshold number."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_audio_threshold"

    @property
    def native_value(self) -> Optional[float]:
        """Return the current audio threshold."""
        if not self.coordinator.last_update_success:
            return None
        
        status = self.coordinator.data.get("status", {})
        auto_detection = status.get("auto_detection", {})
        return auto_detection.get("threshold", 0.01)

    async def async_set_native_value(self, value: float) -> None:
        """Set the audio threshold."""
        await self.coordinator.async_set_audio_threshold(value)
        await self.coordinator.async_request_refresh()


class PiAudioCastSilenceTimeoutNumber(PiAudioCastNumberBase):
    """Number entity for silence timeout."""

    _attr_name = "Silence Timeout"
    _attr_icon = "mdi:timer"
    _attr_native_min_value = SILENCE_TIMEOUT_MIN
    _attr_native_max_value = SILENCE_TIMEOUT_MAX
    _attr_native_step = 0.5
    _attr_native_unit_of_measurement = "s"

    def __init__(self, coordinator: PiAudioCastCoordinator, entry: ConfigEntry) -> None:
        """Initialize the silence timeout number."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_silence_timeout"

    @property
    def native_value(self) -> Optional[float]:
        """Return the current silence timeout."""
        if not self.coordinator.last_update_success:
            return None
        
        status = self.coordinator.data.get("status", {})
        auto_detection = status.get("auto_detection", {})
        return auto_detection.get("silence_timeout", 5.0)

    async def async_set_native_value(self, value: float) -> None:
        """Set the silence timeout."""
        await self.coordinator.async_set_silence_timeout(value)
        await self.coordinator.async_request_refresh()