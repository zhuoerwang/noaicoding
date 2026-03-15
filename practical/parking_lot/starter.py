"""Parking Lot System — ICF-Style System Design

Implement a parking lot management system across 4 progressive levels.
Each level builds on the previous without rewriting existing code.

Run tests by level:
    pytest test_parking_lot.py -k "TestLevel1"
    pytest test_parking_lot.py -k "TestLevel2"
    pytest test_parking_lot.py -k "TestLevel3"
    pytest test_parking_lot.py -k "TestLevel4"
"""

from __future__ import annotations

import math
from enum import Enum


# ── Enums (Level 2+) ──────────────────────────────────────────────

class VehicleType(Enum):
    MOTORCYCLE = "motorcycle"
    CAR = "car"
    TRUCK = "truck"


class SpotSize(Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


# ── Parking Lot ───────────────────────────────────────────────────

class ParkingLot:
    """A parking lot system supporting multiple vehicle types, fees,
    reservations, peak pricing, and analytics."""

    # Level 1: Basic constructor — ParkingLot(capacity: int)
    # Level 2: Extended constructor — ParkingLot(spots: dict[SpotSize, list[int]])
    def __init__(self, capacity_or_spots: int | dict[SpotSize, list[int]]) -> None:
        """Initialize the parking lot.

        Args:
            capacity_or_spots: Either an int (Level 1: number of spots 0..n-1)
                or a dict mapping SpotSize to list of spot IDs (Level 2+).
        """
        pass

    # ── Level 1 ────────────────────────────────────────────────────

    def park(self, vehicle_id: str, vehicle_type: VehicleType | None = None,
             timestamp: int | None = None) -> int:
        """Park a vehicle in the lot.

        Args:
            vehicle_id: Unique identifier for the vehicle.
            vehicle_type: Type of vehicle (Level 2+). Defaults to CAR.
            timestamp: Check-in time as epoch seconds (Level 3+).

        Returns:
            The spot ID where the vehicle was parked.

        Raises:
            ValueError: If the lot is full or no fitting spot is available.
        """
        pass

    def leave(self, spot_id: int, timestamp: int | None = None) -> str | tuple[str, float]:
        """Remove a vehicle from a spot.

        Args:
            spot_id: The spot to vacate.
            timestamp: Check-out time as epoch seconds (Level 3+).

        Returns:
            Level 1-2: The vehicle_id that was parked there.
            Level 3+: A tuple of (vehicle_id, fee).

        Raises:
            ValueError: If spot_id is invalid or the spot is empty.
        """
        pass

    # ── Level 3 ────────────────────────────────────────────────────

    def get_revenue(self) -> float:
        """Return total fees collected so far."""
        pass

    # ── Level 4 ────────────────────────────────────────────────────

    def reserve(self, vehicle_id: str, vehicle_type: VehicleType,
                start: int, end: int) -> int:
        """Reserve a spot for a future time window.

        Args:
            vehicle_id: Vehicle that will use the reservation.
            vehicle_type: Type of vehicle.
            start: Reservation start time (epoch seconds).
            end: Reservation end time (epoch seconds).

        Returns:
            Reservation ID (auto-increment from 1).

        Raises:
            ValueError: If no fitting spot is available for the window.
        """
        pass

    def cancel_reservation(self, reservation_id: int) -> None:
        """Cancel a reservation by its ID.

        Raises:
            ValueError: If reservation_id is invalid.
        """
        pass

    def set_peak_hours(self, start_hour: int, end_hour: int,
                       multiplier: float) -> None:
        """Set peak pricing for a range of hours (0–23).

        Args:
            start_hour: Start of peak period (inclusive).
            end_hour: End of peak period (exclusive).
            multiplier: Price multiplier during peak hours.
        """
        pass

    def spot_utilization(self) -> dict[int, float]:
        """Return hours each spot has been used (completed sessions only).

        Returns:
            Dict mapping spot_id to total hours occupied.
        """
        pass

    def revenue_by_type(self) -> dict[VehicleType, float]:
        """Return total revenue grouped by vehicle type.

        Returns:
            Dict mapping VehicleType to total revenue collected.
        """
        pass
