from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector
from homeassistant.const import UnitOfTemperature, PERCENTAGE, UnitOfConcentration

from .const import (
    CONF_INSIDE_CO2,
    CONF_INSIDE_HUMIDITY,
    CONF_INSIDE_TEMPERATURE,
    CONF_OUTSIDE_HUMIDITY,
    CONF_OUTSIDE_TEMPERATURE,
    DOMAIN,
)


class VentilationAssistantConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="Ventilation Assistant", data=user_input)

        data_schema = vol.Schema(
            {
                vol.Required(CONF_INSIDE_TEMPERATURE, description={"suggested_value": "Inside Temperature"}): selector.selector(
                    {
                        "entity": {
                            "domain": "sensor",
                            "device_class": "temperature",
                        }
                    }
                ),
                vol.Required(CONF_INSIDE_HUMIDITY, description={"suggested_value": "Inside Humidity"}): selector.selector(
                    {
                        "entity": {
                            "domain": "sensor",
                            "device_class": "humidity",
                        }
                    }
                ),
                vol.Required(CONF_INSIDE_CO2, description={"suggested_value": "Inside CO2"}): selector.selector(
                    {
                        "entity": {
                            "domain": "sensor",
                            "device_class": None,
                            "unit_of_measurement": "ppm",
                        }
                    }
                ),
                vol.Required(CONF_OUTSIDE_TEMPERATURE, description={"suggested_value": "Outside Temperature"}): selector.selector(
                    {
                        "entity": {
                            "domain": "sensor",
                            "device_class": "temperature",
                        }
                    }
                ),
                vol.Required(CONF_OUTSIDE_HUMIDITY, description={"suggested_value": "Outside Humidity"}): selector.selector(
                    {
                        "entity": {
                            "domain": "sensor",
                            "device_class": "humidity",
                        }
                    }
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            description_placeholders={
                CONF_INSIDE_TEMPERATURE: "Select a temperature sensor for the inside of your home",
                CONF_INSIDE_HUMIDITY: "Select a humidity sensor for the inside of your home",
                CONF_INSIDE_CO2: "Select a CO2 sensor (PPM) for the inside of your home",
                CONF_OUTSIDE_TEMPERATURE: "Select a temperature sensor for outside",
                CONF_OUTSIDE_HUMIDITY: "Select a humidity sensor for outside",
            },
        )
