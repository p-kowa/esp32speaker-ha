"""
API package for esp32speaker_integration.

Exception hierarchy:
    Esp32SpeakerApiClientError (base)
    ├── Esp32SpeakerApiClientCommunicationError (network/timeout)
    └── Esp32SpeakerApiClientAuthenticationError (401/403)

The coordinator maps them onto ConfigEntryAuthFailed and UpdateFailed; nothing else
in the integration imports this package.
"""

from .client import (
    FAN_SPEEDS,
    Esp32SpeakerApiClient,
    Esp32SpeakerApiClientAuthenticationError,
    Esp32SpeakerApiClientCommunicationError,
    Esp32SpeakerApiClientError,
)

__all__ = [
    "FAN_SPEEDS",
    "Esp32SpeakerApiClient",
    "Esp32SpeakerApiClientAuthenticationError",
    "Esp32SpeakerApiClientCommunicationError",
    "Esp32SpeakerApiClientError",
]
