"""Sensor entity for esp32speaker_integration."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from custom_components.esp32speaker_integration.entity import Esp32SpeakerEntity
from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.helpers.typing import StateType


@dataclass(frozen=True, kw_only=True)
class Esp32SpeakerSensorEntityDescription(SensorEntityDescription):
    """Describes a sensor and how to read it from coordinator data."""

    value_fn: Callable[[dict[str, Any]], StateType]


class Esp32SpeakerSensor(SensorEntity, Esp32SpeakerEntity):
    """Sensor backed by one value in the coordinator payload."""

    entity_description: Esp32SpeakerSensorEntityDescription

    @property
    def native_value(self) -> StateType:
        """Return the value read from coordinator data."""
        return self.entity_description.value_fn(self.coordinator.data)
