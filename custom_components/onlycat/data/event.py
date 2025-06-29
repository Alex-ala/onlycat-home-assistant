"""Custom types for onlycat representing a flap event."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from .type import Type

_LOGGER = logging.getLogger(__name__)


class EventTriggerSource(Enum):
    """Enum representing the source of an OnlyCat flap event."""

    UNKNOWN = -1
    MANUAL = 0
    REMOTE = 1
    INDOOR_MOTION = 2
    OUTDOOR_MOTION = 3

    @classmethod
    def _missing_(cls, value: str) -> EventTriggerSource:
        """Handle missing enum values in case of API extensions."""
        _LOGGER.warning("Unknown event trigger source: %s", value)
        return cls.UNKNOWN


class EventClassification(Enum):
    """Enum representing the classification of an OnlyCat flap event."""

    UNKNOWN = 0
    CLEAR = 1
    SUSPICIOUS = 2
    CONTRABAND = 3
    HUMAN_ACTIVITY = 4
    REMOTE_UNLOCK = 10

    @classmethod
    def _missing_(cls, value: str) -> EventClassification:
        """Handle missing enum values in case of API extensions."""
        _LOGGER.warning("Unknown event classification: %s", value)
        return cls.UNKNOWN


@dataclass
class Event:
    """Data representing an OnlyCat flap event."""

    global_id: int
    device_id: str
    event_id: int
    timestamp: datetime
    frame_count: int
    event_trigger_source: EventTriggerSource
    event_classification: EventClassification
    poster_frame_index: int
    access_token: str
    rfid_codes: list[str]

    @classmethod
    def from_api_response(cls, api_event: dict) -> Event | None:
        """Create an Event instance from API response data."""
        if not api_event:
            return None
        timestamp = api_event.get("timestamp")
        trigger_source = api_event.get("eventTriggerSource")
        classification = api_event.get("eventClassification")

        return cls(
            global_id=api_event.get("globalId"),
            device_id=api_event.get("deviceId"),
            event_id=api_event.get("eventId"),
            timestamp=datetime.fromisoformat(timestamp) if timestamp else None,
            frame_count=api_event.get("frameCount"),
            event_trigger_source=EventTriggerSource(trigger_source)
            if trigger_source
            else None,
            event_classification=EventClassification(classification)
            if classification
            else None,
            poster_frame_index=api_event.get("posterFrameIndex"),
            access_token=api_event.get("accessToken"),
            rfid_codes=api_event.get("rfidCodes"),
        )


@dataclass
class EventUpdate:
    """Data representing an update to an OnlyCat flap event."""

    device_id: str
    event_id: int
    type: Type
    body: Event

    @classmethod
    def from_api_response(cls, api_event: dict) -> EventUpdate | None:
        """Create an EventUpdate instance from API response data."""
        return cls(
            device_id=api_event["deviceId"],
            event_id=api_event["eventId"],
            type=Type(api_event["type"]) if api_event.get("type") else Type.UNKNOWN,
            body=Event.from_api_response(api_event.get("body")),
        )
