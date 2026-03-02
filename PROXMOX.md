# Proxmox LXC Setup Guide

## Check Your Installation Type

```bash
docker ps 2>/dev/null
```

---

## Docker Installation (Community Scripts)

**If you see a Home Assistant container:**

```bash
docker exec homeassistant apk add --no-cache lm-sensors
```

Done! Add the integration in Home Assistant.

**After updates:** Re-run the command (takes 5 seconds).

**Why:** Community-scripts uses Alpine Linux container. The update command replaces it with fresh official image, so lm-sensors needs reinstalling.

---

## Systemd Installation (LXC Native)

**If "command not found" above:**

### 1. Install

```bash
apt-get update
apt-get install lm-sensors
sensors-detect  # Answer YES to safe questions
sensors -u      # Test
```

### 2. Fix Permissions

```bash
usermod -a -G adm,dialout,i2c homeassistant
systemctl restart home-assistant@homeassistant.service
su - homeassistant -s /bin/bash -c "sensors -u"  # Verify
```

### 3. Add Integration

Settings → Devices & Services → Add Integration → LM Sensors

---

## Troubleshooting

**No sensors after sensors-detect:**
- Stop container in Proxmox
- Options → Features → Enable "Privileged container"
- Start container, run `sensors-detect` again

**Sensors work as root but not as homeassistant:**
```bash
usermod -a -G adm,dialout,i2c homeassistant
systemctl restart home-assistant@homeassistant.service
```

**Kernel modules not loaded:**
On Proxmox host (not in LXC):
```bash
apt-get install lm-sensors
sensors-detect
service kmod start
```
Then restart LXC.
