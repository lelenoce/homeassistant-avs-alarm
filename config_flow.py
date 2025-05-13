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

class AVSAlarmConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for AVS Alarm."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                # Test connection
                result = await self.hass.async_add_executor_job(
                    open_session,
                    user_input[CONF_HOST],
                    user_input[CONF_PORT],
                    user_input[CONF_USERNAME],
                    user_input["pid"],
                )

                if result:
                    return self.async_create_entry(
                        title=f"AVS Alarm ({user_input['pid']})",
                        data=user_input,
                    )
                else:
                    errors["base"] = "cannot_connect"
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
                }
            ),
            errors=errors,
        ) 