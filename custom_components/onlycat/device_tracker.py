"""Device tracker platform for OnlyCat."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.components.device_tracker import (
    TrackerEntity,
    TrackerEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .data import OnlyCatConfigEntry


ENTITY_DESCRIPTION = TrackerEntityDescription(
    key="OnlyCat",
    name="OnlyCat Cat Tracker",
    icon="mdi:paw",
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: OnlyCatConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the device tracker platform."""
    entry.runtime_data.device_tracker = OnlyCatDeviceTrackerWrapper(
        entry=entry, async_add_entities=async_add_entities
    )


class OnlyCatDeviceTrackerWrapper:
    """Wrapper for OnlyCat device tracker."""

    def __init__(
        self, entry: OnlyCatConfigEntry, async_add_entities: AddEntitiesCallback
    ) -> None:
        """Initialize the wrapper."""
        self.entry = entry
        self.async_add_entities = async_add_entities
        self.api_client = entry.runtime_data.client
        self.api_client.add_event_listener(
            "eventUpdate", self.see_or_add_device_tracker
        )

    async def see_or_add_device_tracker(self, data: dict) -> None:
        """See or add a device tracker seen in this event."""
        _LOGGER.debug("Processing event update for device_tracker: %s", data)
        if "rfidCodes" in data["body"] and len(data["body"]["rfidCodes"]) > 0:
            for rfid in data["body"]["rfidCodes"]:
                if rfid in self.entry.runtime_data.pets:
                    await self.see_device_tracker(rfid, data["deviceId"])
                else:
                    await self.add_device_tracker(rfid, data["deviceId"])

    async def see_device_tracker(self, rfid: str, device_id: str) -> None:
        """See a device tracker."""
        _LOGGER.debug("Seeing device tracker for RFID: %s", rfid)
        # TODO: Implement

    async def add_device_tracker(self, rfid: str, device_id: str) -> None:
        """Add a new device tracker for the given RFID."""
        pet_info = await self.api_client.send_message(
            "getRfidProfile",
            {"rfidCode": rfid, "deviceId": device_id, "subscribe": True},
        )
        name = pet_info.get("label", rfid)
        _LOGGER.debug("Adding device tracker for RFID: %s", rfid)
        device_tracker = OnlyCatDeviceTracker(device=device_id, name=name, rfid=rfid)
        self.async_add_entities([device_tracker])
        self.entry.runtime_data.pets[rfid] = device_tracker


class OnlyCatDeviceTracker(TrackerEntity):
    """Device tracker for OnlyCat."""

    _attr_has_entity_name = True
    _attr_should_poll = False
    entity_category = EntityCategory.DIAGNOSTIC
    _attr_translation_key = "onlycat_device_tracker"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info to map to a device."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.device)},
            serial_number=self.device,
        )

    def __init__(
        self,
        device: dict,
        name: str,
        rfid: str,
    ) -> None:
        """Initialize the sensor class."""
        self.entity_description = ENTITY_DESCRIPTION
        self._state = None
        self._attr_raw_data = None
        self._attr_name = "Pet"
        self._attr_unique_id = device.replace("-", "_").lower() + '_' + name
        self._attr_extra_state_attributes = {"rfid": rfid }
        self.entity_id = "device_tracker." + self._attr_unique_id
        self.device = device
        self.name = name
        self.rfid = rfid

    # def see(self, data) -> None:
    #     """See the device tracker."""
    #     _LOGGER.debug("Seeing device tracker: %s", self._attr_unique_id)
    #     self._state = "home"
    #     self._attr_extra_state_attributes["last_seen"] = data.get("timestamp")
    #     self.async_write_ha_state()


# TODO: Mapping to new name with same RFID doesnt work persistently as runtime_data.pets is not persistent.
# TODO: Events are not handled along multiple updates, so the information on which side the event was triggered is lost.
# TODO: Device tracker see is not implemented