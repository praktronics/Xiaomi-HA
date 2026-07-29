"""Constants for the Xiaomi Air Purifier integration."""

from __future__ import annotations

from datetime import timedelta
from typing import Final

DOMAIN: Final = "xiaomi_air_purifier"
MANUFACTURER: Final = "Xiaomi"
MODEL: Final = "xiaomi.airp.mb5"
DEFAULT_NAME: Final = "Xiaomi Air Purifier"

# Polling interval for status updates
SCAN_INTERVAL: Final = timedelta(seconds=30)

# Fan level choices on the device (siid=2, piid=5)
# Level1 (0), Level2 (1), Level3 (2)
FAN_LEVELS: Final = (1, 2, 3)
FAN_LEVEL_TO_DEVICE: Final = {1: 0, 2: 1, 3: 2}
DEVICE_TO_FAN_LEVEL: Final = {0: 1, 1: 2, 2: 3}

# Mode choices (siid=2, piid=4)
# Auto (0), Sleep (3), Favorite (5), None (6)
MODE_AUTO: Final = 0
MODE_SLEEP: Final = 3
MODE_FAVORITE: Final = 5
MODE_NONE: Final = 6

PRESET_MODE_AUTO: Final = "Auto"
PRESET_MODE_SLEEP: Final = "Sleep"
PRESET_MODE_FAVORITE: Final = "Favorite"
PRESET_MODE_MANUAL: Final = "Manual"

PRESET_MODES: Final = (
    PRESET_MODE_AUTO,
    PRESET_MODE_SLEEP,
    PRESET_MODE_FAVORITE,
    PRESET_MODE_MANUAL,
)

PRESET_TO_MODE: Final = {
    PRESET_MODE_AUTO: MODE_AUTO,
    PRESET_MODE_SLEEP: MODE_SLEEP,
    PRESET_MODE_FAVORITE: MODE_FAVORITE,
    PRESET_MODE_MANUAL: MODE_NONE,
}

MODE_TO_PRESET: Final = {
    MODE_AUTO: PRESET_MODE_AUTO,
    MODE_SLEEP: PRESET_MODE_SLEEP,
    MODE_FAVORITE: PRESET_MODE_FAVORITE,
    MODE_NONE: PRESET_MODE_MANUAL,
}

# MIoT property mapping for xiaomi.airp.mb5
# Source: schema/xiaomi.airp.mb5.json
MIOT_MAPPING: Final = {
    # Air purifier (siid=2)
    "power": {"siid": 2, "piid": 1},
    "fault": {"siid": 2, "piid": 2},
    "mode": {"siid": 2, "piid": 4},
    "fan_level": {"siid": 2, "piid": 5},
    "anion": {"siid": 2, "piid": 6},
    "uv": {"siid": 2, "piid": 7},
    # Environment (siid=3)
    "humidity": {"siid": 3, "piid": 1},
    "air_quality": {"siid": 3, "piid": 3},
    "pm25": {"siid": 3, "piid": 4},
    "pm10": {"siid": 3, "piid": 5},
    "temperature": {"siid": 3, "piid": 7},
    "pm1": {"siid": 3, "piid": 9},
    # Filter (siid=4)
    "filter_life": {"siid": 4, "piid": 1},
    "filter_left_time": {"siid": 4, "piid": 2},
    "filter_used_time": {"siid": 4, "piid": 3},
    # Screen (siid=7)
    "screen_on": {"siid": 7, "piid": 1},
    "screen_brightness": {"siid": 7, "piid": 2},
    # Custom service (siid=13)
    "motor_speed": {"siid": 13, "piid": 3},
}

AIR_QUALITY_LABELS: Final = {
    0: "Excellent",
    1: "Good",
    2: "Moderate",
    3: "Poor",
    4: "Heavy Pollution",
    5: "Hazardous",
}
