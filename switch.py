"""The AVS Alarm Switch integration."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .avs_api import AVSAlarmCoordinator, open_session, edit_sector_status

_LOGGER = logging.getLogger(__name__)

ARMED_STATES = {
    "arm-on": "ON",
    "arm-area": "Area armed",
    "arm-home": "Home armed",
    "arm-perimeter": "Perimeter armed",
}

class AVSAlarmSectorSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of an AVS Alarm sector switch."""

    def __init__(
        self,
        coordinator: AVSAlarmCoordinator,
        sector: int,
        arm_mode: str,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._sector = sector
        self._arm_mode = arm_mode
        self._attr_name = f"AVS Alarm Sector {sector} {arm_mode}"
        self._attr_unique_id = f"avs_alarm_sector_{sector}_{arm_mode}"
        self._attr_icon = "mdi:shield-lock" if arm_mode != "disarm" else "mdi:shield-off"

    @property
    def name(self) -> str:
        """Return the name of the switch."""
        return self._attr_name

    @property
    def is_on(self) -> bool:
        """Return true if the switch is on."""
        if not self.coordinator.data:
            return False

        sector_status = self.coordinator.data.get(f"sector_{self._sector}")
        return ARMED_STATES.get(self._arm_mode) == sector_status

    async def _async_wait_for_state(self, expected_state: str | None) -> None:
        """Retry a few refreshes because the panel may apply the change with delay."""
        for _ in range(5):
            await self.coordinator.async_refresh()
            current_state = self.coordinator.data.get(f"sector_{self._sector}")

            if expected_state is None:
                if current_state not in ARMED_STATES.values():
                    return
            elif current_state == expected_state:
                return

            await asyncio.sleep(1)

    async def async_turn_on(self) -> None:
        """Turn the switch on."""
        try:
            # Apri una nuova sessione (ignoriamo il risultato)
            await self.hass.async_add_executor_job(
                open_session,
                self.coordinator.ip,
                self.coordinator.port,
                self.coordinator.user,
                self.coordinator.pid,
            )

            # Esegui il comando
            result = await self.hass.async_add_executor_job(
                edit_sector_status,
                self.coordinator.ip,
                self.coordinator.port,
                self.coordinator.user,
                self.coordinator.pid,
                self._sector,
                self._arm_mode,
            )

            if result:
                await self._async_wait_for_state(ARMED_STATES[self._arm_mode])
                # Aggiorna lo stato locale
                self.async_write_ha_state()

        except Exception as err:
            _LOGGER.error("Error changing AVS alarm sector: %s", err)
            raise

    async def async_turn_off(self) -> None:
        """Turn the switch off."""
        try:
            # Apri una nuova sessione (ignoriamo il risultato)
            await self.hass.async_add_executor_job(
                open_session,
                self.coordinator.ip,
                self.coordinator.port,
                self.coordinator.user,
                self.coordinator.pid,
            )

            # Esegui il comando
            result = await self.hass.async_add_executor_job(
                edit_sector_status,
                self.coordinator.ip,
                self.coordinator.port,
                self.coordinator.user,
                self.coordinator.pid,
                self._sector,
                "disarm",
            )

            if result:
                await self._async_wait_for_state(None)
                # Aggiorna lo stato locale
                self.async_write_ha_state()

        except Exception as err:
            _LOGGER.error("Error changing AVS alarm sector: %s", err)
            raise

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the AVS Alarm switches from a config entry."""
    coordinator = hass.data["avsalarm"][entry.entry_id]
    num_sectors = entry.data.get("sectors", 1)
    
    switches = []
    arm_modes = ["arm-on", "arm-area", "arm-home", "arm-perimeter"]
    
    for sector in range(1, num_sectors + 1):
        for arm_mode in arm_modes:
            switches.append(AVSAlarmSectorSwitch(coordinator, sector, arm_mode))
    
    async_add_entities(switches)

__all__ = ["async_setup_entry"] 
