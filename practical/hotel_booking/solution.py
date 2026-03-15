"""Hotel Booking System — Reference Solution (all levels)."""

from __future__ import annotations

import math
from enum import Enum
from dataclasses import dataclass, field


class RoomType(Enum):
    SINGLE = "single"
    DOUBLE = "double"
    SUITE = "suite"


_BASE_RATES: dict[RoomType, float] = {
    RoomType.SINGLE: 100.0,
    RoomType.DOUBLE: 200.0,
    RoomType.SUITE: 500.0,
}

_UPGRADE_PATH: dict[RoomType, RoomType] = {
    RoomType.SINGLE: RoomType.DOUBLE,
    RoomType.DOUBLE: RoomType.SUITE,
}


@dataclass
class Booking:
    booking_id: int
    guest: str
    room_id: int
    room_type: RoomType
    check_in: int
    check_out: int
    cost: float
    active: bool = True


class Hotel:
    def __init__(self, rooms: list[int] | dict[RoomType, list[int]]) -> None:
        if isinstance(rooms, list):
            self._rooms: dict[RoomType, list[int]] = {RoomType.SINGLE: sorted(rooms)}
        else:
            self._rooms = {rt: sorted(ids) for rt, ids in rooms.items()}

        self._room_type_map: dict[int, RoomType] = {}
        for rt, ids in self._rooms.items():
            for rid in ids:
                self._room_type_map[rid] = rt

        self._bookings: dict[int, Booking] = {}
        self._next_booking_id: int = 1
        self._loyalty: dict[str, int] = {}

        # Level 3: seasons
        self._seasons: list[dict] = []

        # Level 4
        self._overbooking_ratio: float = 1.0
        self._waitlists: dict[RoomType, list[dict]] = {rt: [] for rt in RoomType}

    # ── Level 1–3: book ───────────────────────────────────────────

    def book(self, guest: str, check_in: int, check_out: int,
             room_type: RoomType | None = None) -> int | tuple[int, float]:
        if room_type is None:
            room_type = RoomType.SINGLE

        room_id = self._find_available_room(room_type, check_in, check_out)
        if room_id is None:
            raise ValueError("No rooms available for the requested dates")

        cost = self._calculate_cost(room_type, check_in, check_out)
        bid = self._next_booking_id
        self._next_booking_id += 1

        self._bookings[bid] = Booking(
            booking_id=bid, guest=guest, room_id=room_id,
            room_type=room_type, check_in=check_in, check_out=check_out,
            cost=cost,
        )

        # Loyalty points: 10 per dollar
        self._loyalty[guest] = self._loyalty.get(guest, 0) + int(cost * 10)

        if self._seasons:
            return bid, cost
        return bid

    def cancel(self, booking_id: int) -> None:
        if booking_id not in self._bookings or not self._bookings[booking_id].active:
            raise ValueError(f"Invalid booking ID: {booking_id}")
        self._bookings[booking_id].active = False

        # Level 4: auto-assign from waitlist
        b = self._bookings[booking_id]
        self._process_waitlist(b.room_type)

    # ── Level 2: availability ─────────────────────────────────────

    def get_availability(self, room_type: RoomType,
                         check_in: int, check_out: int) -> list[int]:
        result = []
        for rid in self._rooms.get(room_type, []):
            if self._is_room_available(rid, check_in, check_out):
                result.append(rid)
        return sorted(result)

    # ── Level 3: pricing and loyalty ──────────────────────────────

    def set_season(self, name: str, start: int, end: int,
                   multiplier: float) -> None:
        self._seasons.append({
            "name": name, "start": start, "end": end, "multiplier": multiplier,
        })

    def get_loyalty_points(self, guest: str) -> int:
        return self._loyalty.get(guest, 0)

    # ── Level 4 ───────────────────────────────────────────────────

    def set_overbooking_ratio(self, ratio: float) -> None:
        self._overbooking_ratio = ratio

    def waitlist(self, guest: str, check_in: int, check_out: int,
                 room_type: RoomType) -> int:
        entry = {"guest": guest, "check_in": check_in,
                 "check_out": check_out, "room_type": room_type}
        self._waitlists[room_type].append(entry)
        return len(self._waitlists[room_type])

    def upgrade(self, booking_id: int) -> int:
        if booking_id not in self._bookings or not self._bookings[booking_id].active:
            raise ValueError(f"Invalid booking ID: {booking_id}")

        b = self._bookings[booking_id]
        if b.room_type not in _UPGRADE_PATH:
            raise ValueError("Cannot upgrade from SUITE")

        new_type = _UPGRADE_PATH[b.room_type]
        new_room = self._find_available_room(new_type, b.check_in, b.check_out)
        if new_room is None:
            raise ValueError(f"No {new_type.value} rooms available for upgrade")

        # Update booking
        b.room_type = new_type
        b.room_id = new_room
        return new_room

    def revenue_report(self, start: int, end: int) -> dict:
        report: dict[str, float] = {rt.value.upper(): 0.0 for rt in RoomType}
        report["total"] = 0.0

        for b in self._bookings.values():
            if b.active and start <= b.check_in < end:
                key = b.room_type.value.upper()
                report[key] += b.cost
                report["total"] += b.cost

        return report

    # ── Internals ─────────────────────────────────────────────────

    def _find_available_room(self, room_type: RoomType,
                             check_in: int, check_out: int) -> int | None:
        for rid in self._rooms.get(room_type, []):
            if self._is_room_available(rid, check_in, check_out):
                return rid

        # Level 4: overbooking check
        if self._overbooking_ratio > 1.0:
            max_bookings = math.ceil(
                len(self._rooms.get(room_type, [])) * self._overbooking_ratio
            )
            for day in range(check_in, check_out):
                count = sum(
                    1 for b in self._bookings.values()
                    if b.active and b.room_type == room_type
                    and b.check_in <= day < b.check_out
                )
                if count >= max_bookings:
                    return None
            # Overbooking: assign a virtual room (reuse lowest room id)
            if self._rooms.get(room_type):
                return self._rooms[room_type][0]

        return None

    def _is_room_available(self, room_id: int,
                           check_in: int, check_out: int) -> bool:
        for b in self._bookings.values():
            if not b.active:
                continue
            if b.room_id == room_id:
                if not (check_out <= b.check_in or b.check_out <= check_in):
                    return False
        return True

    def _calculate_cost(self, room_type: RoomType,
                        check_in: int, check_out: int) -> float:
        base = _BASE_RATES[room_type]
        total = 0.0
        for day in range(check_in, check_out):
            multiplier = self._get_season_multiplier(day)
            total += base * multiplier
        return total

    def _get_season_multiplier(self, day: int) -> float:
        max_mult = 1.0
        for s in self._seasons:
            if s["start"] <= day < s["end"]:
                max_mult = max(max_mult, s["multiplier"])
        return max_mult

    def _process_waitlist(self, room_type: RoomType) -> None:
        remaining = []
        for entry in self._waitlists[room_type]:
            room_id = self._find_available_room(
                entry["room_type"], entry["check_in"], entry["check_out"]
            )
            if room_id is not None:
                cost = self._calculate_cost(
                    entry["room_type"], entry["check_in"], entry["check_out"]
                )
                bid = self._next_booking_id
                self._next_booking_id += 1
                self._bookings[bid] = Booking(
                    booking_id=bid, guest=entry["guest"], room_id=room_id,
                    room_type=entry["room_type"], check_in=entry["check_in"],
                    check_out=entry["check_out"], cost=cost,
                )
                self._loyalty[entry["guest"]] = (
                    self._loyalty.get(entry["guest"], 0) + int(cost * 10)
                )
            else:
                remaining.append(entry)
        self._waitlists[room_type] = remaining
