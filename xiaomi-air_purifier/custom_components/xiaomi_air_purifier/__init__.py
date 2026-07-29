"""The Xiaomi Air Purifier integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_TOKEN, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from miio import DeviceException

from .coordinator import XiaomiAirPurifierCoordinator
from .device import XiaomiAirPurifier

PLATFORMS: list[Platform] = [
    Platform.FAN,
    Platform.SENSOR,
    Platform.SWITCH,
]

type XiaomiAirPurifierConfigEntry = ConfigEntry[XiaomiAirPurifierCoordinator]


async def async_setup_entry(
    hass: HomeAssistant, entry: XiaomiAirPurifierConfigEntry
) -> bool:
    """Set up Xiaomi Air Purifier from a config entry."""
    host: str = entry.data[CONF_HOST]
    token: str = entry.data[CONF_TOKEN]

    device = XiaomiAirPurifier(host, token)

    try:
        await hass.async_add_executor_job(device.connect)
    except DeviceException as err:
        raise ConfigEntryNotReady(f"Unable to connect to {host}: {err}") from err

    coordinator = XiaomiAirPurifierCoordinator(hass, entry, device)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: XiaomiAirPurifierConfigEntry
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
