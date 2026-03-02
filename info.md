# LM Sensors Integration

Monitor system hardware sensors: temperature, fans, voltage, power consumption.

## Requirements

Install `lm-sensors` on your system:

```bash
# Debian/Ubuntu
apt-get install lm-sensors && sensors-detect

# Docker (Alpine)
docker exec homeassistant apk add lm-sensors

# Fedora/RHEL
dnf install lm_sensors && sensors-detect
```

**Docker users:** Re-run after container updates (5 seconds).

## Quick Start

1. Install via HACS
2. Restart Home Assistant
3. Settings → Devices & Services → Add Integration
4. Search "LM Sensors"

All sensors automatically discovered and added as entities.

## Troubleshooting

**Permission errors:** Add homeassistant user to groups:
```bash
usermod -a -G adm,dialout,i2c homeassistant
```

**Proxmox users:** See [PROXMOX.md](https://github.com/aisaiev/ha-lm-sensors/blob/main/PROXMOX.md) for privileged containers.

Full documentation: [README.md](https://github.com/aisaiev/ha-lm-sensors/blob/main/README.md)
