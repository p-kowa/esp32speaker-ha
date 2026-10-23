"""Runtime data for the MQTT-backed media player."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from .coordinator import Esp32SpeakerDataUpdateCoordinator


type Esp32SpeakerConfigEntry = ConfigEntry[Esp32SpeakerData]


@dataclass
class Esp32SpeakerData:
    """Runtime data stored on the config entry after a successful setup."""

    coordinator: Esp32SpeakerDataUpdateCoordinator
