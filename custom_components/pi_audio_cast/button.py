"""Button entities for PiAudioCast integration."""

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
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
    """Set up PiAudioCast button entities from a config entry."""
    coordinator: PiAudioCastCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    async_add_entities([
        PiAudioCastRefreshCastDevicesButton(coordinator, entry),
    ])


class PiAudioCastButtonBase(CoordinatorEntity, ButtonEntity):
    """Base class for PiAudioCast button entities."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator: PiAudioCastCoordinator, entry: ConfigEntry) -> None:
        """Initialize the button entity."""
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


class PiAudioCastRefreshCastDevicesButton(PiAudioCastButtonBase):
    """Button to refresh cast devices discovery."""

    _attr_name = "Refresh Cast Devices"
    _attr_icon = "mdi:refresh"

    def __init__(self, coordinator: PiAudioCastCoordinator, entry: ConfigEntry) -> None:
        """Initialize the refresh cast devices button."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_refresh_cast_devices"

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.coordinator.async_refresh_cast_devices()
        await self.coordinator.async_request_refresh()