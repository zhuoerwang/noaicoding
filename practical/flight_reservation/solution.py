"""Flight Reservation System — Reference Solution (all levels)."""

from __future__ import annotations

from enum import Enum
from dataclasses import dataclass


class SeatClass(Enum):
    ECONOMY = "economy"
    BUSINESS = "business"
    FIRST = "first"


_BASE_FARES: dict[SeatClass, float] = {
    SeatClass.ECONOMY: 200.0,
    SeatClass.BUSINESS: 500.0,
    SeatClass.FIRST: 1000.0,
}

_CLASS_ORDER: list[SeatClass] = [SeatClass.ECONOMY, SeatClass.BUSINESS, SeatClass.FIRST]

_BAGGAGE_FEE: float = 30.0
_MAX_BAGS: int = 3


@dataclass
class Reservation:
    reservation_id: int
    passenger: str
    seat_id: int
    seat_class: SeatClass
    fare: float
    bags: int = 0
    active: bool = True

    @property
    def baggage_cost(self) -> float:
        return max(0, self.bags - 1) * _BAGGAGE_FEE

    @property
    def total_cost(self) -> float:
        return self.fare + self.baggage_cost


class Flight:
    def __init__(self, flight_id: str,
                 seats: int | dict[SeatClass, list[int]]) -> None:
        self.flight_id = flight_id

        if isinstance(seats, int):
            self._seats: dict[int, SeatClass] = {
                i: SeatClass.ECONOMY for i in range(seats)
            }
        else:
            self._seats = {}
            for sc, ids in seats.items():
                for sid in ids:
                    self._seats[sid] = sc

        self._reservations: dict[int, Reservation] = {}
        self._seat_to_res: dict[int, int] = {}  # seat_id → reservation_id
        self._next_res_id: int = 1
        self._has_classes: bool = not isinstance(seats, int)

    # ── Level 1–3: reserve ────────────────────────────────────────

    def reserve(self, passenger: str,
                seat_or_class: int | SeatClass) -> int | tuple[int, float]:
        if isinstance(seat_or_class, int):
            seat_id = seat_or_class
            if seat_id not in self._seats:
                raise ValueError(f"Invalid seat ID: {seat_id}")
            if seat_id in self._seat_to_res:
                raise ValueError(f"Seat {seat_id} is already taken")
            seat_class = self._seats[seat_id]
        else:
            seat_class = seat_or_class
            available = self.get_availability(seat_class)
            if not available:
                raise ValueError(f"No seats available in {seat_class.value}")
            seat_id = available[0]

        fare = _BASE_FARES[seat_class]
        rid = self._next_res_id
        self._next_res_id += 1

        self._reservations[rid] = Reservation(
            reservation_id=rid, passenger=passenger,
            seat_id=seat_id, seat_class=seat_class, fare=fare,
        )
        self._seat_to_res[seat_id] = rid

        if self._has_classes:
            return rid, fare
        return rid

    def cancel(self, reservation_id: int) -> None:
        if reservation_id not in self._reservations:
            raise ValueError(f"Invalid reservation ID: {reservation_id}")
        res = self._reservations[reservation_id]
        if not res.active:
            raise ValueError(f"Reservation {reservation_id} already cancelled")
        res.active = False
        del self._seat_to_res[res.seat_id]

    def get_available_seats(self) -> list[int]:
        return sorted(
            sid for sid in self._seats if sid not in self._seat_to_res
        )

    # ── Level 2: class availability ───────────────────────────────

    def get_availability(self, seat_class: SeatClass) -> list[int]:
        return sorted(
            sid for sid, sc in self._seats.items()
            if sc == seat_class and sid not in self._seat_to_res
        )

    # ── Level 3: baggage and upgrades ─────────────────────────────

    def add_baggage(self, reservation_id: int) -> float:
        res = self._get_active_reservation(reservation_id)
        if res.bags >= _MAX_BAGS:
            raise ValueError("Maximum baggage limit reached")
        res.bags += 1
        return res.total_cost

    def request_upgrade(self, reservation_id: int,
                        target_class: SeatClass) -> tuple[int, float]:
        res = self._get_active_reservation(reservation_id)

        current_idx = _CLASS_ORDER.index(res.seat_class)
        target_idx = _CLASS_ORDER.index(target_class)
        if target_idx <= current_idx:
            raise ValueError("Can only upgrade to a higher class")

        available = self.get_availability(target_class)
        if not available:
            raise ValueError(f"No seats available in {target_class.value}")

        new_seat = available[0]
        upgrade_cost = _BASE_FARES[target_class] - _BASE_FARES[res.seat_class]

        # Free old seat
        del self._seat_to_res[res.seat_id]
        # Assign new seat
        res.seat_id = new_seat
        res.seat_class = target_class
        res.fare = _BASE_FARES[target_class]
        self._seat_to_res[new_seat] = reservation_id

        return new_seat, upgrade_cost

    def get_total_cost(self, reservation_id: int) -> float:
        return self._get_active_reservation(reservation_id).total_cost

    def _get_active_reservation(self, reservation_id: int) -> Reservation:
        if reservation_id not in self._reservations:
            raise ValueError(f"Invalid reservation ID: {reservation_id}")
        res = self._reservations[reservation_id]
        if not res.active:
            raise ValueError(f"Reservation {reservation_id} is cancelled")
        return res


# ── Level 4: Multi-Leg FlightSystem ──────────────────────────────


class FlightSystem:
    def __init__(self) -> None:
        self._flights: dict[str, Flight] = {}
        self._pnrs: dict[str, list[tuple[str, int]]] = {}  # pnr → [(flight_id, res_id)]
        self._next_pnr: int = 1

    def add_flight(self, flight: Flight) -> None:
        self._flights[flight.flight_id] = flight

    def book_connection(self, passenger: str,
                        legs: list[tuple[str, SeatClass]]) -> str:
        if not legs:
            raise ValueError("At least one leg is required")

        booked: list[tuple[str, int]] = []
        try:
            for flight_id, seat_class in legs:
                if flight_id not in self._flights:
                    raise ValueError(f"Unknown flight: {flight_id}")
                flight = self._flights[flight_id]
                result = flight.reserve(passenger, seat_class)
                if isinstance(result, tuple):
                    rid = result[0]
                else:
                    rid = result
                booked.append((flight_id, rid))
        except (ValueError, Exception):
            # Rollback all booked legs
            for fid, rid in booked:
                self._flights[fid].cancel(rid)
            raise

        pnr = f"PNR-{self._next_pnr}"
        self._next_pnr += 1
        self._pnrs[pnr] = booked
        return pnr

    def cancel_pnr(self, pnr: str) -> None:
        if pnr not in self._pnrs:
            raise ValueError(f"Invalid PNR: {pnr}")
        for flight_id, rid in self._pnrs[pnr]:
            self._flights[flight_id].cancel(rid)
        del self._pnrs[pnr]

    def get_itinerary(self, pnr: str) -> list[dict]:
        if pnr not in self._pnrs:
            raise ValueError(f"Invalid PNR: {pnr}")
        itinerary = []
        for flight_id, rid in self._pnrs[pnr]:
            flight = self._flights[flight_id]
            res = flight._reservations[rid]
            itinerary.append({
                "flight_id": flight_id,
                "seat_id": res.seat_id,
                "seat_class": res.seat_class,
                "fare": res.fare,
            })
        return itinerary
