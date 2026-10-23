"""Media player platform for existing ESP32 Speaker MQTT devices."""

from typing import TYPE_CHECKING

from .speaker import ENTITY_DESCRIPTIONS, Esp32SpeakerMediaPlayer

if TYPE_CHECKING:
    from custom_components.esp32speaker_integration.data import Esp32SpeakerConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: Esp32SpeakerConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Create one media player per configured speaker."""
    async_add_entities(
        Esp32SpeakerMediaPlayer(entry.runtime_data.coordinator, description)
        for description in ENTITY_DESCRIPTIONS
    )