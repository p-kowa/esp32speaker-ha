"""Test the media player through Home Assistant states and service calls."""

from unittest.mock import AsyncMock

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_mock_service

from homeassistant.components.media_player import MediaPlayerEntityFeature
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import entity_registry as er

from .conftest import SOURCE_ENTITIES, TOPIC


def player_id(hass: HomeAssistant, entry: MockConfigEntry) -> str:
    """Look up the media player without depending on a generated entity name."""
    return er.async_entries_for_config_entry(er.async_get(hass), entry.entry_id)[0].entity_id


async def test_live_state(hass: HomeAssistant, init_integration: MockConfigEntry) -> None:
    """Metadata and volume track the source entities without polling."""
    entity_id = player_id(hass, init_integration)
    state = hass.states.get(entity_id)
    assert state.state == "playing"
    assert state.attributes["volume_level"] == pytest.approx(3 / 21)
    assert state.attributes["media_title"] == "Current song"
    assert state.attributes["source_list"] == ["Radio: SWR3", "Radio: DLF", "SD: /song.mp3"]
    assert not state.attributes["supported_features"] & MediaPlayerEntityFeature.PAUSE
    assert not state.attributes["supported_features"] & MediaPlayerEntityFeature.SEEK
    hass.states.async_set(SOURCE_ENTITIES["power"], "off")
    hass.states.async_set(SOURCE_ENTITIES["volume"], "21")
    hass.states.async_set(SOURCE_ENTITIES["title"], "New title")
    await hass.async_block_till_done()
    state = hass.states.get(entity_id)
    assert state.state == "idle"
    assert state.attributes["volume_level"] == 1
    assert state.attributes["media_title"] == "New title"


async def test_controls(hass: HomeAssistant, init_integration: MockConfigEntry) -> None:
    """Commands go through the existing switch, number and select platforms."""
    switch_calls = async_mock_service(hass, "switch", "turn_off")
    number_calls = async_mock_service(hass, "number", "set_value")
    select_calls = async_mock_service(hass, "select", "select_option")
    target = {"entity_id": player_id(hass, init_integration)}
    await hass.services.async_call("media_player", "media_stop", target, blocking=True)
    await hass.services.async_call(
        "media_player", "volume_set", {**target, "volume_level": 0.5}, blocking=True
    )
    await hass.services.async_call(
        "media_player", "select_source", {**target, "source": "SD: /song.mp3"}, blocking=True
    )
    assert switch_calls[0].data["entity_id"] == SOURCE_ENTITIES["power"]
    assert number_calls[0].data["value"] == 10
    assert select_calls[0].data["entity_id"] == SOURCE_ENTITIES["sd"]
    assert select_calls[0].data["option"] == "/song.mp3"
    assert hass.states.get(target["entity_id"]).state == "playing"


@pytest.mark.parametrize("announce", [False, True])
async def test_play_url(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
    mqtt_publish: AsyncMock,
    announce: bool,
) -> None:
    """URL commands use the correct topic and must never be retained."""
    await hass.services.async_call(
        "media_player",
        "play_media",
        {
            "entity_id": player_id(hass, init_integration),
            "media_content_id": "http://example.com/test.mp3",
            "media_content_type": "music",
            "announce": announce,
        },
        blocking=True,
    )
    command = "announce" if announce else "station_url"
    mqtt_publish.assert_awaited_once_with(
        hass, f"{TOPIC}/set/{command}", "http://example.com/test.mp3", qos=0, retain=False
    )


@pytest.mark.parametrize("source_state", ["unavailable", "unknown"])
async def test_missing_source(
    hass: HomeAssistant, init_integration: MockConfigEntry, source_state: str
) -> None:
    """Offline and unknown source states are not presented as stopped playback."""
    hass.states.async_set(SOURCE_ENTITIES["power"], source_state)
    await hass.async_block_till_done()
    assert hass.states.get(player_id(hass, init_integration)).state == source_state


async def test_invalid_source(hass: HomeAssistant, init_integration: MockConfigEntry) -> None:
    """Reject sources not advertised by the current selects."""
    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            "media_player",
            "select_source",
            {"entity_id": player_id(hass, init_integration), "source": "not a station"},
            blocking=True,
        )
