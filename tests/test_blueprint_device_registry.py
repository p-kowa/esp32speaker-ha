"""Verify the helper links to, but never owns, the MQTT device."""

from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er

from .conftest import SOURCE_ENTITIES


async def test_mqtt_keeps_device_ownership(
    hass: HomeAssistant, init_integration: MockConfigEntry, mqtt_speaker: MockConfigEntry
) -> None:
    """No duplicate device is created and the existing one stays MQTT-owned."""
    registry = er.async_get(hass)
    source = registry.async_get(SOURCE_ENTITIES["power"])
    player = er.async_entries_for_config_entry(registry, init_integration.entry_id)[0]
    assert init_integration.state is ConfigEntryState.LOADED
    assert player.device_id == source.device_id
    assert dr.async_get(hass).async_get(source.device_id).config_entry_id == mqtt_speaker.entry_id
    assert not dr.async_entries_for_config_entry(dr.async_get(hass), init_integration.entry_id)
    assert player.unique_id == "F88B419FC114_player"


async def test_unload_preserves_mqtt_entities(
    hass: HomeAssistant, init_integration: MockConfigEntry
) -> None:
    """Unloading the helper does not remove or control source entities."""
    assert await hass.config_entries.async_unload(init_integration.entry_id)
    await hass.async_block_till_done()
    assert init_integration.state is ConfigEntryState.NOT_LOADED
    hass.states.async_set(SOURCE_ENTITIES["power"], "off")
    await hass.async_block_till_done()
    assert hass.states.get(SOURCE_ENTITIES["power"]).state == "off"
