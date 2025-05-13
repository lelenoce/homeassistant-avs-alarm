"""The AVS Alarm Sensor integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .avs_api import AVSAlarmCoordinator

_LOGGER = logging.getLogger(__name__)

class AVSAlarmSensor(CoordinatorEntity, SensorEntity):
    """Representation of an AVS Alarm sensor."""

    def __init__(
        self,
        coordinator: AVSAlarmCoordinator,
        name: str,
        sector: int,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._name = name
        self._sector = sector
        self._attr_unique_id = f"avs_alarm_sensor_{sector}"
        self._attr_icon = "mdi:shield-check"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._name

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None

        return self.coordinator.data.get(f"sector_{self._sector}")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        if not self.coordinator.data:
            return {}
            
        sector_status = self.coordinator.data.get(f"sector_{self._sector}")
        return {
            "sector": self._sector,
            "status": sector_status
        }

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the AVS Alarm sensors from a config entry."""
    coordinator = hass.data["avsalarm"][entry.entry_id]
    num_sectors = entry.data.get("sectors", 1)

    sensors = [
        AVSAlarmSensor(coordinator, f"AVS Alarm Sector {sector} Status", sector)
        for sector in range(1, num_sectors + 1)
    ]

    async_add_entities(sensors)

__all__ = ["async_setup_entry"]