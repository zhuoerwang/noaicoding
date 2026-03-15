"""Hotel Booking System — ICF-Style System Design

Implement a hotel booking system across 4 progressive levels.

Run tests by level:
    pytest test_hotel_booking.py -k "TestLevel1"
    pytest test_hotel_booking.py -k "TestLevel2"
    pytest test_hotel_booking.py -k "TestLevel3"
    pytest test_hotel_booking.py -k "TestLevel4"
"""

from __future__ import annotations

import math
from enum import Enum


class RoomType(Enum):
    SINGLE = "single"
    DOUBLE = "double"
    SUITE = "suite"


class Hotel:
    """A hotel booking system with room types, pricing, loyalty,
    overbooking, and revenue reporting."""

    # Level 1: Hotel(rooms: list[int])
    # Level 2: Hotel(rooms: dict[RoomType, list[int]])
    def __init__(self, rooms: list[int] | dict[RoomType, list[int]]) -> None:
        """Initialize the hotel with room IDs.

        Args:
            rooms: Either a list of room IDs (Level 1) or a dict mapping
                RoomType to list of room IDs (Level 2+).
        """
        pass

    # ── Level 1 ────────────────────────────────────────────────────

    def book(self, guest: str, check_in: int, check_out: int,
             room_type: RoomType | None = None) -> int | tuple[int, float]:
        """Book a room for a guest.

        Returns:
            Level 1-2: booking_id (int)
            Level 3+: (booking_id, total_cost)
        """
        pass

    def cancel(self, booking_id: int) -> None:
        """Cancel a booking by ID."""
        pass

    # ── Level 2 ────────────────────────────────────────────────────

    def get_availability(self, room_type: RoomType,
                         check_in: int, check_out: int) -> list[int]:
        """Return sorted list of available room IDs for the given type and dates."""
        pass

    # ── Level 3 ────────────────────────────────────────────────────

    def set_season(self, name: str, start: int, end: int,
                   multiplier: float) -> None:
        """Define a pricing season with a multiplier."""
        pass

    def get_loyalty_points(self, guest: str) -> int:
        """Return accumulated loyalty points for a guest."""
        pass

    # ── Level 4 ────────────────────────────────────────────────────

    def set_overbooking_ratio(self, ratio: float) -> None:
        """Set the overbooking ratio (e.g., 1.1 for 110% capacity)."""
        pass

    def waitlist(self, guest: str, check_in: int, check_out: int,
                 room_type: RoomType) -> int:
        """Add guest to waitlist, return position (1-indexed)."""
        pass

    def upgrade(self, booking_id: int) -> int:
        """Upgrade booking to next room tier, return new room ID."""
        pass

    def revenue_report(self, start: int, end: int) -> dict:
        """Revenue breakdown by room type for bookings in [start, end)."""
        pass
