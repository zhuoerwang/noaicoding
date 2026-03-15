"""Flight Reservation System — ICF-Style System Design

Implement a flight reservation system across 4 progressive levels.

Run tests by level:
    pytest test_flight_reservation.py -k "TestLevel1"
    pytest test_flight_reservation.py -k "TestLevel2"
    pytest test_flight_reservation.py -k "TestLevel3"
    pytest test_flight_reservation.py -k "TestLevel4"
"""

from __future__ import annotations

from enum import Enum


class SeatClass(Enum):
    ECONOMY = "economy"
    BUSINESS = "business"
    FIRST = "first"


class Flight:
    """A single flight with seat management, fares, and upgrades."""

    # Level 1: Flight(flight_id: str, total_seats: int)
    # Level 2: Flight(flight_id: str, seats: dict[SeatClass, list[int]])
    def __init__(self, flight_id: str,
                 seats: int | dict[SeatClass, list[int]]) -> None:
        """Initialize a flight.

        Args:
            flight_id: Unique flight identifier.
            seats: Either total seat count (Level 1) or dict mapping
                SeatClass to list of seat IDs (Level 2+).
        """
        pass

    # ── Level 1 ────────────────────────────────────────────────────

    def reserve(self, passenger: str,
                seat_or_class: int | SeatClass) -> int | tuple[int, float]:
        """Reserve a seat.

        Args:
            passenger: Passenger name.
            seat_or_class: Seat ID (Level 1) or SeatClass (Level 2+).

        Returns:
            Level 1-2: reservation_id
            Level 3+: (reservation_id, fare)
        """
        pass

    def cancel(self, reservation_id: int) -> None:
        """Cancel a reservation."""
        pass

    def get_available_seats(self) -> list[int]:
        """Return sorted list of all available seat IDs."""
        pass

    # ── Level 2 ────────────────────────────────────────────────────

    def get_availability(self, seat_class: SeatClass) -> list[int]:
        """Return sorted list of available seat IDs in the given class."""
        pass

    # ── Level 3 ────────────────────────────────────────────────────

    def add_baggage(self, reservation_id: int) -> float:
        """Add a bag to a reservation, return updated total cost."""
        pass

    def request_upgrade(self, reservation_id: int,
                        target_class: SeatClass) -> tuple[int, float]:
        """Upgrade to target class, return (new_seat_id, upgrade_cost)."""
        pass

    def get_total_cost(self, reservation_id: int) -> float:
        """Return total cost for a reservation (fare + baggage)."""
        pass


# ── Level 4 ────────────────────────────────────────────────────────


class FlightSystem:
    """Manages multiple flights and multi-leg bookings."""

    def __init__(self) -> None:
        pass

    def add_flight(self, flight: Flight) -> None:
        """Register a flight with the system."""
        pass

    def book_connection(self, passenger: str,
                        legs: list[tuple[str, SeatClass]]) -> str:
        """Book a multi-leg trip atomically, return PNR."""
        pass

    def cancel_pnr(self, pnr: str) -> None:
        """Cancel all reservations in a PNR."""
        pass

    def get_itinerary(self, pnr: str) -> list[dict]:
        """Return leg details for a PNR."""
        pass
