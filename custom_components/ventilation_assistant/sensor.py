from __future__ import annotations

from datetime import datetime

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
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


class VentilationAssistantReasonSensor(SensorEntity):
    entity_description = SensorEntityDescription(
        key="ventilation_reason",
        name="Ventilation Decision Reason",
    )

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self._entry = entry
        self._attr_name = "Ventilation Decision Reason"
        self._attr_unique_id = f"{entry.entry_id}_ventilation_reason"
        self._attr_native_value = "Unknown"
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

        from .const import (
            CONF_CO2_THRESHOLD,
            CONF_WINTER_START,
            CONF_WINTER_END,
            CONF_SUMMER_START,
            CONF_SUMMER_END,
            CONF_SUMMER_MIN_TEMP,
            DEFAULT_CO2_THRESHOLD,
            DEFAULT_SUMMER_MIN_TEMP,
        )

        co2_thresh = self._entry.data.get(CONF_CO2_THRESHOLD, DEFAULT_CO2_THRESHOLD)
        winter_start = int(self._entry.data.get(CONF_WINTER_START, 12))
        winter_end = int(self._entry.data.get(CONF_WINTER_END, 3))
        summer_start = int(self._entry.data.get(CONF_SUMMER_START, 6))
        summer_end = int(self._entry.data.get(CONF_SUMMER_END, 9))
        summer_min_temp = int(
            self._entry.data.get(CONF_SUMMER_MIN_TEMP, DEFAULT_SUMMER_MIN_TEMP)
        )

        _, attributes = calculate_window_recommendation(
            inside_temp=inside_temp,
            outside_temp=outside_temp,
            inside_rh=inside_humidity,
            outside_rh=outside_humidity,
            inside_co2=inside_co2,
            now=datetime.now(),
            co2_threshold=co2_thresh,
            winter_start=winter_start,
            winter_end=winter_end,
            summer_start=summer_start,
            summer_end=summer_end,
            summer_min_temp=summer_min_temp,
        )

        self._attr_native_value = attributes.get("reason", "Unknown")
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
    async_add_entities([VentilationAssistantReasonSensor(hass, entry)])
