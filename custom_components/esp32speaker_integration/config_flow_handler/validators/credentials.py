"""Credential validation for the config flow."""

from typing import TYPE_CHECKING

from custom_components.esp32speaker_integration.api import Esp32SpeakerApiClient
from homeassistant.helpers.aiohttp_client import async_get_clientsession

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant


async def validate_credentials(hass: HomeAssistant, username: str, password: str) -> None:
    """
    Test the credentials against the API.

    Args:
        hass: The Home Assistant instance.
        username: The username to validate.
        password: The password to validate.

    Raises:
        Esp32SpeakerApiClientAuthenticationError: If the credentials are rejected.
        Esp32SpeakerApiClientCommunicationError: If the API cannot be reached.
        Esp32SpeakerApiClientError: For any other API failure.

    """
    client = Esp32SpeakerApiClient(
        username=username,
        password=password,
        session=async_get_clientsession(hass),
    )
    await client.async_get_data()


__all__ = ["validate_credentials"]
