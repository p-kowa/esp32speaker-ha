"""State-driven coordinator for an existing MQTT speaker."""

from typing import TYPE_CHECKING, Any

from custom_components.esp32speaker_integration.const import CONF_ENTITIES, CONF_TOPIC_PREFIX, LOGGER
from homeassistant.components import mqtt
from homeassistant.core import State, callback
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

if TYPE_CHECKING:
    from custom_components.esp32speaker_integration.data import Esp32SpeakerConfigEntry
    from homeassistant.core import Event, EventStateChangedData, HomeAssistant


class Esp32SpeakerDataUpdateCoordinator(DataUpdateCoordinator[dict[str, State | None]]):
    """Mirror selected entities without polling the speaker."""

    config_entry: Esp32SpeakerConfigEntry

    def __init__(self, hass: HomeAssistant, entry: Esp32SpeakerConfigEntry) -> None:
        """Initialize the state listener."""
        super().__init__(hass, LOGGER, config_entry=entry, name=entry.title)
        self.entities: dict[str, str] = entry.data[CONF_ENTITIES]
        self.topic: str = entry.data[CONF_TOPIC_PREFIX]

    @callback
    def async_start(self) -> None:
        """Subscribe before reading the initial state."""
        self.config_entry.async_on_unload(
            async_track_state_change_event(self.hass, list(self.entities.values()), self._async_changed)
        )
        self._async_read_states()

    @callback
    def _async_changed(self, event: Event[EventStateChangedData]) -> None:
        """Update the media player when a backing entity changes."""
        self._async_read_states()

    @callback
    def _async_read_states(self) -> None:
        """Publish a consistent snapshot of the backing entities."""
        self.async_set_updated_data(
            {key: self.hass.states.get(entity_id) for key, entity_id in self.entities.items()}
        )

    async def async_command(self, key: str, service: str, **data: Any) -> None:
        """Control a backing entity through its own integration."""
        entity_id = self.entities[key]
        await self.hass.services.async_call(
            entity_id.split(".", 1)[0], service, {"entity_id": entity_id, **data}, blocking=True
        )

    async def async_publish(self, command: str, payload: str) -> None:
        """Send non-retained playback commands using Home Assistant's MQTT client."""
        await mqtt.async_publish(self.hass, f"{self.topic}/set/{command}", payload, qos=0, retain=False)
