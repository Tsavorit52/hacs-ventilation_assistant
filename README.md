# Ventilation Assistant

A Home Assistant custom integration that recommends whether windows should be opened or closed based on indoor/outdoor temperature, humidity, and CO2 levels.

## Installation

Place this repository in your Home Assistant configuration folder with the following structure:

```
/config/custom_components/ventilation_assistant/
```

Then restart Home Assistant and add the integration from `Settings -> Devices & Services -> Add Integration`.

## HACS

This repository is set up as a HACS custom integration. Add the repository URL in HACS under `Integrations -> Custom repositories`, then install `Ventilation Assistant`.

## Contents

- `custom_components/ventilation_assistant/` - integration files
- `hacs.json` - HACS repository metadata
- `README.md` - root repository description
- `.gitignore` - safe Git ignore rules for Home Assistant development
