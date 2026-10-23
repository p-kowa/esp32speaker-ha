"""Base entity linking the helper to its existing MQTT-owned device."""

from typing import TYPE_CHECKING

from custom_components.esp32speaker_integration.const import CONF_DEVICE_ID
from custom_components.esp32speaker_integration.coordinator import Esp32SpeakerDataUpdateCoordinator
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.helpers.update_coordinator import CoordinatorEntity

if TYPE_CHECKING:
    from homeassistant.helpers.entity import EntityDescription


class Esp32SpeakerEntity(CoordinatorEntity[Esp32SpeakerDataUpdateCoordinator]):
    """Provide stable identity without claiming ownership of the MQTT device."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: Esp32SpeakerDataUpdateCoordinator,
        entity_description: EntityDescription,
    ) -> None:
        """Initialize the helper and link its source device."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        entry = coordinator.config_entry
        self._attr_unique_id = f"{entry.data[CONF_DEVICE_ID]}_{entity_description.key}"
        source = er.async_get(coordinator.hass).async_get(coordinator.entities["power"])
        if source and source.device_id:
            self.device_entry = dr.async_get(coordinator.hass).async_get(source.device_id)
