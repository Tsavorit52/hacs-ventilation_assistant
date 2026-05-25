# Ventilation Assistant

Home Assistant custom integration for recommending window ventilation based on temperature, humidity, and indoor CO2.

## What it does

- Reads inside temperature, outside temperature, inside humidity, outside humidity, and inside CO2 sensors.
- Computes actual water vapor content to make mold-safe ventilation decisions.
- Uses outside temperature differences to avoid warming the home in summer.
- Prioritizes mold and CO2 in winter while keeping airing periods short.
- Exposes a binary sensor recommendation: `open_windows`.

## Installation

### Manual install

1. Copy this repository into your Home Assistant config folder under `custom_components/ventilation_assistant`.
   - Example: `/config/custom_components/ventilation_assistant`
2. Restart Home Assistant.
3. Go to `Settings -> Devices & Services -> Add Integration`.
4. Search for `Ventilation Assistant` and add it.
5. Select the five sensor entities from the picker in the integration setup.

### HACS install

1. Publish this repository to GitHub or a Git provider.
2. In HACS, choose `Integrations` -> `Custom repositories`.
3. Add your repository URL and select `Integration`.
4. Install `Ventilation Assistant` from HACS.
5. Restart Home Assistant and configure it in `Settings -> Devices & Services`.

## Configuration

You will need to select the following entities:

- Inside temperature sensor
- Outside temperature sensor
- Inside humidity sensor
- Outside humidity sensor
- Inside CO2 sensor

The integration creates a binary sensor.

## Usage

Use the new binary sensor in dashboards and automations:

- `binary_sensor.ventilation_assistant_window_ventilation`

If it is `on`, it is recommending the windows be opened.

## Notes

- The decision is based on absolute moisture content, not relative humidity alone.
- In summer, the integration avoids opening the windows when outside air is hotter than inside.
- In winter, the logic focuses on mold and CO2 prevention, with conservative airing.
