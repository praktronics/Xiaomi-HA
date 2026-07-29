# Xiaomi Air Purifier (Home Assistant)

Custom Home Assistant integration for the **Xiaomi Air Purifier** model `xiaomi.airp.mb5` (and compatible MIoT variants using the same schema).

Communication is local over the miIO/MIoT protocol using [python-miio](https://github.com/rytilahti/python-miio). No Xiaomi cloud connection is required at runtime.

## Features

| Category | Capability |
|----------|------------|
| Control | Power on/off |
| Control | Fan level (1–3) |
| Control | Preset modes: Auto, Sleep, Favorite, Manual |
| Control | Screen on/off |
| Control | Anion (ionizer) on/off |
| Control | UV on/off |
| Sensors | Temperature (°C) |
| Sensors | Relative humidity (%) |
| Sensors | PM1, PM2.5, PM10 (µg/m³) |
| Sensors | Fan motor speed (RPM) |
| Sensors | Filter life (%) and remaining hours |
| Sensors | Air quality label |

Multiple purifiers are supported: add the integration once per device (each has its own IP and token).

## Requirements

- Home Assistant 2024.1 or newer (Home Assistant OS, Container, Core, or Supervised)
- Air purifier on the **same local network** as Home Assistant
- Device **IP address** and **32-character miIO token**

### Getting the token

Common options:

1. **XiaomiMiio.Cli** (in this monorepo) — query the device and dump schema/token metadata
2. Community token extractors for the Mi Home / Xiaomi Home app (version-dependent)
3. Cloud token tools such as [Xiaomi-cloud-tokens-extractor](https://github.com/PiotrMachowski/Xiaomi-cloud-tokens-extractor)

The token is 32 hexadecimal characters (for example `0123456789abcdef0123456789abcdef`).

---

## Install on Home Assistant OS

These steps assume Home Assistant OS with the **Samba share** or **Studio Code Server** add-on available. Any method that can write files under `/config` works the same way.

### 1. Create the custom components folder

If it does not already exist:

```text
/config/custom_components/
```

### 2. Copy the integration

Copy the folder:

```text
xiaomi_air_purifier/
```

from this repository:

```text
xiaomi-air_purifier/custom_components/xiaomi_air_purifier/
```

so that on the Home Assistant host you have:

```text
/config/custom_components/xiaomi_air_purifier/
├── __init__.py
├── config_flow.py
├── const.py
├── coordinator.py
├── device.py
├── entity.py
├── fan.py
├── manifest.json
├── sensor.py
├── strings.json
├── switch.py
└── translations/
    └── en.json
```

#### Option A — Samba share add-on

1. Install **Samba share** from Settings → Add-ons.
2. Start it and note the share credentials.
3. On your PC, open the `config` share.
4. Create `custom_components` if needed.
5. Copy the `xiaomi_air_purifier` directory into `custom_components`.

#### Option B — Studio Code Server / File editor

1. Install **Studio Code Server** (or **File editor**) from Add-ons.
2. Open `/config`.
3. Create `custom_components/xiaomi_air_purifier/`.
4. Paste/upload all integration files listed above.

#### Option C — SSH / Terminal add-on

```bash
mkdir -p /config/custom_components
# From a machine that has this repo checked out:
scp -r xiaomi-air_purifier/custom_components/xiaomi_air_purifier \
  root@homeassistant.local:/config/custom_components/
```

Or with the Terminal add-on and a downloaded zip of this project:

```bash
cd /config
unzip Xiaomi-HA.zip
cp -r Xiaomi-HA/xiaomi-air_purifier/custom_components/xiaomi_air_purifier \
  /config/custom_components/
```

### 3. Restart Home Assistant

Settings → System → **Restart**

Home Assistant will install the `python-miio` dependency declared in `manifest.json` on first load.

### 4. Add the integration

1. Go to **Settings → Devices & services**.
2. Click **Add integration**.
3. Search for **Xiaomi Air Purifier**.
4. Enter:
   - **IP address** — e.g. `192.168.4.225`
   - **Token** — 32-character hex token
5. Submit.

On success, a device appears with fan, switches, and sensors.

### 5. Add another purifier (optional)

Repeat **Add integration** with the other device’s IP and token. Each device is tracked by its MAC address so entities stay unique across restarts.

---

## Entities created

| Platform | Entity | Notes |
|----------|--------|--------|
| `fan` | Air purifier | On/off, speed %, presets |
| `switch` | Screen | Display on/off |
| `switch` | Anion | Ionizer |
| `switch` | UV | UV lamp |
| `sensor` | Temperature | °C |
| `sensor` | Humidity | % |
| `sensor` | PM1 / PM2.5 / PM10 | µg/m³ |
| `sensor` | Fan speed | RPM (diagnostic) |
| `sensor` | Filter life | % remaining (diagnostic) |
| `sensor` | Filter remaining | Hours left (diagnostic) |
| `sensor` | Air quality | Text label |

Polling interval defaults to **30 seconds**.

---

## Troubleshooting

| Symptom | What to check |
|---------|----------------|
| “Failed to connect” during setup | IP reachable from HA (`ping`); device on same L2/L3 network; token correct and lowercase hex |
| Integration missing after copy | Path must be `/config/custom_components/xiaomi_air_purifier/manifest.json`; restart HA |
| Entities unavailable | Device offline or Wi‑Fi changed; update IP via remove/re-add if needed |
| Token rejected | Must be exactly 32 hex chars; cloud-bound tokens sometimes change after app reset |

Enable debug logs in `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.xiaomi_air_purifier: debug
    miio: debug
```

---

## Device schema

MIoT property/action definitions used by this integration live in:

```text
schema/xiaomi.airp.mb5.json
```

Generated with the XiaomiMiio.Cli utility from a live device.

## Development layout

```text
xiaomi-air_purifier/
├── AGENTS.md
├── README.md
├── schema/
│   └── xiaomi.airp.mb5.json
└── custom_components/
    └── xiaomi_air_purifier/
        └── ...
```
