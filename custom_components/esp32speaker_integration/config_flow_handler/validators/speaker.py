"""Validate hardware identity and discover the existing MQTT entities."""

import re
from typing import Any

from custom_components.esp32speaker_integration.const import (
    CONF_DEVICE_ID,
    CONF_ENTITIES,
    CONF_POWER_ENTITY,
    CONF_TOPIC_PREFIX,
    ENTITY_SUFFIXES,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry as dr, entity_registry as er


@callback
def validate_speaker(
    hass: HomeAssistant, user_input: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, str]]:
    """Cross-check the hardware ID and prefix against MQTT discovery metadata."""
    device_id = user_input[CONF_DEVICE_ID].strip().upper()
    if re.fullmatch(r"[0-9A-F]{12}", device_id) is None:
        return {}, {CONF_DEVICE_ID: "invalid_device_id"}
    topic = user_input[CONF_TOPIC_PREFIX].strip().rstrip("/")
    if not topic or any(character in topic for character in ("+", "#", "\x00")):
        return {}, {CONF_TOPIC_PREFIX: "invalid_topic"}
    registry = er.async_get(hass)
    power = registry.async_get(user_input[CONF_POWER_ENTITY])
    prefix = f"{topic}_{device_id[-8:]}"
    if (
        power is None
        or power.platform != "mqtt"
        or power.domain != "switch"
        or power.device_id is None
        or power.disabled
        or power.unique_id != f"{prefix}_power"
    ):
        return {}, {CONF_POWER_ENTITY: "device_mismatch"}
    device = dr.async_get(hass).async_get(power.device_id)
    if device is None:
        return {}, {CONF_POWER_ENTITY: "device_mismatch"}
    entries = er.async_entries_for_device(registry, power.device_id)
    entities = {
        key: candidate.entity_id
        for key, suffix in ENTITY_SUFFIXES.items()
        for candidate in entries
        if candidate.platform == "mqtt"
        and candidate.unique_id == f"{prefix}_{suffix}"
        and not candidate.disabled
    }
    if "volume" not in entities or "power" not in entities:
        return {}, {"base": "missing_entities"}
    return {
        CONF_DEVICE_ID: device_id,
        CONF_POWER_ENTITY: power.entity_id,
        CONF_TOPIC_PREFIX: topic,
        CONF_ENTITIES: entities,
        "title": device.name_by_user or device.name or "ESP32 Speaker",
    }, {}