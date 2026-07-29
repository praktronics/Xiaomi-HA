"""Config flow for Xiaomi Air Purifier."""

from __future__ import annotations

import logging
from typing import Any

from miio import DeviceException
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_TOKEN
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .const import DEFAULT_NAME, DOMAIN, MODEL
from .device import XiaomiAirPurifier

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_TOKEN): vol.All(str, vol.Length(min=32, max=32)),
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate host/token and return info used to create the config entry."""
    host = data[CONF_HOST].strip()
    token = data[CONF_TOKEN].strip().lower()

    if any(c not in "0123456789abcdef" for c in token):
        raise InvalidToken("Token must be 32 hexadecimal characters")

    device = XiaomiAirPurifier(host, token)

    try:
        info = await hass.async_add_executor_job(device.connect)
    except DeviceException as err:
        _LOGGER.debug("Connection failed to %s: %s", host, err)
        raise CannotConnect from err

    # Prefer MAC as unique id so multiple purifiers can coexist
    unique_id = (info.mac_address or str(info.raw.get("uid", host))).replace(":", "").lower()
    title = f"{DEFAULT_NAME} ({host})"
    if info.model:
        title = f"{info.model} ({host})"

    return {
        "title": title,
        "unique_id": unique_id,
        "model": info.model or MODEL,
        CONF_HOST: host,
        CONF_TOKEN: token,
    }


class XiaomiAirPurifierConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Xiaomi Air Purifier."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step: request IP and token."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidToken:
                errors["base"] = "invalid_token"
            except Exception:
                _LOGGER.exception("Unexpected exception during config flow")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(info["unique_id"])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=info["title"],
                    data={
                        CONF_HOST: info[CONF_HOST],
                        CONF_TOKEN: info[CONF_TOKEN],
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidToken(HomeAssistantError):
    """Error to indicate the token format is invalid."""
