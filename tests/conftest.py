"""Fixtures for a real helper layered over an existing MQTT device."""

from collections.abc import AsyncGenerator, Generator
from unittest.mock import AsyncMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.esp32speaker_integration.const import DOMAIN, ENTITY_SUFFIXES
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er

DEVICE_ID = "F88B419FC114"
TOPIC = "esp32radio-419FC114"
SOURCE_ENTITIES = {
    "power": "switch.speaker_power",
    "volume": "number.speaker_volume",
    "station": "sensor.speaker_station",
    "title": "sensor.speaker_title",
    "radio": "select.speaker_radio",
    "sd": "select.speaker_sd",
    "announcing": "binary_sensor.speaker_announcing",
}


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: None) -> None:
    """Load custom integrations in every test."""


@pytest.fixture
def mqtt_publish() -> Generator[AsyncMock]:
    """Mock only the outbound MQTT transport boundary."""
    with patch("homeassistant.components.mqtt.async_publish", new_callable=AsyncMock) as publish:
        yield publish


@pytest.fixture
async def mqtt_speaker(hass: HomeAssistant) -> AsyncGenerator[MockConfigEntry]:
    """Represent MQTT discovery without connecting to an external broker."""
    mqtt_entry = MockConfigEntry(domain="mqtt", title="MQTT", data={"broker": "test-broker"})
    mqtt_entry.add_to_hass(hass)
    with patch("homeassistant.components.mqtt.async_setup_entry", return_value=True):
        assert await hass.config_entries.async_setup(mqtt_entry.entry_id)
        device = dr.async_get(hass).async_get_or_create(
            config_entry_id=mqtt_entry.entry_id,
            identifiers={("mqtt", f"{TOPIC}_419FC114")},
            name="ESP32 Radio",
        )
        registry = er.async_get(hass)
        for key, entity_id in SOURCE_ENTITIES.items():
            domain, object_id = entity_id.split(".", 1)
            registry.async_get_or_create(
                domain,
                "mqtt",
                f"{TOPIC}_419FC114_{ENTITY_SUFFIXES[key]}",
                suggested_object_id=object_id,
                device_id=device.id,
                config_entry=mqtt_entry,
            )
        hass.states.async_set(SOURCE_ENTITIES["power"], "on")
        hass.states.async_set(SOURCE_ENTITIES["volume"], "3", {"min": 0, "max": 21, "step": 1})
        hass.states.async_set(SOURCE_ENTITIES["title"], "Current song")
        hass.states.async_set(SOURCE_ENTITIES["station"], "SWR3")
        hass.states.async_set(SOURCE_ENTITIES["radio"], "SWR3", {"options": ["SWR3", "DLF"]})
        hass.states.async_set(SOURCE_ENTITIES["sd"], "/song.mp3", {"options": ["/song.mp3"]})
        hass.states.async_set(SOURCE_ENTITIES["announcing"], "off")
        yield mqtt_entry


@pytest.fixture
def config_entry() -> MockConfigEntry:
    """Return one configured speaker helper."""
    return MockConfigEntry(
        domain=DOMAIN,
        title="ESP32 Radio",
        unique_id=DEVICE_ID,
        version=2,
        data={
            "device_id": DEVICE_ID,
            "power_entity": SOURCE_ENTITIES["power"],
            "topic_prefix": TOPIC,
            "entities": SOURCE_ENTITIES,
        },
    )


@pytest.fixture
async def init_integration(
    hass: HomeAssistant, mqtt_speaker: MockConfigEntry, config_entry: MockConfigEntry
) -> MockConfigEntry:
    """Load the actual media player platform over the source device."""
    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    return config_entry
