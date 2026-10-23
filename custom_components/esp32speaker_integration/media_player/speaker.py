"""Media player backed by the firmware's existing MQTT entities."""

import math
from typing import Any
from urllib.parse import urlsplit

from custom_components.esp32speaker_integration.const import DOMAIN
from custom_components.esp32speaker_integration.entity import Esp32SpeakerEntity
from homeassistant.components import media_source
from homeassistant.components.media_player import (
    MediaPlayerDeviceClass,
    MediaPlayerEntity,
    MediaPlayerEntityDescription,
    MediaPlayerEntityFeature,
    MediaPlayerState,
    async_process_play_media_url,
)
from homeassistant.const import STATE_OFF, STATE_ON, STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.exceptions import ServiceValidationError

ENTITY_DESCRIPTIONS = (
    MediaPlayerEntityDescription(key="player", translation_key="player", name=None),
)


class Esp32SpeakerMediaPlayer(MediaPlayerEntity, Esp32SpeakerEntity):
    """Expose real firmware capabilities, without optimistic playback state."""

    _attr_device_class = MediaPlayerDeviceClass.SPEAKER
    _attr_volume_step = 1 / 21
    _attr_supported_features = (
        MediaPlayerEntityFeature.PLAY
        | MediaPlayerEntityFeature.STOP
        | MediaPlayerEntityFeature.PLAY_MEDIA
        | MediaPlayerEntityFeature.MEDIA_ANNOUNCE
        | MediaPlayerEntityFeature.SELECT_SOURCE
        | MediaPlayerEntityFeature.VOLUME_SET
        | MediaPlayerEntityFeature.VOLUME_STEP
        | MediaPlayerEntityFeature.TURN_ON
        | MediaPlayerEntityFeature.TURN_OFF
    )

    @property
    def available(self) -> bool:
        """Treat a missing or disconnected power entity as an offline speaker."""
        power = self.coordinator.data.get("power")
        return super().available and power is not None and power.state != STATE_UNAVAILABLE

    @property
    def state(self) -> MediaPlayerState | None:
        """Map the firmware's actual playback indication, not a mains power state."""
        power = self.coordinator.data.get("power")
        if power is None or power.state not in (STATE_ON, STATE_OFF):
            return None
        return MediaPlayerState.PLAYING if power.state == STATE_ON else MediaPlayerState.IDLE

    @property
    def volume_level(self) -> float | None:
        """Convert the firmware's 22 volume steps to Home Assistant's range."""
        volume = self.coordinator.data.get("volume")
        if volume is None:
            return None
        try:
            value = float(volume.state)
        except ValueError:
            return None
        return max(0.0, min(1.0, value / 21)) if math.isfinite(value) else None

    def _state_text(self, key: str) -> str | None:
        """Read optional metadata without leaking unknown sentinel values."""
        state = self.coordinator.data.get(key)
        if state is None or state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            return None
        return state.state

    @property
    def media_title(self) -> str | None:
        """Return the current title reported by the speaker."""
        return self._state_text("title")

    @property
    def media_channel(self) -> str | None:
        """Return the actual station or SD path reported by the speaker."""
        return self._state_text("station")

    @property
    def source_list(self) -> list[str]:
        """Keep radio names and SD paths distinct even when names collide."""
        sources: list[str] = []
        for key, prefix in (("radio", "Radio: "), ("sd", "SD: ")):
            if (state := self.coordinator.data.get(key)) is not None:
                sources.extend(prefix + option for option in state.attributes.get("options", []))
        return sources

    @property
    def source(self) -> str | None:
        """Use live station metadata rather than a stale select state."""
        station = self._state_text("station")
        if station is None:
            return None
        candidate = station if station.startswith("SD: ") else f"Radio: {station}"
        return candidate if candidate in self.source_list else None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Start the last or first stored radio station."""
        await self.coordinator.async_command("power", "turn_on")

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Stop playback; the ESP32 itself remains powered."""
        await self.coordinator.async_command("power", "turn_off")

    async def async_media_play(self) -> None:
        """Start radio playback, without promising paused-file resumption."""
        await self.async_turn_on()

    async def async_media_stop(self) -> None:
        """Stop playback."""
        await self.async_turn_off()

    async def async_set_volume_level(self, volume: float) -> None:
        """Set the nearest supported hardware volume step."""
        if not math.isfinite(volume) or not 0 <= volume <= 1:
            raise ServiceValidationError(translation_domain=DOMAIN, translation_key="invalid_volume")
        await self.coordinator.async_command("volume", "set_value", value=round(volume * 21))

    async def async_select_source(self, source: str) -> None:
        """Play a radio favorite or SD file through its existing select entity."""
        if source not in self.source_list:
            raise ServiceValidationError(translation_domain=DOMAIN, translation_key="invalid_source")
        key = "sd" if source.startswith("SD: ") else "radio"
        await self.coordinator.async_command(key, "select_option", option=source.split(": ", 1)[1])

    async def async_play_media(self, media_type: str, media_id: str, **kwargs: Any) -> None:
        """Play an audio URL, a local SD file, or an announcement/TTS URL."""
        announce = kwargs.get("announce", False)
        if media_source.is_media_source_id(media_id):
            resolved = await media_source.async_resolve_media(self.hass, media_id, self.entity_id)
            media_id = resolved.url
        if media_id.startswith("/") and not announce:
            sd = self.coordinator.data.get("sd")
            if sd is not None and media_id in sd.attributes.get("options", []):
                await self.coordinator.async_command("sd", "select_option", option=media_id)
                return
        media_id = async_process_play_media_url(self.hass, media_id)
        if urlsplit(media_id).scheme not in ("http", "https"):
            raise ServiceValidationError(translation_domain=DOMAIN, translation_key="invalid_media")
        await self.coordinator.async_publish("announce" if announce else "station_url", media_id)