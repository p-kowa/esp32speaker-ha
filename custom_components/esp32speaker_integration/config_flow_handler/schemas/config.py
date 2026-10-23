"""Setup schema for an existing MQTT speaker."""

from collections.abc import Mapping
from typing import Any

import probatio

from custom_components.esp32speaker_integration.const import (
    CONF_DEVICE_ID,
    CONF_POWER_ENTITY,
    CONF_TOPIC_PREFIX,
)
from homeassistant.helpers import selector


def get_user_schema(defaults: Mapping[str, Any] | None = None) -> probatio.Schema:
    """Build the three-field setup and reconfiguration form."""
    defaults = defaults or {}
    return probatio.Schema(
        {
            probatio.Required(
                CONF_DEVICE_ID, default=defaults.get(CONF_DEVICE_ID, probatio.UNDEFINED)
            ): selector.TextSelector(),
            probatio.Required(
                CONF_POWER_ENTITY, default=defaults.get(CONF_POWER_ENTITY, probatio.UNDEFINED)
            ): selector.EntitySelector(selector.EntitySelectorConfig(domain="switch", integration="mqtt")),
            probatio.Required(
                CONF_TOPIC_PREFIX, default=defaults.get(CONF_TOPIC_PREFIX, probatio.UNDEFINED)
            ): selector.TextSelector(),
        },
    )
