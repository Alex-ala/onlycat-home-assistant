"""Custom types for onlycat representing a flap event summary."""

from __future__ import annotations

import logging
from dataclasses import dataclass

_LOGGER = logging.getLogger(__name__)

class SubEvent:
    """Data representing a subevent of an OnlyCat flap event summary."""

    start_frame_index: int
    end_frame_index: int
    rfid_code: str | None
    direction: str | None
    action: str | None


@dataclass
class EventSummary:
    """Data representing an OnlyCat flap event summary."""

    device_id: str | None = None
    event_id: int | None = None
    subevents: list[SubEvent] = list()
    processed_frame_count: int | None = None
    invalidated_at: None = None
    processing_at: None = None
    processing_by: None = None

    @classmethod
    def from_api_response(cls, api_summary: dict) -> EventSummary | None:
        """Create an Event instance from API response data."""
        if not api_summary:
            return None
        device_id = api_summary.get("deviceId")
        event_id = api_summary.get("eventId")
        processed_frame_count = api_summary.get("processedFrameCount")
        invalidated_at = api_summary.get("invalidatedAt")
        processing_at = api_summary.get("processingAt")
        processing_by = api_summary.get("processingBy")
        subevents = []
        for subevent_data in api_summary.get("subevents", []):
            if not all(key in subevent_data for key in ("startFrameIndex", "endFrameIndex", "rfidCode", "direction", "action")):
                _LOGGER.warning(f"Skipping invalid subevent in event summary {event_id} for device {device_id}: {subevent_data}")
                continue
            subevent = SubEvent(
                start_frame_index=subevent_data["startFrameIndex"],
                end_frame_index=subevent_data["endFrameIndex"],
                rfid_code=subevent_data.get("rfidCode"),
                direction=subevent_data.get("direction"),
                action=subevent_data.get("action"),
            )
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
