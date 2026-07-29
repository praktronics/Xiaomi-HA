"""Data update coordinator for Xiaomi Air Purifier."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from miio import DeviceException

from .const import DOMAIN, SCAN_INTERVAL
from .device import AirPurifierStatus, XiaomiAirPurifier

_LOGGER = logging.getLogger(__name__)


class XiaomiAirPurifierCoordinator(DataUpdateCoordinator[AirPurifierStatus]):
    """Poll the air purifier and cache the latest status."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        device: XiaomiAirPurifier,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            config_entry=entry,
            update_interval=SCAN_INTERVAL,
        )
        self.device = device
        self.entry = entry

    async def _async_update_data(self) -> AirPurifierStatus:
        """Fetch status from the device."""
        try:
            return await self.hass.async_add_executor_job(self.device.status)
        except DeviceException as err:
            raise UpdateFailed(f"Error communicating with device: {err}") from err
