"""The AVS Alarm Binary Sensor integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .avs_api import AVSAlarmCoordinator

_LOGGER = logging.getLogger(__name__)

class AVSAlarmArmedBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of an AVS Alarm binary sensor."""

    def __init__(
        self,
        coordinator: AVSAlarmCoordinator,
        sector: int,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._sector = sector
        self._attr_name = f"AVS Alarm Sector {sector} Armed"
        self._attr_unique_id = f"avs_alarm_sector_{sector}_armed"
        self._attr_icon = "mdi:shield-lock"

    @property
    def name(self) -> str:
        """Return the name of the binary sensor."""
        return self._attr_name

    @property
    def is_on(self) -> bool:
        """Return true if the binary sensor is on (armed)."""
        if not self.coordinator.data:
            return False

        sector_status = self.coordinator.data.get(f"sector_{self._sector}")
        return sector_status in ["Perimeter armed", "Area armed", "Home armed", "ON"]

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        if not self.coordinator.data:
            return {
                "sector": self._sector,
                "state_text": "Unknown"
            }
            
        sector_status = self.coordinator.data.get(f"sector_{self._sector}", "Unknown")
        return {
            "sector": self._sector,
            "state_text": sector_status,
            "armed": self.is_on
        }

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the AVS Alarm binary sensors from a config entry."""
    coordinator = hass.data["avsalarm"][entry.entry_id]
    num_sectors = entry.data.get("sectors", 1)

    binary_sensors = [
        AVSAlarmArmedBinarySensor(coordinator, sector)
        for sector in range(1, num_sectors + 1)
    ]

    async_add_entities(binary_sensors)

__all__ = ["async_setup_entry"]
