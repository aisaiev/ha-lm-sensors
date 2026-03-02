# LM Sensors Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

Hardware monitoring integration using Linux `lm-sensors`. Reads temperature, fan speed, voltage, power, current, and energy data.

## Quick Setup

### Home Assistant Core (Native Linux)
```bash
sudo apt-get install lm-sensors
sudo sensors-detect
```
Done! Add the integration.

### Home Assistant Container (Docker)
```bash
# Alpine-based (official image):
docker exec homeassistant apk add --no-cache lm-sensors

# Debian/Ubuntu-based:
docker run ... -v /usr/bin/sensors:/usr/bin/sensors:ro -v /sys:/sys:ro
```

### Proxmox LXC
See [PROXMOX.md](PROXMOX.md) for Proxmox-specific setup (permissions, privileged containers, etc.)

## Features

- 🌡️ **Temperature sensors** - CPU, motherboard, GPU temperatures
- 🌀 **Fan speed monitoring** - All system fans
- ⚡ **Voltage sensors** - Power supply and component voltages
- 🔌 **Power consumption** - Power draw of components
- 📊 **Current sensors** - Current draw monitoring
- ⚙️ **Easy configuration** - UI-based setup through Home Assistant
- 🔄 **Configurable update interval** - Set how often sensors are polled

## Prerequisites

Install `lm-sensors` on your system:

```bash
# Debian/Ubuntu/Raspberry Pi
sudo apt-get install lm-sensors && sudo sensors-detect

# Fedora/RHEL/CentOS
sudo dnf install lm_sensors && sudo sensors-detect

# Arch Linux
sudo pacman -S lm_sensors && sudo sensors-detect

# Alpine (Docker containers)
apk add --no-cache lm-sensors

# Verify it works
sensors -u
```

## Setup by Installation Type

### Home Assistant Core

1. Install lm-sensors (see Prerequisites above)
2. Add integration in Home Assistant

**If permission error:**
```bash
sudo usermod -a -G adm,dialout,i2c homeassistant
sudo systemctl restart home-assistant@homeassistant.service
```

### Home Assistant Container (Docker)

**Alpine (official image):**
```bash
docker exec homeassistant apk add --no-cache lm-sensors
```

**After container updates:** Re-run the command above (takes 5 seconds).

**Debian/Ubuntu:**
```bash
# Mount sensors from host
-v /usr/bin/sensors:/usr/bin/sensors:ro -v /sys:/sys:ro
```

### Home Assistant OS

Not supported (locked down OS).

### Proxmox LXC

See [PROXMOX.md](PROXMOX.md) for privileged containers and kernel modules.

## Installation

### HACS (Recommended)

1. HACS → Integrations → ⋮ → Custom repositories
2. Add: `https://github.com/aisaiev/ha-lm-sensors` (Category: Integration)
3. Install "LM Sensors"
4. Restart Home Assistant

### Manual

1. Copy `custom_components/lm_sensors/` to `<config>/custom_components/lm_sensors/`
2. Restart Home Assistant

## Configuration

1. Settings → Devices & Services → Add Integration
2. Search "LM Sensors"
3. Set scan interval (default: 60 seconds)

**To modify:** Settings → Devices & Services → LM Sensors → Configure

## Sensor Entities

The integration creates sensor entities for each detected hardware sensor. Entity names are automatically generated based on the chip and feature name.

### Example Sensors:

- `sensor.coretemp_isa_0000_core_0` - CPU core temperature
- `sensor.it8728_isa_0a30_fan1` - System fan speed
- `sensor.it8728_isa_0a30_in0` - Voltage sensor
- `sensor.k10temp_pci_00c3_vddcr_soc` - SoC voltage

### Sensor Types:

- **Temperature** - Unit: °C, Device Class: temperature
- **Fan Speed** - Unit: RPM
- **Voltage** - Unit: V, Device Class: voltage
- **Power** - Unit: W, Device Class: power
- **Current** - Unit: A, Device Class: current
- **Energy** - Unit: J, Device Class: energy

## Usage Examples

### Temperature Alert Automation

```yaml
automation:
  - alias: "CPU Temperature Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.coretemp_isa_0000_core_0
        above: 80
    action:
      - service: notify.notify
        data:
          message: "CPU temperature is {{ states('sensor.coretemp_isa_0000_core_0') }}°C"
```

### Dashboard Card

```yaml
type: entities
title: Hardware Monitoring
entities:
  - sensor.coretemp_isa_0000_core_0
  - sensor.it8728_isa_0a30_fan1
```

## Troubleshooting

**"Cannot connect" error:**

1. Verify sensors work: `sensors -u`
2. Check Home Assistant logs: Settings → System → Logs

**Solutions by type:**

- **Core:** Fix permissions - `sudo usermod -a -G adm,dialout,i2c homeassistant`
- **Docker:** Install in container - `docker exec homeassistant apk add lm-sensors`  
- **Proxmox:** See [PROXMOX.md](PROXMOX.md)

**No sensors found:**
- Run `sensors-detect` (answer YES to safe questions)
- Proxmox: Enable privileged container

## Development

### Project Structure

```
custom_components/lm_sensors/
├── __init__.py          # Integration setup
├── config_flow.py       # UI configuration
├── const.py             # Constants
├── manifest.json        # Integration metadata
├── sensor.py            # Sensor platform
├── sensor_reader.py     # lm-sensors interface
├── strings.json         # UI strings
├── brand/               # Brand images (Home Assistant API)
│   ├── icon.png         # Integration icon (256x256 or 512x512)
│   └── logo.png         # Integration logo (256x256 or 512x512)
└── translations/
    └── en.json          # English translations
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

## Support

If you encounter any issues or have questions:
- Open an issue on [GitHub](https://github.com/aisaiev/ha-lm-sensors/issues)
- Check existing issues for solutions

## Changelog

### Version 0.1.0
- Initial release
- Support for temperature, fan, voltage, power, current, and energy sensors
- UI-based configuration
- Configurable scan interval
- Automatic sensor discovery
