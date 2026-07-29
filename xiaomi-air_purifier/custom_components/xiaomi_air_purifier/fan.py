"""Fan platform for Xiaomi Air Purifier."""

from __future__ import annotations

import logging
from typing import Any

from miio import DeviceException

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.util.percentage import (
    ordered_list_item_to_percentage,
    percentage_to_ordered_list_item,
)

from . import XiaomiAirPurifierConfigEntry
from .const import FAN_LEVELS, PRESET_MODES
from .entity import XiaomiAirPurifierEntity

_LOGGER = logging.getLogger(__name__)

# Named speeds corresponding to device fan levels 1/2/3
ORDERED_NAMED_FAN_SPEEDS = [str(level) for level in FAN_LEVELS]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: XiaomiAirPurifierConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the air purifier fan entity."""
    coordinator = entry.runtime_data
    async_add_entities([XiaomiAirPurifierFan(coordinator)])


class XiaomiAirPurifierFan(XiaomiAirPurifierEntity, FanEntity):
    """Representation of the air purifier as a fan."""

    _attr_name = None
    _attr_translation_key = "air_purifier"
    _attr_supported_features = (
        FanEntityFeature.SET_SPEED
        | FanEntityFeature.PRESET_MODE
        | FanEntityFeature.TURN_ON
        | FanEntityFeature.TURN_OFF
    )
    _attr_preset_modes = list(PRESET_MODES)
    _attr_speed_count = len(ORDERED_NAMED_FAN_SPEEDS)

    def __init__(self, coordinator) -> None:
        """Initialize the fan entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._unique_base}_fan"

    @property
    def is_on(self) -> bool | None:
        """Return true if the purifier is on."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.is_on

    @property
    def percentage(self) -> int | None:
        """Return the current fan level as a percentage."""
        status = self.coordinator.data
        if status is None or not status.is_on or status.fan_level is None:
            return 0 if status and not status.is_on else None
        return ordered_list_item_to_percentage(
            ORDERED_NAMED_FAN_SPEEDS, str(status.fan_level)
        )

    @property
    def preset_mode(self) -> str | None:
        """Return the current preset mode."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.preset_mode

    async def async_turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Turn the purifier on, optionally setting speed or preset."""
        try:
            await self.hass.async_add_executor_job(self._device.set_power, True)
            if preset_mode is not None:
                await self.hass.async_add_executor_job(
                    self._device.set_preset_mode, preset_mode
                )
            elif percentage is not None:
                await self._async_set_percentage(percentage)
        except (DeviceException, ValueError) as err:
            raise HomeAssistantError(f"Failed to turn on air purifier: {err}") from err
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the purifier off."""
        try:
            await self.hass.async_add_executor_job(self._device.set_power, False)
        except DeviceException as err:
            raise HomeAssistantError(f"Failed to turn off air purifier: {err}") from err
        await self.coordinator.async_request_refresh()

    async def async_set_percentage(self, percentage: int) -> None:
        """Set fan speed percentage (maps to levels 1–3)."""
        if percentage == 0:
            await self.async_turn_off()
            return
        try:
            await self._async_set_percentage(percentage)
        except (DeviceException, ValueError) as err:
            raise HomeAssistantError(f"Failed to set fan level: {err}") from err
        await self.coordinator.async_request_refresh()

    async def _async_set_percentage(self, percentage: int) -> None:
        """Map percentage to a named fan level and send to the device."""
        level_str = percentage_to_ordered_list_item(
            ORDERED_NAMED_FAN_SPEEDS, percentage
        )
        await self.hass.async_add_executor_job(
            self._device.set_fan_level, int(level_str)
        )

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the operation mode preset."""
        try:
            await self.hass.async_add_executor_job(
                self._device.set_preset_mode, preset_mode
            )
        except (DeviceException, ValueError) as err:
            raise HomeAssistantError(f"Failed to set preset mode: {err}") from err
        await self.coordinator.async_request_refresh()
