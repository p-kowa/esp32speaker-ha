"""Number platform for esp32speaker_integration."""

from typing import TYPE_CHECKING

from .target_humidity import ENTITY_DESCRIPTIONS, Esp32SpeakerHumidityNumber

# Acts on the device: the coordinator does not limit outbound calls.
PARALLEL_UPDATES = 1

if TYPE_CHECKING:
    from custom_components.esp32speaker_integration.data import Esp32SpeakerConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback


async def async_setup_entry(
    hass: HomeAssistant,
    entry: Esp32SpeakerConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the number platform."""
    async_add_entities(
        Esp32SpeakerHumidityNumber(entry.runtime_data.coordinator, description)
        for description in ENTITY_DESCRIPTIONS
    )
