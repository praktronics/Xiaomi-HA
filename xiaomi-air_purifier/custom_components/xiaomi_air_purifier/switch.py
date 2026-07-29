"""Switch platform for Xiaomi Air Purifier."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import logging
from typing import Any

from miio import DeviceException

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import XiaomiAirPurifierConfigEntry
from .device import AirPurifierStatus, XiaomiAirPurifier
from .entity import XiaomiAirPurifierEntity

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class XiaomiAirPurifierSwitchEntityDescription(SwitchEntityDescription):
    """Describes a switch backed by a boolean MIoT property."""

    is_on_fn: Callable[[AirPurifierStatus], bool | None]
    set_fn: Callable[[XiaomiAirPurifier, bool], None]


SWITCHES: tuple[XiaomiAirPurifierSwitchEntityDescription, ...] = (
    XiaomiAirPurifierSwitchEntityDescription(
        key="screen",
        translation_key="screen",
        is_on_fn=lambda s: s.screen_on,
        set_fn=lambda d, v: d.set_screen(v),
    ),
    XiaomiAirPurifierSwitchEntityDescription(
        key="anion",
        translation_key="anion",
        is_on_fn=lambda s: s.anion,
        set_fn=lambda d, v: d.set_anion(v),
    ),
    XiaomiAirPurifierSwitchEntityDescription(
        key="uv",
        translation_key="uv",
        is_on_fn=lambda s: s.uv,
        set_fn=lambda d, v: d.set_uv(v),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: XiaomiAirPurifierConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up air purifier switch entities."""
    coordinator = entry.runtime_data
    async_add_entities(
        XiaomiAirPurifierSwitch(coordinator, description) for description in SWITCHES
    )


class XiaomiAirPurifierSwitch(XiaomiAirPurifierEntity, SwitchEntity):
    """Switch entity for a boolean air purifier feature."""

    entity_description: XiaomiAirPurifierSwitchEntityDescription

    def __init__(
        self,
        coordinator,
        description: XiaomiAirPurifierSwitchEntityDescription,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{self._unique_base}_{description.key}"

    @property
    def is_on(self) -> bool | None:
        """Return true if the switch is on."""
        if self.coordinator.data is None:
            return None
        return self.entity_description.is_on_fn(self.coordinator.data)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        await self._async_set(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        await self._async_set(False)

    async def _async_set(self, value: bool) -> None:
        """Write the switch state to the device."""
        try:
            await self.hass.async_add_executor_job(
                self.entity_description.set_fn, self._device, value
            )
        except DeviceException as err:
            raise HomeAssistantError(
                f"Failed to set {self.entity_description.key}: {err}"
            ) from err
        await self.coordinator.async_request_refresh()
