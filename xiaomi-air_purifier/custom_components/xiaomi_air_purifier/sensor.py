"""Sensor platform for Xiaomi Air Purifier."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    PERCENTAGE,
    REVOLUTIONS_PER_MINUTE,
    EntityCategory,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.typing import StateType

from . import XiaomiAirPurifierConfigEntry
from .device import AirPurifierStatus
from .entity import XiaomiAirPurifierEntity


@dataclass(frozen=True, kw_only=True)
class XiaomiAirPurifierSensorEntityDescription(SensorEntityDescription):
    """Describes an air purifier sensor."""

    value_fn: Callable[[AirPurifierStatus], StateType]


SENSORS: tuple[XiaomiAirPurifierSensorEntityDescription, ...] = (
    XiaomiAirPurifierSensorEntityDescription(
        key="temperature",
        translation_key="temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda s: s.temperature,
    ),
    XiaomiAirPurifierSensorEntityDescription(
        key="humidity",
        translation_key="humidity",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda s: s.humidity,
    ),
    XiaomiAirPurifierSensorEntityDescription(
        key="pm1",
        translation_key="pm1",
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:dots-hexagon",
        value_fn=lambda s: s.pm1,
    ),
    XiaomiAirPurifierSensorEntityDescription(
        key="pm25",
        translation_key="pm25",
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        device_class=SensorDeviceClass.PM25,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda s: s.pm25,
    ),
    XiaomiAirPurifierSensorEntityDescription(
        key="pm10",
        translation_key="pm10",
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        device_class=SensorDeviceClass.PM10,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda s: s.pm10,
    ),
    XiaomiAirPurifierSensorEntityDescription(
        key="motor_speed",
        translation_key="motor_speed",
        native_unit_of_measurement=REVOLUTIONS_PER_MINUTE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:fan",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda s: s.motor_speed,
    ),
    XiaomiAirPurifierSensorEntityDescription(
        key="filter_life",
        translation_key="filter_life",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:air-filter",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda s: s.filter_life,
    ),
    XiaomiAirPurifierSensorEntityDescription(
        key="filter_left_time",
        translation_key="filter_left_time",
        native_unit_of_measurement=UnitOfTime.HOURS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:clock-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda s: s.filter_left_time,
    ),
    XiaomiAirPurifierSensorEntityDescription(
        key="air_quality",
        translation_key="air_quality",
        icon="mdi:air-filter",
        value_fn=lambda s: s.air_quality_label,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: XiaomiAirPurifierConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up air purifier sensor entities."""
    coordinator = entry.runtime_data
    async_add_entities(
        XiaomiAirPurifierSensor(coordinator, description) for description in SENSORS
    )


class XiaomiAirPurifierSensor(XiaomiAirPurifierEntity, SensorEntity):
    """Sensor entity for an air purifier measurement."""

    entity_description: XiaomiAirPurifierSensorEntityDescription

    def __init__(
        self,
        coordinator,
        description: XiaomiAirPurifierSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{self._unique_base}_{description.key}"

    @property
    def native_value(self) -> StateType:
        """Return the sensor value."""
        if self.coordinator.data is None:
            return None
        return self.entity_description.value_fn(self.coordinator.data)
