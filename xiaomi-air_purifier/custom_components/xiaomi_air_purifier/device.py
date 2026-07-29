"""Device client for Xiaomi Air Purifier (xiaomi.airp.mb5)."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any

from miio import DeviceException, DeviceInfo, MiotDevice

from .const import (
    AIR_QUALITY_LABELS,
    DEVICE_TO_FAN_LEVEL,
    FAN_LEVEL_TO_DEVICE,
    MIOT_MAPPING,
    MODE_TO_PRESET,
    MODEL,
    PRESET_TO_MODE,
)

_LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class AirPurifierStatus:
    """Parsed status snapshot from the air purifier."""

    power: bool | None = None
    fault: int | None = None
    mode: int | None = None
    fan_level: int | None = None  # Human-facing 1/2/3
    anion: bool | None = None
    uv: bool | None = None
    humidity: int | None = None
    air_quality: int | None = None
    pm25: int | None = None
    pm10: int | None = None
    temperature: float | None = None
    pm1: int | None = None
    filter_life: int | None = None
    filter_left_time: int | None = None
    filter_used_time: int | None = None
    screen_on: bool | None = None
    screen_brightness: int | None = None
    motor_speed: int | None = None

    @property
    def is_on(self) -> bool:
        """Return True when the purifier is powered on."""
        return bool(self.power)

    @property
    def preset_mode(self) -> str | None:
        """Return the HA preset mode name for the current device mode."""
        if self.mode is None:
            return None
        return MODE_TO_PRESET.get(self.mode)

    @property
    def air_quality_label(self) -> str | None:
        """Return a human-readable air quality label."""
        if self.air_quality is None:
            return None
        return AIR_QUALITY_LABELS.get(self.air_quality, str(self.air_quality))


class XiaomiAirPurifier:
    """Thin wrapper around python-miio for xiaomi.airp.mb5."""

    def __init__(self, host: str, token: str) -> None:
        """Initialize the device client."""
        self._host = host
        self._token = token
        self._device = MiotDevice(
            ip=host,
            token=token,
            model=MODEL,
            mapping=dict(MIOT_MAPPING),
        )
        self._device_info: DeviceInfo | None = None

    @property
    def host(self) -> str:
        """Return the configured host/IP."""
        return self._host

    def connect(self) -> DeviceInfo:
        """Handshake with the device and return device info.

        Raises:
            DeviceException: If the device cannot be reached or the token is wrong.
        """
        info = self._device.info()
        self._device_info = info
        _LOGGER.debug(
            "Connected to %s model=%s fw=%s",
            self._host,
            info.model,
            info.firmware_version,
        )
        return info

    def get_device_info(self) -> DeviceInfo:
        """Return cached device info, fetching it if needed."""
        if self._device_info is None:
            return self.connect()
        return self._device_info

    def status(self) -> AirPurifierStatus:
        """Fetch and parse the current device status."""
        raw_list = self._device.get_properties_for_mapping()
        raw: dict[str, Any] = {
            prop["did"]: prop.get("value")
            for prop in raw_list
            if prop.get("code", -1) == 0
        }

        device_fan = raw.get("fan_level")
        fan_level = (
            DEVICE_TO_FAN_LEVEL.get(device_fan) if isinstance(device_fan, int) else None
        )

        return AirPurifierStatus(
            power=raw.get("power"),
            fault=raw.get("fault"),
            mode=raw.get("mode"),
            fan_level=fan_level,
            anion=raw.get("anion"),
            uv=raw.get("uv"),
            humidity=raw.get("humidity"),
            air_quality=raw.get("air_quality"),
            pm25=raw.get("pm25"),
            pm10=raw.get("pm10"),
            temperature=raw.get("temperature"),
            pm1=raw.get("pm1"),
            filter_life=raw.get("filter_life"),
            filter_left_time=raw.get("filter_left_time"),
            filter_used_time=raw.get("filter_used_time"),
            screen_on=raw.get("screen_on"),
            screen_brightness=raw.get("screen_brightness"),
            motor_speed=raw.get("motor_speed"),
        )

    def set_power(self, on: bool) -> None:
        """Turn the purifier on or off."""
        self._set_property("power", on)

    def set_fan_level(self, level: int) -> None:
        """Set fan level (1, 2, or 3)."""
        if level not in FAN_LEVEL_TO_DEVICE:
            raise ValueError(
                f"Invalid fan level {level}; expected one of {list(FAN_LEVEL_TO_DEVICE)}"
            )
        self._set_property("fan_level", FAN_LEVEL_TO_DEVICE[level])

    def set_preset_mode(self, preset: str) -> None:
        """Set operation mode from a preset name."""
        if preset not in PRESET_TO_MODE:
            raise ValueError(f"Unknown preset mode: {preset}")
        self._set_property("mode", PRESET_TO_MODE[preset])

    def set_anion(self, on: bool) -> None:
        """Enable or disable anion (ionizer)."""
        self._set_property("anion", on)

    def set_uv(self, on: bool) -> None:
        """Enable or disable UV."""
        self._set_property("uv", on)

    def set_screen(self, on: bool) -> None:
        """Turn the display screen on or off."""
        self._set_property("screen_on", on)

    def _set_property(self, name: str, value: Any) -> None:
        """Write a single mapped MIoT property."""
        if name not in MIOT_MAPPING:
            raise DeviceException(f"Unknown property: {name}")
        result = self._device.set_property(name, value)
        _LOGGER.debug("set_property %s=%s -> %s", name, value, result)
