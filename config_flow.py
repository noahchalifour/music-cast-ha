"""Config flow for PiAudioCast integration."""

import asyncio
import logging
from typing import Any, Dict, Optional

import aiohttp
import async_timeout
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN,
    DEFAULT_HOST,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    CONF_SCAN_INTERVAL,
    ERROR_CANNOT_CONNECT,
    ERROR_INVALID_HOST,
    ERROR_TIMEOUT,
)

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
    vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.All(vol.Coerce(int), vol.Range(min=1, max=65535)),
    vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(vol.Coerce(int), vol.Range(min=5, max=300)),
})


class PiAudioCastConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for PiAudioCast."""

    VERSION = 1

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None) -> FlowResult:
        """Handle the initial step."""
        errors: Dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            port = user_input[CONF_PORT]
            
            # Check if already configured
            await self.async_set_unique_id(f"{host}:{port}")
            self._abort_if_unique_id_configured()

            # Test connection
            error = await self._test_connection(host, port)
            if error:
                errors["base"] = error
            else:
                title = f"PiAudioCast ({host}:{port})"
                return self.async_create_entry(title=title, data=user_input)

        return self.async_show_form(
            step_id="user", 
            data_schema=DATA_SCHEMA, 
            errors=errors
        )

    async def _test_connection(self, host: str, port: int) -> Optional[str]:
        """Test if we can connect to the PiAudioCast server."""
        session = async_get_clientsession(self.hass)
        url = f"http://{host}:{port}/"
        
        try:
            with async_timeout.timeout(10):
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        if "PyAudioCast" in data.get("message", ""):
                            return None
                        else:
                            return ERROR_INVALID_HOST
                    else:
                        return ERROR_CANNOT_CONNECT
        except asyncio.TimeoutError:
            return ERROR_TIMEOUT
        except aiohttp.ClientError:
            return ERROR_CANNOT_CONNECT
        except Exception as ex:
            _LOGGER.exception("Unexpected error connecting to PiAudioCast: %s", ex)
            return ERROR_CANNOT_CONNECT