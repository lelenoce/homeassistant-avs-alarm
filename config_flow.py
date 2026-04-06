"""Config flow for AVS Alarm integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_USERNAME
from homeassistant.data_entry_flow import FlowResult

from .avs_api import open_session

_LOGGER = logging.getLogger(__name__)

DOMAIN = "avsalarm"


def _parse_zones(raw_zones: str) -> list[int]:
    """Parse a comma-separated list of zone ids."""
    if not raw_zones.strip():
        return []

    zones = []
    for item in raw_zones.split(","):
        cleaned = item.strip()
        if not cleaned:
            continue

        zone = int(cleaned)
        if zone < 1:
            raise ValueError("Zone ids must be positive integers")
        zones.append(zone)

    return sorted(set(zones))


def _serialize_zones(zones: list[int]) -> str:
    """Serialize zones to a comma-separated string."""
    return ",".join(str(zone) for zone in zones)


async def _async_validate_connection(
    flow: config_entries.ConfigFlow | config_entries.OptionsFlow,
    host: str,
    port: int,
    username: str,
    pid: str,
) -> bool:
    """Validate the connection to the AVS panel."""
    return await flow.hass.async_add_executor_job(
        open_session,
        host,
        port,
        username,
        pid,
    )

class AVSAlarmConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for AVS Alarm."""

    VERSION = 1

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return AVSAlarmOptionsFlow(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                zones = _parse_zones(user_input.get("zones", ""))
                result = await _async_validate_connection(
                    self,
                    user_input[CONF_HOST],
                    user_input[CONF_PORT],
                    user_input[CONF_USERNAME],
                    user_input["pid"],
                )

                if result:
                    user_input = {
                        **user_input,
                        "zones": zones,
                    }
                    return self.async_create_entry(
                        title=f"AVS Alarm ({user_input['pid']})",
                        data=user_input,
                    )
                else:
                    errors["base"] = "cannot_connect"
            except ValueError:
                errors["base"] = "invalid_zones"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Required(CONF_PORT, default=80): int,
                    vol.Required(CONF_USERNAME): str,
                    vol.Required("pid"): str,
                    vol.Required("sectors", default=1): vol.All(vol.Coerce(int), vol.Range(min=1, max=4)),
                    vol.Optional("zones", default=""): str,
                }
            ),
            errors=errors,
        ) 


class AVSAlarmOptionsFlow(config_entries.OptionsFlow):
    """Handle AVS Alarm options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the integration options."""
        errors = {}

        if user_input is not None:
            try:
                zones = _parse_zones(user_input.get("zones", ""))
                result = await _async_validate_connection(
                    self,
                    user_input[CONF_HOST],
                    user_input[CONF_PORT],
                    user_input[CONF_USERNAME],
                    user_input["pid"],
                )
                if not result:
                    errors["base"] = "cannot_connect"
                    raise ValueError("Cannot connect")

                self.hass.config_entries.async_update_entry(
                    self.config_entry,
                    data={
                        **self.config_entry.data,
                        CONF_HOST: user_input[CONF_HOST],
                        CONF_PORT: user_input[CONF_PORT],
                        CONF_USERNAME: user_input[CONF_USERNAME],
                        "pid": user_input["pid"],
                    },
                    title=f"AVS Alarm ({user_input['pid']})",
                )
                return self.async_create_entry(
                    title="",
                    data={
                        "sectors": user_input["sectors"],
                        "zones": zones,
                    },
                )
            except ValueError:
                if "base" not in errors:
                    errors["base"] = "invalid_zones"

        current_host = self.config_entry.data.get(CONF_HOST, "")
        current_port = self.config_entry.data.get(CONF_PORT, 80)
        current_username = self.config_entry.data.get(CONF_USERNAME, "")
        current_pid = self.config_entry.data.get("pid", "")
        current_sectors = self.config_entry.options.get(
            "sectors",
            self.config_entry.data.get("sectors", 1),
        )
        current_zones = self.config_entry.options.get(
            "zones",
            self.config_entry.data.get("zones", []),
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_HOST,
                        default=current_host,
                    ): str,
                    vol.Required(
                        CONF_PORT,
                        default=current_port,
                    ): int,
                    vol.Required(
                        CONF_USERNAME,
                        default=current_username,
                    ): str,
                    vol.Required(
                        "pid",
                        default=current_pid,
                    ): str,
                    vol.Required(
                        "sectors",
                        default=current_sectors,
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=4)),
                    vol.Optional(
                        "zones",
                        default=_serialize_zones(current_zones),
                    ): str,
                }
            ),
            errors=errors,
        )
