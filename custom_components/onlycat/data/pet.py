"""Custom types for onlycat representing a pet."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime

    from .event import Event
    from .event_summary import EventSummary, SubEvent

_LOGGER = logging.getLogger(__name__)


@dataclass
class Pet:
    """Data representing a pet."""

    rfid_code: str
    location: str
    last_seen: datetime | None
    last_seen_event: Event | None = None
    last_seen_summary: EventSummary | None = None
    label: str | None = None

    def update_from_subevent(self, subevent: SubEvent) -> None:
        """Update pet data from a subevent."""
        # TODO: Remove these static strings
        if subevent.direction == "INWARD":
            if subevent.action == "TRANSIT":
                self.location = "home"
            else:
                self.location = "not_home"
        elif subevent.direction == "OUTWARD":
            if subevent.action == "TRANSIT":
                self.location = "not_home"
            else:
                self.location = "home"
        _LOGGER.debug("Updated pet %s location to %s based on subevent", self.rfid_code, self.location)
