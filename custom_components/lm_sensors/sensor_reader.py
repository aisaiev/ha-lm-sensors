"""LM Sensors data reader."""
from __future__ import annotations

import asyncio
import logging
import os
from typing import Any

from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

SENSORS_PATHS = ["/usr/bin/sensors", "/usr/local/bin/sensors", "/bin/sensors", "sensors"]


class LMSensorsReader:
    """Class to read sensor data from lm-sensors."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the reader."""
        self.hass = hass
        self._sensors_data: dict[str, Any] = {}
        self._sensors_cmd: str | None = None

    async def _find_sensors_command(self) -> str | None:
        """Find the sensors command path."""
        if self._sensors_cmd:
            return self._sensors_cmd
        
        for cmd_path in SENSORS_PATHS:
            try:
                if cmd_path.startswith("/") and not os.path.exists(cmd_path):
                    continue

                process = await asyncio.create_subprocess_exec(
                    cmd_path, "-v",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, _ = await process.communicate()
                
                if process.returncode == 0:
                    self._sensors_cmd = cmd_path
                    _LOGGER.info("Found sensors at %s", cmd_path)
                    return cmd_path
                    
            except (FileNotFoundError, PermissionError):
                continue
            except Exception as err:
                _LOGGER.debug("Error testing %s: %s", cmd_path, err)

        return None

    async def is_available(self) -> bool:
        """Check if lm-sensors is available."""
        cmd = await self._find_sensors_command()
        if not cmd:
            _LOGGER.error(
                "sensors command not found. Install: apt-get install lm-sensors or "
                "docker exec homeassistant apk add lm-sensors. See PROXMOX.md"
            )
            return False
        
        try:
            process = await asyncio.create_subprocess_exec(
                cmd, "-u",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                _LOGGER.error("Cannot read sensors: %s", stderr.decode())
                return False
            
            if not stdout.decode().strip():
                _LOGGER.error("No sensors detected. Run sensors-detect")
                return False
            
            return True
            
        except Exception as err:
            _LOGGER.error("Error testing sensors: %s", err)
            return False

    async def async_update(self) -> dict[str, Any]:
        """Update sensor data."""
        cmd = await self._find_sensors_command()
        if not cmd:
            _LOGGER.error("Sensors command not available")
            return self._sensors_data

        try:
            process = await asyncio.create_subprocess_exec(
                cmd, "-u",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                _LOGGER.error("Error running sensors command: %s", stderr.decode())
                return self._sensors_data

            output = stdout.decode()
            self._sensors_data = self._parse_sensors_output(output)
            
            return self._sensors_data

        except Exception as err:
            _LOGGER.error("Error updating sensor data: %s", err)
            return self._sensors_data

    def _parse_sensors_output(self, output: str) -> dict[str, Any]:
        """Parse the output from the sensors command."""
        sensors = {}
        current_chip = None
        current_feature = None

        for line in output.split("\n"):
            if not line.strip():
                continue

            # Sensor readings (2 spaces indent)
            if line.startswith("  ") and current_chip and current_feature:
                parts = line.strip().split(":", 1)
                if len(parts) == 2:
                    try:
                        sensors[current_chip][current_feature][parts[0].strip()] = float(parts[1].strip())
                    except ValueError:
                        pass
                continue

            stripped = line.strip()
            
            # Skip adapter lines
            if stripped.startswith("Adapter:"):
                continue
            
            # Feature name (ends with colon)
            if stripped.endswith(":"):
                current_feature = stripped[:-1]
                if current_chip:
                    sensors[current_chip][current_feature] = {}
            # Chip identifier (no colon, not indented)
            elif not line.startswith(" ") and ":" not in stripped:
                current_chip = stripped
                sensors[current_chip] = {}
                current_feature = None

        return sensors

    def get_sensors_list(self) -> list[dict[str, Any]]:
        """Get a list of all available sensors."""
        sensor_list = []

        for chip, features in self._sensors_data.items():
            for feature, readings in features.items():
                for reading_name, value in readings.items():
                    # Determine sensor type and unit
                    sensor_type, unit, device_class = self._classify_sensor(reading_name)
                    
                    if sensor_type and "_input" in reading_name:
                        sensor_list.append({
                            "chip": chip,
                            "feature": feature,
                            "reading": reading_name,
                            "type": sensor_type,
                            "unit": unit,
                            "device_class": device_class,
                            "value": value,
                            "name": f"{chip} {feature}",
                        })

        return sensor_list

    def _classify_sensor(self, reading_name: str) -> tuple[str | None, str | None, str | None]:
        """Classify sensor type based on reading name."""
        reading_lower = reading_name.lower()

        if "temp" in reading_lower:
            return ("temperature", "°C", "temperature")
        elif "fan" in reading_lower:
            return ("fan", "RPM", None)
        elif "in" in reading_lower or "volt" in reading_lower:
            return ("voltage", "V", "voltage")
        elif "power" in reading_lower:
            return ("power", "W", "power")
        elif "curr" in reading_lower:
            return ("current", "A", "current")
        elif "energy" in reading_lower:
            return ("energy", "J", "energy")

        return (None, None, None)

    def get_sensor_value(self, chip: str, feature: str, reading: str) -> float | None:
        """Get a specific sensor value."""
        try:
            return self._sensors_data.get(chip, {}).get(feature, {}).get(reading)
        except (KeyError, TypeError):
            return None
