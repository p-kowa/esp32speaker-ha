"""Test setup against the firmware's actual MQTT discovery identity format."""

from unittest.mock import patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.esp32speaker_integration.const import DOMAIN
from homeassistant.config_entries import SOURCE_RECONFIGURE, SOURCE_USER
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers import entity_registry as er

from .conftest import DEVICE_ID, SOURCE_ENTITIES, TOPIC

USER_INPUT = {"device_id": DEVICE_ID, "power_entity": SOURCE_ENTITIES["power"], "topic_prefix": TOPIC}


async def test_user_setup(hass: HomeAssistant, mqtt_speaker: MockConfigEntry) -> None:
    """Resolve all existing MQTT entities and normalize the firmware identity."""
    with patch("custom_components.esp32speaker_integration.async_setup_entry", return_value=True):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_USER}, data={**USER_INPUT, "device_id": DEVICE_ID.lower()}
        )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"]["device_id"] == DEVICE_ID
    assert result["data"]["entities"] == SOURCE_ENTITIES
    assert result["result"].unique_id == DEVICE_ID


@pytest.mark.parametrize(
    ("changes", "expected_errors"),
    [
        ({"device_id": "002dc75ef216af1bd4439d57e9f43db8"}, {"device_id": "invalid_device_id"}),
        ({"topic_prefix": "other-device"}, {"power_entity": "device_mismatch"}),
        ({"topic_prefix": "esp32radio/#"}, {"topic_prefix": "invalid_topic"}),
        ({"power_entity": "switch.missing"}, {"power_entity": "device_mismatch"}),
    ],
)
async def test_invalid_configuration(
    hass: HomeAssistant, mqtt_speaker: MockConfigEntry, changes: dict, expected_errors: dict
) -> None:
    """Do not silently bind a helper to the wrong device or a wildcard topic."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}, data={**USER_INPUT, **changes}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == expected_errors


async def test_duplicate_device(
    hass: HomeAssistant, mqtt_speaker: MockConfigEntry, config_entry: MockConfigEntry
) -> None:
    """The same firmware ID cannot be configured twice."""
    config_entry.add_to_hass(hass)
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}, data=USER_INPUT
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_renamed_entity_is_discovered(
    hass: HomeAssistant, mqtt_speaker: MockConfigEntry
) -> None:
    """Registry unique IDs, not translated entity names, decide the mapping."""
    er.async_get(hass).async_update_entity(SOURCE_ENTITIES["volume"], new_entity_id="number.custom_name")
    with patch("custom_components.esp32speaker_integration.async_setup_entry", return_value=True):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_USER}, data=USER_INPUT
        )
    assert result["data"]["entities"]["volume"] == "number.custom_name"


async def test_reconfigure(hass: HomeAssistant, init_integration: MockConfigEntry) -> None:
    """Reconfiguration refreshes the entity mapping without changing identity."""
    er.async_get(hass).async_update_entity(SOURCE_ENTITIES["volume"], new_entity_id="number.new_volume")
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_RECONFIGURE, "entry_id": init_integration.entry_id},
        data=USER_INPUT,
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    assert init_integration.data["entities"]["volume"] == "number.new_volume"