"""Data update coordinator for esp32speaker_integration."""

from typing import TYPE_CHECKING, Any

from custom_components.esp32speaker_integration.api import (
    Esp32SpeakerApiClientAuthenticationError,
    Esp32SpeakerApiClientError,
)
from custom_components.esp32speaker_integration.const import DOMAIN
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

if TYPE_CHECKING:
    from custom_components.esp32speaker_integration.data import Esp32SpeakerConfigEntry


class Esp32SpeakerDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetch the device state once per interval and hand it to every entity."""

    config_entry: Esp32SpeakerConfigEntry

    async def _async_update_data(self) -> dict[str, Any]:
        """
        Fetch the current device state.

        Returns:
            The payload entities read by key.

        Raises:
            ConfigEntryAuthFailed: If the credentials were rejected; triggers reauth.
            UpdateFailed: If the fetch failed for any other reason.

        """
        try:
            return await self.config_entry.runtime_data.client.async_get_data()
        except Esp32SpeakerApiClientAuthenticationError as exception:
            raise ConfigEntryAuthFailed(
                translation_domain=DOMAIN,
                translation_key="authentication_failed",
            ) from exception
        except Esp32SpeakerApiClientError as exception:
            raise UpdateFailed(
                translation_domain=DOMAIN,
                translation_key="update_failed",
            ) from exception
