from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    CONF_INSIDE_CO2,
    CONF_INSIDE_HUMIDITY,
    CONF_INSIDE_TEMPERATURE,
    CONF_OUTSIDE_HUMIDITY,
    CONF_OUTSIDE_TEMPERATURE,
    DOMAIN,
)


CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_INSIDE_TEMPERATURE): selector.selector(
            {
                "entity": {
                    "domain": "sensor",
                    "device_class": "temperature",
                }
            }
        ),
        vol.Required(CONF_INSIDE_HUMIDITY): selector.selector(
            {
                "entity": {
                    "domain": "sensor",
                    "device_class": "humidity",
                }
            }
        ),
        vol.Required(CONF_INSIDE_CO2): selector.selector(
            {
                "entity": {
                    "domain": "sensor",
                    "device_class": "carbon_dioxide",
                }
            }
        ),
        vol.Required(CONF_OUTSIDE_TEMPERATURE): selector.selector(
            {
                "entity": {
                    "domain": "sensor",
                    "device_class": "temperature",
                }
            }
        ),
        vol.Required(CONF_OUTSIDE_HUMIDITY): selector.selector(
            {
                "entity": {
                    "domain": "sensor",
                    "device_class": "humidity",
                }
            }
        ),
        vol.Optional("co2_threshold", default=1200): selector.selector({
            "number": {"min": 400, "max": 5000, "step": 50}
        }),
        vol.Optional("winter_start_month", default=12): selector.selector({
            "number": {"min": 1, "max": 12, "step": 1}
        }),
        vol.Optional("winter_end_month", default=3): selector.selector({
            "number": {"min": 1, "max": 12, "step": 1}
        }),
        vol.Optional("summer_start_month", default=6): selector.selector({
            "number": {"min": 1, "max": 12, "step": 1}
        }),
        vol.Optional("summer_end_month", default=9): selector.selector({
            "number": {"min": 1, "max": 12, "step": 1}
        }),
    }
)


class VentilationAssistantConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Ventilation Assistant."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle a flow initiated by the user."""
        if user_input is not None:
            return self.async_create_entry(title="Ventilation Assistant", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=CONFIG_SCHEMA,
        )
