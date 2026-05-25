import math
from datetime import datetime

from homeassistant.const import UnitOfTemperature


def saturation_vapor_pressure(temp_celsius: float) -> float:
    """Return saturation vapor pressure in hPa using the Magnus formula."""
    return 6.112 * math.exp(17.62 * temp_celsius / (243.12 + temp_celsius))


def absolute_humidity(temp_celsius: float, relative_humidity: float) -> float | None:
    """Return absolute humidity in g/m³ from temperature and relative humidity."""
    if temp_celsius is None or relative_humidity is None:
        return None

    try:
        rel = float(relative_humidity)
    except (TypeError, ValueError):
        return None

    vapor_pressure = saturation_vapor_pressure(temp_celsius) * rel / 100.0
    return 216.7 * (vapor_pressure / (temp_celsius + 273.15))


def month_in_range(month: int, start: int, end: int) -> bool:
    """Return True if month is in the inclusive range start..end handling wrap-around."""
    if start <= end:
        return start <= month <= end
    # wrap-around (e.g., start=11, end=3)
    return month >= start or month <= end


def season_label(
    now: datetime,
    outside_temp: float | None,
    winter_start: int = 12,
    winter_end: int = 3,
    summer_start: int = 6,
    summer_end: int = 9,
) -> str:
    """Return season label for ventilation logic, using configurable month ranges."""
    month = now.month
    if month_in_range(month, winter_start, winter_end) or (
        outside_temp is not None and outside_temp <= 10
    ):
        return "winter"
    if month_in_range(month, summer_start, summer_end) or (
        outside_temp is not None and outside_temp >= 20
    ):
        return "summer"
    return "transition"


def calculate_window_recommendation(
    inside_temp: float | None,
    outside_temp: float | None,
    inside_rh: float | None,
    outside_rh: float | None,
    inside_co2: float | None,
    now: datetime,
    co2_threshold: int = 1200,
    winter_start: int = 12,
    winter_end: int = 3,
    summer_start: int = 6,
    summer_end: int = 9,
) -> tuple[bool, dict[str, float | str | None]]:
    """Return whether windows should be opened and numeric state attributes."""
    values = {
        "season": season_label(now, outside_temp, winter_start, winter_end, summer_start, summer_end),
        "inside_temperature": inside_temp,
        "outside_temperature": outside_temp,
        "inside_humidity": inside_rh,
        "outside_humidity": outside_rh,
        "inside_co2": inside_co2,
        "inside_absolute_humidity": None,
        "outside_absolute_humidity": None,
        "reason": None,
    }

    if inside_temp is None or outside_temp is None or inside_rh is None or outside_rh is None or inside_co2 is None:
        values["reason"] = "missing sensor data"
        return False, values

    inside_ah = absolute_humidity(inside_temp, inside_rh)
    outside_ah = absolute_humidity(outside_temp, outside_rh)
    values["inside_absolute_humidity"] = round(inside_ah, 2) if inside_ah is not None else None
    values["outside_absolute_humidity"] = round(outside_ah, 2) if outside_ah is not None else None

    season = values["season"]
    temp_delta = outside_temp - inside_temp
    mold_condition = inside_ah is not None and inside_ah >= 9.0
    co2_condition = inside_co2 is not None and inside_co2 >= co2_threshold
    outside_cooler = temp_delta < -0.5
    outside_hotter = temp_delta > 1.0
    outside_dryer = outside_ah is not None and inside_ah is not None and outside_ah + 2 <= inside_ah

    if season == "winter":
        if not (mold_condition or co2_condition):
            values["reason"] = "no winter mold or CO2 need"
            return False, values

        if outside_temp < inside_temp - 5 and outside_temp < 10:
            values["reason"] = "outside too cold for winter airing"
            return False, values

        values["reason"] = "winter ventilation for mold or CO2"
        return True, values

    if season == "summer" and outside_hotter:
        values["reason"] = "outside warmer than inside in summer"
        return False, values

    if mold_condition and outside_dryer and outside_temp <= inside_temp + 2:
        values["reason"] = "reduce mold risk with cooler, dryer air"
        return True, values

    if co2_condition and outside_temp <= inside_temp + 2 and (outside_ah is None or outside_ah <= inside_ah + 5):
        values["reason"] = "reduce indoor CO2 with outside air"
        return True, values

    if outside_cooler and (outside_ah is None or outside_ah <= inside_ah + 5):
        values["reason"] = "cool indoor air with cooler outside air"
        return True, values

    values["reason"] = "no ventilation conditions met"
    return False, values
