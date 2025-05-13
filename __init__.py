"""The AVS Alarm integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .avs_api import AVSAlarmCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.SELECT]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up AVS Alarm from a config entry."""
    coordinator = AVSAlarmCoordinator(
        hass,
        ip=entry.data[CONF_HOST],
        port=entry.data[CONF_PORT],
        user=entry.data[CONF_USERNAME],
        pid=entry.data["pid"],
    )

    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        raise ConfigEntryNotReady(f"Error connecting to AVS Alarm: {err}") from err

    hass.data.setdefault("avsalarm", {})
    hass.data["avsalarm"][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data["avsalarm"].pop(entry.entry_id)

    return unload_ok
