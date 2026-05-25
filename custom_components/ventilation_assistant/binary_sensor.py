from __future__ import annotations

from datetime import datetime

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
    BinarySensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event

from .const import (
    CONF_INSIDE_CO2,
    CONF_INSIDE_HUMIDITY,
    CONF_INSIDE_TEMPERATURE,
    CONF_OUTSIDE_HUMIDITY,
    CONF_OUTSIDE_TEMPERATURE,
    DOMAIN,
)
from .helpers import calculate_window_recommendation


class VentilationAssistantBinarySensor(BinarySensorEntity):
    entity_description = BinarySensorEntityDescription(
        key="open_windows",
        name="Window ventilation",
        device_class=BinarySensorDeviceClass.WINDOW,
    )

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self._entry = entry
        self._attr_name = "Ventilation Assistant"
        self._attr_unique_id = f"{entry.entry_id}_ventilation_recommendation"
        self._attr_is_on = False
        self._attr_extra_state_attributes = {}
        self._listener_remove = None

    async def async_added_to_hass(self) -> None:
        sensor_ids = [
            self._entry.data[CONF_INSIDE_TEMPERATURE],
            self._entry.data[CONF_INSIDE_HUMIDITY],
            self._entry.data[CONF_INSIDE_CO2],
            self._entry.data[CONF_OUTSIDE_TEMPERATURE],
            self._entry.data[CONF_OUTSIDE_HUMIDITY],
        ]

        self._listener_remove = async_track_state_change_event(
            self.hass, sensor_ids, self._async_sensor_updated
        )
        self._async_update_state()

    async def async_will_remove_from_hass(self) -> None:
        if self._listener_remove is not None:
            self._listener_remove()
            self._listener_remove = None

    @callback
    def _async_sensor_updated(self, event) -> None:
        self._async_update_state()

    @callback
    def _async_update_state(self) -> None:
        inside_temp = self._get_numeric_state(self._entry.data[CONF_INSIDE_TEMPERATURE])
        inside_humidity = self._get_numeric_state(self._entry.data[CONF_INSIDE_HUMIDITY])
        inside_co2 = self._get_numeric_state(self._entry.data[CONF_INSIDE_CO2])
        outside_temp = self._get_numeric_state(self._entry.data[CONF_OUTSIDE_TEMPERATURE])
        outside_humidity = self._get_numeric_state(self._entry.data[CONF_OUTSIDE_HUMIDITY])

        open_windows, attributes = calculate_window_recommendation(
            inside_temp=inside_temp,
            outside_temp=outside_temp,
            inside_rh=inside_humidity,
            outside_rh=outside_humidity,
            inside_co2=inside_co2,
            now=datetime.now(),
        )

        self._attr_is_on = open_windows
        self._attr_extra_state_attributes = attributes
        self.async_write_ha_state()

    def _get_numeric_state(self, entity_id: str) -> float | None:
        state = self.hass.states.get(entity_id)
        if state is None:
            return None

        if state.state in (STATE_UNKNOWN, STATE_UNAVAILABLE, "unknown", "unavailable"):
            return None

        try:
            return float(state.state)
        except (TypeError, ValueError):
            return None


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities([VentilationAssistantBinarySensor(hass, entry)])
