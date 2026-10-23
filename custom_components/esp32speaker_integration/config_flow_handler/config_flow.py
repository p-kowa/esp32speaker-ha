"""Configure a media player for an already discovered MQTT speaker."""

from typing import Any

from custom_components.esp32speaker_integration.const import CONF_DEVICE_ID, DOMAIN
from homeassistant import config_entries

from .schemas import get_user_schema
from .validators import validate_speaker


class Esp32SpeakerConfigFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Select an existing speaker, without creating a second physical device."""

    VERSION = 2

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Validate the hardware ID and the selected MQTT device."""
        errors: dict[str, str] = {}
        if user_input is not None:
            data, errors = validate_speaker(self.hass, user_input)
            if not errors:
                await self.async_set_unique_id(data[CONF_DEVICE_ID])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=data.pop("title"), data=data)
        return self.async_show_form(
            step_id="user", data_schema=get_user_schema(user_input), errors=errors
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Refresh entity mappings or change the MQTT prefix for the same speaker."""
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}
        if user_input is not None:
            data, errors = validate_speaker(self.hass, user_input)
            if not errors:
                await self.async_set_unique_id(data[CONF_DEVICE_ID])
                self._abort_if_unique_id_mismatch()
                return self.async_update_reload_and_abort(
                    entry, title=data.pop("title"), data_updates=data
                )
        return self.async_show_form(
            step_id="reconfigure",
            data_schema=get_user_schema(user_input or dict(entry.data)),
            errors=errors,
        )


__all__ = ["Esp32SpeakerConfigFlowHandler"]
