"""Support for LM Sensors."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

DEVICE_CLASS_MAP = {
    "temperature": SensorDeviceClass.TEMPERATURE,
    "voltage": SensorDeviceClass.VOLTAGE,
    "power": SensorDeviceClass.POWER,
    "current": SensorDeviceClass.CURRENT,
    "energy": SensorDeviceClass.ENERGY,
}

ICON_MAP = {
    "temperature": "mdi:thermometer",
    "fan": "mdi:fan",
    "voltage": "mdi:flash",
    "power": "mdi:lightning-bolt",
    "current": "mdi:current-ac",
    "energy": "mdi:lightning-bolt-circle",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up LM Sensors from a config entry."""
    coordinator: DataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    # Get the reader from coordinator
    reader = coordinator.update_method.__self__

    # Get all available sensors
    sensors = reader.get_sensors_list()

    entities = [
        LMSensorEntity(
            coordinator,
            sensor["chip"],
            sensor["feature"],
            sensor["reading"],
            sensor["name"],
            sensor["unit"],
            sensor["device_class"],
            sensor["type"],
        )
        for sensor in sensors
    ]

    async_add_entities(entities)


class LMSensorEntity(CoordinatorEntity, SensorEntity):
    """Representation of an LM Sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        chip: str,
        feature: str,
        reading: str,
        name: str,
        unit: str | None,
        device_class: str | None,
        sensor_type: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        
        self._chip = chip
        self._feature = feature
        self._reading = reading
        self._attr_name = feature.replace("_", " ").title()
        self._attr_native_unit_of_measurement = unit
        self._sensor_type = sensor_type
        self._attr_device_class = DEVICE_CLASS_MAP.get(device_class)
        
        if sensor_type in ["temperature", "voltage", "power", "current", "energy", "fan"]:
            self._attr_state_class = SensorStateClass.MEASUREMENT
        
        self._attr_icon = ICON_MAP.get(sensor_type, "mdi:chip")

        # Unique ID
        self._attr_unique_id = f"lm_sensors_{chip}_{feature}_{reading}".replace(" ", "_").replace("-", "_").lower()

        # Device info
        self._attr_device_info = {
            "identifiers": {(DOMAIN, chip)},
            "name": chip,
            "manufacturer": "LM Sensors",
            "model": chip.split("-")[0] if "-" in chip else chip,
        }

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None

        try:
            value = (
                self.coordinator.data
                .get(self._chip, {})
                .get(self._feature, {})
                .get(self._reading)
            )
            return value
        except (KeyError, TypeError):
            return None

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()
