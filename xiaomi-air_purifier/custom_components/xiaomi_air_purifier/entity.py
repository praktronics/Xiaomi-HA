"""Base entity for Xiaomi Air Purifier."""

from __future__ import annotations

from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL
from .coordinator import XiaomiAirPurifierCoordinator


class XiaomiAirPurifierEntity(CoordinatorEntity[XiaomiAirPurifierCoordinator]):
    """Base class for air purifier entities."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: XiaomiAirPurifierCoordinator) -> None:
        """Initialize the entity with shared device info."""
        super().__init__(coordinator)
        self._device = coordinator.device
        entry = coordinator.entry
        unique_base = entry.unique_id or entry.entry_id

        try:
            info = self._device.get_device_info()
            model = info.model or MODEL
            fw = info.firmware_version
            hw = info.hardware_version
            mac = info.mac_address
        except Exception:  # noqa: BLE001 - fall back if info unavailable
            model = MODEL
            fw = None
            hw = None
            mac = None

        device_info = DeviceInfo(
            identifiers={(DOMAIN, unique_base)},
            name=entry.title,
            manufacturer=MANUFACTURER,
            model=model,
            sw_version=fw,
            hw_version=hw,
        )
        if mac:
            device_info["connections"] = {(CONNECTION_NETWORK_MAC, mac)}

        self._attr_device_info = device_info
        self._unique_base = unique_base
