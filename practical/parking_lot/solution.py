"""Parking Lot System — Reference Solution (all levels)."""

from __future__ import annotations

import math
from enum import Enum


class VehicleType(Enum):
    MOTORCYCLE = "motorcycle"
    CAR = "car"
    TRUCK = "truck"


class SpotSize(Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


# Fitting rules: vehicle type → allowed spot sizes (in preference order)
_FIT_RULES: dict[VehicleType, list[SpotSize]] = {
    VehicleType.MOTORCYCLE: [SpotSize.SMALL, SpotSize.MEDIUM, SpotSize.LARGE],
    VehicleType.CAR: [SpotSize.MEDIUM, SpotSize.LARGE],
    VehicleType.TRUCK: [SpotSize.LARGE],
}

_HOURLY_RATES: dict[VehicleType, float] = {
    VehicleType.MOTORCYCLE: 1.0,
    VehicleType.CAR: 2.0,
    VehicleType.TRUCK: 3.0,
}


class ParkingLot:
    def __init__(self, capacity_or_spots: int | dict[SpotSize, list[int]]) -> None:
        # Normalize both constructor forms into a unified internal structure
        if isinstance(capacity_or_spots, int):
            capacity = capacity_or_spots
            self._spots: dict[int, SpotSize] = {
                i: SpotSize.MEDIUM for i in range(capacity)
            }
        else:
            self._spots = {}
            for size, ids in capacity_or_spots.items():
                for sid in ids:
                    self._spots[sid] = size

        # spot_id → (vehicle_id, vehicle_type, checkin_timestamp)
        self._occupied: dict[int, tuple[str, VehicleType, int | None]] = {}
        # vehicle_id → spot_id (for duplicate detection)
        self._vehicle_to_spot: dict[str, int] = {}

        # Level 3
        self._revenue: float = 0.0

        # Level 4
        self._reservations: dict[int, dict] = {}  # res_id → {vehicle_id, vehicle_type, spot_id, start, end}
        self._next_reservation_id: int = 1
        self._peak_start: int | None = None
        self._peak_end: int | None = None
        self._peak_multiplier: float = 1.0
        self._utilization: dict[int, float] = {}  # spot_id → total hours
        self._revenue_by_type: dict[VehicleType, float] = {}

    # ── Level 1–3: park ───────────────────────────────────────────

    def park(self, vehicle_id: str, vehicle_type: VehicleType | None = None,
             timestamp: int | None = None) -> int:
        if vehicle_type is None:
            vehicle_type = VehicleType.CAR

        if vehicle_id in self._vehicle_to_spot:
            raise ValueError(f"Vehicle {vehicle_id} is already parked")

        spot_id = self._find_spot(vehicle_type, timestamp)
        if spot_id is None:
            raise ValueError("No available spot for this vehicle type")

        self._occupied[spot_id] = (vehicle_id, vehicle_type, timestamp)
        self._vehicle_to_spot[vehicle_id] = spot_id
        return spot_id

    def leave(self, spot_id: int, timestamp: int | None = None) -> str | tuple[str, float]:
        if spot_id not in self._spots:
            raise ValueError(f"Invalid spot ID: {spot_id}")
        if spot_id not in self._occupied:
            raise ValueError(f"Spot {spot_id} is empty")

        vehicle_id, vehicle_type, checkin_ts = self._occupied.pop(spot_id)
        del self._vehicle_to_spot[vehicle_id]

        # Level 3: fee calculation
        if timestamp is not None and checkin_ts is not None:
            fee = self._calculate_fee(vehicle_type, checkin_ts, timestamp)
            self._revenue += fee

            # Level 4: analytics
            hours = (timestamp - checkin_ts) / 3600
            self._utilization[spot_id] = self._utilization.get(spot_id, 0.0) + hours
            self._revenue_by_type[vehicle_type] = (
                self._revenue_by_type.get(vehicle_type, 0.0) + fee
            )
            return vehicle_id, fee

        return vehicle_id

    # ── Level 3: revenue ──────────────────────────────────────────

    def get_revenue(self) -> float:
        return self._revenue

    # ── Level 4: reservations ─────────────────────────────────────

    def reserve(self, vehicle_id: str, vehicle_type: VehicleType,
                start: int, end: int) -> int:
        spot_id = self._find_spot(vehicle_type, start, end)
        if spot_id is None:
            raise ValueError("No available spot for reservation")

        res_id = self._next_reservation_id
        self._next_reservation_id += 1
        self._reservations[res_id] = {
            "vehicle_id": vehicle_id,
            "vehicle_type": vehicle_type,
            "spot_id": spot_id,
            "start": start,
            "end": end,
        }
        return res_id

    def cancel_reservation(self, reservation_id: int) -> None:
        if reservation_id not in self._reservations:
            raise ValueError(f"Invalid reservation ID: {reservation_id}")
        del self._reservations[reservation_id]

    def set_peak_hours(self, start_hour: int, end_hour: int,
                       multiplier: float) -> None:
        self._peak_start = start_hour
        self._peak_end = end_hour
        self._peak_multiplier = multiplier

    def spot_utilization(self) -> dict[int, float]:
        return dict(self._utilization)

    def revenue_by_type(self) -> dict[VehicleType, float]:
        return dict(self._revenue_by_type)

    # ── Internals ─────────────────────────────────────────────────

    def _find_spot(self, vehicle_type: VehicleType,
                   timestamp: int | None = None,
                   end_time: int | None = None) -> int | None:
        allowed_sizes = _FIT_RULES[vehicle_type]
        for size in allowed_sizes:
            candidates = sorted(
                sid for sid, s in self._spots.items()
                if s == size and sid not in self._occupied
            )
            for sid in candidates:
                if not self._is_reserved(sid, timestamp, end_time):
                    return sid
        return None

    def _is_reserved(self, spot_id: int,
                     start: int | None, end: int | None) -> bool:
        if start is None:
            return False
        for res in self._reservations.values():
            if res["spot_id"] != spot_id:
                continue
            # Overlap check: NOT (end1 <= start2 or end2 <= start1)
            res_start, res_end = res["start"], res["end"]
            check_end = end if end is not None else start + 1
            if not (check_end <= res_start or res_end <= start):
                return True
        return False

    def _calculate_fee(self, vehicle_type: VehicleType,
                       checkin: int, checkout: int) -> float:
        hours = math.ceil((checkout - checkin) / 3600)
        if hours < 1:
            hours = 1
        rate = _HOURLY_RATES[vehicle_type]
        multiplier = self._get_multiplier(checkin)
        return hours * rate * multiplier

    def _get_multiplier(self, timestamp: int) -> float:
        if self._peak_start is None:
            return 1.0
        hour_of_day = (timestamp % 86400) // 3600
        if self._peak_start <= hour_of_day < self._peak_end:
            return self._peak_multiplier
        return 1.0
