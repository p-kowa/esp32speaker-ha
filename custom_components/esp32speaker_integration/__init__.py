"""Add a media player to an existing ESP32 Speaker MQTT device."""

from typing import TYPE_CHECKING

from homeassistant.const import Platform
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN
from .coordinator import Esp32SpeakerDataUpdateCoordinator
from .data import Esp32SpeakerData

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import Esp32SpeakerConfigEntry

PLATFORMS: list[Platform] = [
    Platform.MEDIA_PLAYER,
]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: Esp32SpeakerConfigEntry,
) -> bool:
    """Start the state listener and load the media player."""
    coordinator = Esp32SpeakerDataUpdateCoordinator(hass, entry)
    entry.runtime_data = Esp32SpeakerData(coordinator=coordinator)
    coordinator.async_start()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: Esp32SpeakerConfigEntry,
) -> bool:
    """
    Unload a config entry.

    Returns:
        True if every platform unloaded cleanly.

    """
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant,
    entry: Esp32SpeakerConfigEntry,
) -> None:
    """Reload the config entry after its data or options changed."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_migrate_entry(hass: HomeAssistant, entry: Esp32SpeakerConfigEntry) -> bool:
    """Refuse demo entries, which have no real speaker configuration."""
    return entry.version == 2
