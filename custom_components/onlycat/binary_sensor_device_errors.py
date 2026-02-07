"""Sensor platform for OnlyCat."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .api import OnlyCatApiClient
    from .data.device import Device

ENTITY_DESCRIPTION = BinarySensorEntityDescription(
    key="OnlyCat",
    name="Device errors",
    device_class=BinarySensorDeviceClass.PROBLEM,
    translation_key="onlycat_error_sensor",
)


class OnlyCatErrorSensor(BinarySensorEntity):
    """OnlyCat Error Sensor class."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info to map to a device."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.device.device_id)},
            name=self.device.description,
            serial_number=self.device.device_id,
        )

    def __init__(
        self,
        device: Device,
        api_client: OnlyCatApiClient,
    ) -> None:
        """Initialize the sensor class."""
        self.entity_description = ENTITY_DESCRIPTION
        self._attr_is_on = False
        self._attr_extra_state_attributes = {}
        self._attr_raw_data = None
        self.device: Device = device
        self._attr_unique_id = device.device_id.replace("-", "_").lower() + "_errors"
        self._api_client = api_client
        self.entity_id = "sensor." + self._attr_unique_id
        self.should_poll = True


    async def async_update(self) -> None:
        """Handle update."""

        errors = await self._api_client.send_message(
            "getDeviceErrorLogs", {
                "deviceId": self.device.device_id,
                "limit": 100,
                "hours": self.device.settings["poll_interval_hours"],
                "measureName": "message"
                })
        self._attr_is_on = len(errors) > 0
        self._attr_extra_state_attributes = {"errors": errors}
        self.async_write_ha_state()

