# Ventilation Assistant

A Home Assistant custom integration that recommends whether windows should be opened or closed based on indoor/outdoor temperature, humidity, and CO2 levels.

## What it does

- Reads inside temperature, outside temperature, inside humidity, outside humidity, and inside CO2 sensors.
- Computes actual water vapor content to make mold-safe ventilation decisions.
- Uses outside temperature differences to avoid warming the home in summer.
- Prioritizes mold and CO2 in winter while keeping airing periods short.
- Creates two entities: a binary sensor for open/close recommendation and a text sensor explaining the reason.

## Installation

### Manual install

1. Copy this repository into your Home Assistant config folder under `custom_components/ventilation_assistant`.
   - Example: `/config/custom_components/ventilation_assistant`
2. Restart Home Assistant.
3. Go to `Settings -> Devices & Services -> Add Integration`.
4. Search for `Ventilation Assistant` and add it.
5. Select the five sensor entities from the picker in the integration setup.

### HACS install

1. Add this repository to HACS under `Integrations -> Custom repositories`.
2. Search for `Ventilation Assistant` and install it.
3. Restart Home Assistant.
4. Go to `Settings -> Devices & Services -> Add Integration`.
5. Search for `Ventilation Assistant` and configure it.

## Configuration

You will need to select the following entities:

- Inside temperature sensor
- Outside temperature sensor
- Inside humidity sensor
- Outside humidity sensor
- Inside CO2 sensor

The integration creates two entities per configured instance.

### Customizable settings during setup

- You can set a custom **CO2 threshold** (default 1200 ppm) in the integration setup. Recommended default: 1200 ppm (opens windows when CO2 is high).
- You can customize which months are considered **winter** and **summer**. The setup form exposes month numbers (1-12) for winter start/end and summer start/end so the season detection matches your local climate.
- You can set a **summer minimum temperature** (default 22°C). When inside temperature reaches this level during summer, windows are no longer opened for cooling and are only recommended if CO2 levels are high.

## Entities Created

The integration creates two entities:

1. **Binary Sensor** - `binary_sensor.ventilation_assistant_window_ventilation`
   - `on` = Windows should be opened
   - `off` = Windows should be closed

2. **Text Sensor** - `sensor.ventilation_assistant_ventilation_decision_reason`
   - Shows the reason for the current recommendation (e.g., "cool indoor air with cooler outside air", "high mold risk", "outside too hot")

Use these in your dashboards and automations.

## Decision Logic

The integration uses sophisticated environmental analysis to decide whether windows should be opened. Here's exactly how it works:

### Key Concepts

- **Absolute Humidity** – Calculated from temperature and relative humidity using the Magnus formula. This matters more than relative humidity alone for mold prevention.
- **Season Detection** – Automatically determines winter/summer/transition based on calendar date and outside temperature.
- **Temperature Delta** – The difference between outside and inside temperature.

### Mold Prevention (All Seasons)

- **Trigger:** Inside absolute humidity ≥ 9 g/m³ (mold risk threshold)
- **Action:** Windows open when outside air is drier (has at least 2 g/m³ less absolute humidity) and not significantly warmer
- **Reasoning:** Bringing in drier air reduces moisture accumulation that causes mold

### Winter Mode (December–March or outside temp ≤ 10°C)

Focus: Mold + CO2 with minimal airing time

- **Condition 1 (Mold):** If inside absolute humidity is high AND outside is drier AND outside temp ≤ inside temp + 2°C → **Open windows**
- **Condition 2 (CO2):** If inside CO2 ≥ 1200 ppm AND outside temp is reasonable (within 5°C of inside) → **Open windows**
- **Override:** If outside is much colder (> 5°C difference) or below 10°C → **Keep windows closed** to avoid excessive heat loss
- **Otherwise:** → **Keep windows closed**

### Summer Mode (June–September or outside temp ≥ 20°C)

Focus: Temperature control without overheating

- **Heat Block:** If outside temp > inside temp → **Keep windows closed** (to avoid warming the home)
- **Summer minimum temperature:** If the inside temperature reaches the configured summer minimum (default 22°C), windows are only opened for CO2 release and not for cooling.
- **Mold + Drying:** If inside humidity is high AND outside is drier AND outside temp is acceptable → **Open windows**
- **CO2 Management:** If CO2 is high AND outside is not hotter AND outside humidity is reasonable → **Open windows**
- **Cooling Opportunity:** If outside is cooler AND outside humidity is acceptable → **Open windows**
- **Otherwise:** → **Keep windows closed**

### Transition Seasons (Spring/Autumn)

- Uses logic similar to summer when determining whether to open windows
- Balances heating concerns (spring) with cooling needs (autumn)

### All Seasons – Abort Conditions

Windows remain **closed** if:
- Any required sensor is unavailable or returning invalid data
- Outside temperature is dangerously extreme for your region

## Supported Languages

- English
- Deutsch (German)

## Notes

- The decision is based on absolute moisture content, not relative humidity alone.
- In summer, the integration avoids opening the windows when outside air is hotter than inside.
- In winter, the logic focuses on mold and CO2 prevention, with conservative airing.
- Real-time sensor updates trigger immediate recalculation.
- All thresholds and calculations can be customized by editing `helpers.py` if needed.
