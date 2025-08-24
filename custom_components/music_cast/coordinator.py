"""Coordinator for MusicCast integration."""

import asyncio
import logging
from datetime import timedelta
from typing import Any, Dict, List, Optional

import aiohttp
import async_timeout
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class MusicCastCoordinator(DataUpdateCoordinator):
    """Class to manage fetching MusicCast data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize coordinator."""
        self.host = entry.data[CONF_HOST]
        self.port = entry.data[CONF_PORT]
        self.base_url = f"http://{self.host}:{self.port}"
        self.session = async_get_clientsession(hass)
        
        scan_interval = entry.data.get(CONF_SCAN_INTERVAL, 30)
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )

    async def async_setup(self) -> bool:
        """Set up the coordinator."""
        try:
            await self._async_test_connection()
            return True
        except Exception as ex:
            _LOGGER.error("Failed to setup MusicCast coordinator: %s", ex)
            return False

    async def _async_test_connection(self) -> None:
        """Test connection to MusicCast server."""
        try:
            with async_timeout.timeout(10):
                async with self.session.get(f"{self.base_url}/") as response:
                    if response.status != 200:
                        raise UpdateFailed(f"Server returned status {response.status}")
                    
                    data = await response.json()
                    if "MusicCast" not in data.get("message", ""):
                        raise UpdateFailed("Invalid server response")
        except asyncio.TimeoutError as ex:
            raise UpdateFailed("Timeout connecting to server") from ex
        except aiohttp.ClientError as ex:
            raise UpdateFailed(f"Connection error: {ex}") from ex

    async def _async_update_data(self) -> Dict[str, Any]:
        """Fetch data from MusicCast server."""
        try:
            with async_timeout.timeout(10):
                # Get status
                async with self.session.get(f"{self.base_url}/status") as response:
                    if response.status != 200:
                        raise UpdateFailed(f"Status endpoint returned {response.status}")
                    status_data = await response.json()

                # Get audio devices
                async with self.session.get(f"{self.base_url}/audio-devices") as response:
                    if response.status != 200:
                        raise UpdateFailed(f"Audio devices endpoint returned {response.status}")
                    audio_devices_data = await response.json()

                # Get cast devices
                async with self.session.get(f"{self.base_url}/cast-devices") as response:
                    if response.status != 200:
                        raise UpdateFailed(f"Cast devices endpoint returned {response.status}")
                    cast_devices_data = await response.json()

                return {
                    "status": status_data,
                    "audio_devices": audio_devices_data,
                    "cast_devices": cast_devices_data,
                }

        except asyncio.TimeoutError as ex:
            raise UpdateFailed("Timeout fetching data") from ex
        except aiohttp.ClientError as ex:
            raise UpdateFailed(f"Connection error: {ex}") from ex
        except Exception as ex:
            raise UpdateFailed(f"Unexpected error: {ex}") from ex

    async def async_start_auto_detection(self) -> bool:
        """Start automatic audio detection."""
        return await self._async_post_request("/auto-detection/start")

    async def async_stop_auto_detection(self) -> bool:
        """Stop automatic audio detection."""
        return await self._async_post_request("/auto-detection/stop")

    async def async_enable_auto_detection(self) -> bool:
        """Enable automatic audio detection."""
        return await self._async_post_request("/auto-detection/enable")

    async def async_disable_auto_detection(self) -> bool:
        """Disable automatic audio detection."""
        return await self._async_post_request("/auto-detection/disable")

    async def async_start_streaming(self) -> bool:
        """Start manual audio streaming."""
        return await self._async_post_request("/stream/start")

    async def async_stop_streaming(self) -> bool:
        """Stop audio streaming."""
        return await self._async_post_request("/stream/stop")

    async def async_set_volume(self, level: float) -> bool:
        """Set volume level."""
        return await self._async_post_request(f"/volume/{level}")

    async def async_mute(self) -> bool:
        """Mute the cast device."""
        return await self._async_post_request("/mute")

    async def async_unmute(self) -> bool:
        """Unmute the cast device."""
        return await self._async_post_request("/unmute")

    async def async_set_audio_threshold(self, threshold: float) -> bool:
        """Set audio detection threshold."""
        return await self._async_post_request(f"/auto-detection/threshold/{threshold}")

    async def async_set_silence_timeout(self, timeout: float) -> bool:
        """Set silence timeout."""
        return await self._async_post_request(f"/auto-detection/silence-timeout/{timeout}")

    async def async_set_audio_device(self, device_index: int) -> bool:
        """Set audio input device."""
        return await self._async_post_request(f"/audio-devices/{device_index}")

    async def async_connect_cast_device(self, device_uuid: str) -> bool:
        """Connect to a cast device."""
        return await self._async_post_request(f"/cast-devices/{device_uuid}/connect")

    async def async_refresh_cast_devices(self) -> bool:
        """Refresh cast devices list."""
        try:
            with async_timeout.timeout(20):  # Discovery can take longer
                async with self.session.get(f"{self.base_url}/cast-devices?refresh=true") as response:
                    return response.status == 200
        except Exception as ex:
            _LOGGER.error("Failed to refresh cast devices: %s", ex)
            return False

    async def _async_post_request(self, endpoint: str) -> bool:
        """Make a POST request to the server."""
        try:
            with async_timeout.timeout(10):
                async with self.session.post(f"{self.base_url}{endpoint}") as response:
                    success = response.status == 200
                    if not success:
                        _LOGGER.warning(
                            "POST request to %s failed with status %s", 
                            endpoint, response.status
                        )
                    return success
        except Exception as ex:
            _LOGGER.error("Failed POST request to %s: %s", endpoint, ex)
            return False