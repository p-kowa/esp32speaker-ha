"""
Runtime data types for esp32speaker_integration.

Access pattern: entry.runtime_data.client / entry.runtime_data.coordinator
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import Esp32SpeakerApiClient
    from .coordinator import Esp32SpeakerDataUpdateCoordinator


type Esp32SpeakerConfigEntry = ConfigEntry[Esp32SpeakerData]


@dataclass
class Esp32SpeakerData:
    """Runtime data stored on the config entry after a successful setup."""

    client: Esp32SpeakerApiClient
    coordinator: Esp32SpeakerDataUpdateCoordinator
    integration: Integration
