"""Filter maintenance binary sensor for esp32speaker_integration."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from custom_components.esp32speaker_integration.entity import Esp32SpeakerEntity
from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorEntityDescription
from homeassistant.components.binary_sensor.const import BinarySensorDeviceClass


@dataclass(frozen=True, kw_only=True)
class Esp32SpeakerBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes a binary sensor and how to read it from coordinator data."""

    value_fn: Callable[[dict[str, Any]], bool | None]


ENTITY_DESCRIPTIONS: tuple[Esp32SpeakerBinarySensorEntityDescription, ...] = (
    Esp32SpeakerBinarySensorEntityDescription(
        key="filter_replacement",
        translation_key="filter_replacement",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=lambda data: data.get("filter_replacement"),
    ),
)


class Esp32SpeakerFilterSensor(BinarySensorEntity, Esp32SpeakerEntity):
    """Binary sensor reporting whether the filter needs replacing."""

    entity_description: Esp32SpeakerBinarySensorEntityDescription

    @property
    def is_on(self) -> bool | None:
        """Return the value read from coordinator data."""
        return self.entity_description.value_fn(self.coordinator.data)
