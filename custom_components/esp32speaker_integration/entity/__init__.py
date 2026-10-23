"""
Entity package for esp32speaker_integration.

Architecture:
    All platform entities inherit from (PlatformEntity, Esp32SpeakerEntity).
    MRO order matters — platform-specific class first, then the integration base.
    Entities read data from coordinator.data and NEVER call the API client directly.
    Unique IDs follow the pattern: {entry_id}_{description.key}

See entity/base.py for the Esp32SpeakerEntity base class.
"""

from .base import Esp32SpeakerEntity

__all__ = ["Esp32SpeakerEntity"]
