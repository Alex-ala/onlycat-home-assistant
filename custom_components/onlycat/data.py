"""Custom types for onlycat."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from device_tracker import OnlyCatDeviceTrackerWrapper
    from homeassistant.config_entries import ConfigEntry

    from .api import OnlyCatApiClient

_LOGGER = logging.getLogger(__name__)

type OnlyCatConfigEntry = ConfigEntry[OnlyCatData]


@dataclass
class OnlyCatData:
    """Data for the OnlyCat integration."""

    client: OnlyCatApiClient
    devices: list
    pets: dict
    device_tracker: OnlyCatDeviceTrackerWrapper | None = None
