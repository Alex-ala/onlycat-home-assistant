"""Sensor platform for OnlyCat."""

from __future__ import annotations
from datetime import timedelta

from typing import TYPE_CHECKING

from .binary_sensor_connectivity import OnlyCatConnectionSensor
from .binary_sensor_contraband import OnlyCatContrabandSensor
from .binary_sensor_event import OnlyCatEventSensor
from .binary_sensor_lock import OnlyCatLockSensor
from .binary_sensor_device_errors import OnlyCatErrorSensor

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .data.__init__ import OnlyCatConfigEntry

SCAN_INTERVAL = timedelta(hours=6)

async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: OnlyCatConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    async_add_entities(
        sensor
        for device in entry.runtime_data.devices
        for sensor in (
            OnlyCatEventSensor(
                device=device,
                api_client=entry.runtime_data.client,
            ),
            OnlyCatContrabandSensor(
                device=device,
                api_client=entry.runtime_data.client,
            ),
            OnlyCatLockSensor(
                device=device,
                api_client=entry.runtime_data.client,
            ),
            OnlyCatConnectionSensor(
                device=device,
                api_client=entry.runtime_data.client,
            ),
        )
    )
    async_add_entities([
        OnlyCatErrorSensor(
            device=device,
            api_client=entry.runtime_data.client
        )for device in entry.runtime_data.devices],
         update_before_add=True
    )
    SCAN_INTERVAL = timedelta(hours=min(device.settings["poll_interval_hours"] for device in entry.runtime_data.devices))
