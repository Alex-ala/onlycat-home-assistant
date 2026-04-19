"""Custom types for onlycat representing a flap event summary."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field, fields

_LOGGER = logging.getLogger(__name__)


class SubEvent:
    """Data representing a subevent of an OnlyCat flap event summary."""

    start_frame_index: int
    end_frame_index: int
    rfid_code: str | None
    direction: str
    action: str


@dataclass
class EventSummary:
    """Data representing an OnlyCat flap event summary."""

    device_id: str
    event_id: int
    subevents: list[SubEvent] = field(default_factory=list)
    processed_frame_count: int | None = None
    invalidated_at: None = None
    processing_at: None = None
    processing_by: None = None

    @classmethod
    def from_api_response(cls, api_summary: dict) -> EventSummary | None:
        """Create an Event instance from API response data."""
        if (
            not api_summary
            or "deviceId" not in api_summary
            or "eventId" not in api_summary
        ):
            return None
        device_id = api_summary.get("deviceId")
        event_id = api_summary.get("eventId")
        processed_frame_count = api_summary.get("processedFrameCount")
        invalidated_at = api_summary.get("invalidatedAt")
        processing_at = api_summary.get("processingAt")
        processing_by = api_summary.get("processingBy")
        subevents = []
        for subevent_data in api_summary.get("subevents", []):
            if not all(
                key in subevent_data
                for key in (
                    "startFrameIndex",
                    "endFrameIndex",
                    "rfidCode",
                    "direction",
                    "action",
                )
            ):
                _LOGGER.warning(
                    "Skipping incomplete subevent in event summary: %s", subevent_data
                )
                continue
            subevent = SubEvent()
            subevent.start_frame_index = subevent_data["startFrameIndex"]
            subevent.end_frame_index = subevent_data["endFrameIndex"]
            subevent.rfid_code = subevent_data.get("rfidCode")
            subevent.direction = subevent_data.get("direction")
            subevent.action = subevent_data.get("action")

            subevents.append(subevent)

        return cls(
            device_id=device_id,
            event_id=event_id,
            subevents=subevents,
            processed_frame_count=processed_frame_count,
            invalidated_at=invalidated_at,
            processing_at=processing_at,
            processing_by=processing_by,
        )

    def update_from(self, updated_summary: EventSummary) -> None:
        """Update the event summary with data from another event summary instance."""
        if updated_summary is None:
            return
        for obj_field in fields(self):
            new_value = getattr(updated_summary, obj_field.name, None)
            if new_value is not None:
                if obj_field.name == "subevents":
                    old_value = getattr(self, obj_field.name) or []
                    new_value = old_value + list(set(new_value) - set(old_value))
                setattr(self, obj_field.name, new_value)
