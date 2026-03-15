"""Parking Lot System — Tests by Level

Run all:       pytest test_parking_lot.py
Run by level:  pytest test_parking_lot.py -k "TestLevel1"
               pytest test_parking_lot.py -k "TestLevel2"
               pytest test_parking_lot.py -k "TestLevel3"
               pytest test_parking_lot.py -k "TestLevel4"
"""

import pytest

from solution import ParkingLot, VehicleType, SpotSize


# ── Level 1: Basic Parking ────────────────────────────────────────


class TestLevel1:
    def test_park_returns_lowest_spot(self):
        lot = ParkingLot(3)
        assert lot.park("A") == 0
        assert lot.park("B") == 1
        assert lot.park("C") == 2

    def test_leave_returns_vehicle_id(self):
        lot = ParkingLot(2)
        lot.park("A")
        assert lot.leave(0) == "A"

    def test_freed_spot_is_reused(self):
        lot = ParkingLot(2)
        lot.park("A")
        lot.park("B")
        lot.leave(0)
        assert lot.park("C") == 0

    def test_park_full_lot_raises(self):
        lot = ParkingLot(1)
        lot.park("A")
        with pytest.raises(ValueError):
            lot.park("B")

    def test_leave_invalid_spot_raises(self):
        lot = ParkingLot(2)
        with pytest.raises(ValueError):
            lot.leave(5)

    def test_leave_empty_spot_raises(self):
        lot = ParkingLot(2)
        with pytest.raises(ValueError):
            lot.leave(0)

    def test_park_duplicate_vehicle_raises(self):
        lot = ParkingLot(3)
        lot.park("A")
        with pytest.raises(ValueError):
            lot.park("A")

    def test_park_after_leave_same_vehicle(self):
        lot = ParkingLot(1)
        lot.park("A")
        lot.leave(0)
        assert lot.park("A") == 0

    def test_capacity_one(self):
        lot = ParkingLot(1)
        assert lot.park("X") == 0
        lot.leave(0)
        assert lot.park("Y") == 0

    def test_lowest_spot_priority(self):
        lot = ParkingLot(5)
        lot.park("A")  # 0
        lot.park("B")  # 1
        lot.park("C")  # 2
        lot.leave(1)
        lot.leave(0)
        # Spot 0 should be assigned first (lowest available)
        assert lot.park("D") == 0
        assert lot.park("E") == 1


# ── Level 2: Vehicle Types and Spot Sizes ─────────────────────────


class TestLevel2:
    def _make_lot(self):
        return ParkingLot({
            SpotSize.SMALL: [0, 1],
            SpotSize.MEDIUM: [2, 3],
            SpotSize.LARGE: [4, 5],
        })

    def test_motorcycle_gets_small_spot(self):
        lot = self._make_lot()
        assert lot.park("M1", VehicleType.MOTORCYCLE) == 0

    def test_car_gets_medium_spot(self):
        lot = self._make_lot()
        assert lot.park("C1", VehicleType.CAR) == 2

    def test_truck_gets_large_spot(self):
        lot = self._make_lot()
        assert lot.park("T1", VehicleType.TRUCK) == 4

    def test_motorcycle_overflow_to_medium(self):
        lot = self._make_lot()
        lot.park("M1", VehicleType.MOTORCYCLE)  # small 0
        lot.park("M2", VehicleType.MOTORCYCLE)  # small 1
        assert lot.park("M3", VehicleType.MOTORCYCLE) == 2  # medium

    def test_car_overflow_to_large(self):
        lot = self._make_lot()
        lot.park("C1", VehicleType.CAR)  # medium 2
        lot.park("C2", VehicleType.CAR)  # medium 3
        assert lot.park("C3", VehicleType.CAR) == 4  # large

    def test_truck_no_spot_raises(self):
        lot = self._make_lot()
        lot.park("T1", VehicleType.TRUCK)  # large 4
        lot.park("T2", VehicleType.TRUCK)  # large 5
        with pytest.raises(ValueError):
            lot.park("T3", VehicleType.TRUCK)

    def test_car_cannot_fit_small(self):
        lot = ParkingLot({SpotSize.SMALL: [0, 1]})
        with pytest.raises(ValueError):
            lot.park("C1", VehicleType.CAR)

    def test_mixed_parking_order(self):
        lot = self._make_lot()
        lot.park("T1", VehicleType.TRUCK)        # large 4
        lot.park("C1", VehicleType.CAR)           # medium 2
        lot.park("M1", VehicleType.MOTORCYCLE)    # small 0
        lot.park("M2", VehicleType.MOTORCYCLE)    # small 1
        lot.park("C2", VehicleType.CAR)           # medium 3
        lot.park("M3", VehicleType.MOTORCYCLE)    # overflow → large 5
        assert lot.leave(5) == "M3"

    def test_leave_frees_spot_for_correct_type(self):
        lot = self._make_lot()
        lot.park("C1", VehicleType.CAR)   # medium 2
        lot.park("C2", VehicleType.CAR)   # medium 3
        lot.leave(2)
        assert lot.park("C3", VehicleType.CAR) == 2

    def test_lowest_id_within_size(self):
        lot = ParkingLot({SpotSize.MEDIUM: [5, 2, 8]})
        assert lot.park("C1", VehicleType.CAR) == 2
        assert lot.park("C2", VehicleType.CAR) == 5
        assert lot.park("C3", VehicleType.CAR) == 8


# ── Level 3: Fee Calculation ──────────────────────────────────────


class TestLevel3:
    def _make_lot(self):
        return ParkingLot({
            SpotSize.SMALL: [0, 1],
            SpotSize.MEDIUM: [2, 3],
            SpotSize.LARGE: [4, 5],
        })

    def test_car_one_hour(self):
        lot = self._make_lot()
        lot.park("C1", VehicleType.CAR, timestamp=0)
        vid, fee = lot.leave(2, timestamp=3600)
        assert vid == "C1"
        assert fee == 2.0

    def test_car_partial_hour_rounds_up(self):
        lot = self._make_lot()
        lot.park("C1", VehicleType.CAR, timestamp=0)
        _, fee = lot.leave(2, timestamp=5400)  # 1.5 hours → ceil = 2
        assert fee == 4.0

    def test_motorcycle_rate(self):
        lot = self._make_lot()
        lot.park("M1", VehicleType.MOTORCYCLE, timestamp=0)
        _, fee = lot.leave(0, timestamp=7200)  # 2 hours
        assert fee == 2.0

    def test_truck_rate(self):
        lot = self._make_lot()
        lot.park("T1", VehicleType.TRUCK, timestamp=0)
        _, fee = lot.leave(4, timestamp=3600)  # 1 hour
        assert fee == 3.0

    def test_minimum_one_hour(self):
        lot = self._make_lot()
        lot.park("C1", VehicleType.CAR, timestamp=0)
        _, fee = lot.leave(2, timestamp=1)  # 1 second → ceil = 1 hour
        assert fee == 2.0

    def test_revenue_accumulates(self):
        lot = self._make_lot()
        lot.park("C1", VehicleType.CAR, timestamp=0)
        lot.leave(2, timestamp=3600)  # $2
        lot.park("C2", VehicleType.CAR, timestamp=0)
        lot.leave(2, timestamp=7200)  # $4
        assert lot.get_revenue() == 6.0

    def test_revenue_starts_at_zero(self):
        lot = self._make_lot()
        assert lot.get_revenue() == 0.0

    def test_multi_type_revenue(self):
        lot = self._make_lot()
        lot.park("M1", VehicleType.MOTORCYCLE, timestamp=0)
        lot.leave(0, timestamp=3600)   # $1
        lot.park("C1", VehicleType.CAR, timestamp=0)
        lot.leave(2, timestamp=3600)   # $2
        lot.park("T1", VehicleType.TRUCK, timestamp=0)
        lot.leave(4, timestamp=3600)   # $3
        assert lot.get_revenue() == 6.0

    def test_long_stay(self):
        lot = self._make_lot()
        lot.park("C1", VehicleType.CAR, timestamp=0)
        _, fee = lot.leave(2, timestamp=86400)  # 24 hours
        assert fee == 48.0


# ── Level 4: Reservations, Peak Pricing, Analytics ────────────────


class TestLevel4:
    def _make_lot(self):
        return ParkingLot({
            SpotSize.SMALL: [0, 1],
            SpotSize.MEDIUM: [2, 3],
            SpotSize.LARGE: [4, 5],
        })

    def test_reserve_returns_id(self):
        lot = self._make_lot()
        res_id = lot.reserve("C1", VehicleType.CAR, 0, 3600)
        assert res_id == 1

    def test_reserve_blocks_park(self):
        lot = ParkingLot({SpotSize.MEDIUM: [2]})
        lot.reserve("C1", VehicleType.CAR, 0, 7200)
        with pytest.raises(ValueError):
            lot.park("C2", VehicleType.CAR, timestamp=1000)

    def test_reserve_non_overlapping_ok(self):
        lot = ParkingLot({SpotSize.MEDIUM: [2]})
        lot.reserve("C1", VehicleType.CAR, 0, 3600)
        # After reservation ends, parking should work
        assert lot.park("C2", VehicleType.CAR, timestamp=3600) == 2

    def test_cancel_reservation(self):
        lot = ParkingLot({SpotSize.MEDIUM: [2]})
        res_id = lot.reserve("C1", VehicleType.CAR, 0, 7200)
        lot.cancel_reservation(res_id)
        assert lot.park("C2", VehicleType.CAR, timestamp=1000) == 2

    def test_cancel_invalid_raises(self):
        lot = self._make_lot()
        with pytest.raises(ValueError):
            lot.cancel_reservation(999)

    def test_peak_pricing(self):
        lot = self._make_lot()
        lot.set_peak_hours(9, 17, 1.5)
        # Park at 10:00 AM (36000 seconds from epoch)
        lot.park("C1", VehicleType.CAR, timestamp=36000)
        _, fee = lot.leave(2, timestamp=39600)  # 1 hour
        assert fee == 3.0  # $2 * 1.5

    def test_off_peak_pricing(self):
        lot = self._make_lot()
        lot.set_peak_hours(9, 17, 1.5)
        # Park at 8:00 PM (72000 seconds)
        lot.park("C1", VehicleType.CAR, timestamp=72000)
        _, fee = lot.leave(2, timestamp=75600)  # 1 hour
        assert fee == 2.0  # no multiplier

    def test_spot_utilization(self):
        lot = self._make_lot()
        lot.park("C1", VehicleType.CAR, timestamp=0)
        lot.leave(2, timestamp=7200)  # 2 hours on spot 2
        util = lot.spot_utilization()
        assert util[2] == pytest.approx(2.0)

    def test_revenue_by_type(self):
        lot = self._make_lot()
        lot.park("M1", VehicleType.MOTORCYCLE, timestamp=0)
        lot.leave(0, timestamp=3600)  # $1
        lot.park("C1", VehicleType.CAR, timestamp=0)
        lot.leave(2, timestamp=3600)  # $2
        rev = lot.revenue_by_type()
        assert rev[VehicleType.MOTORCYCLE] == 1.0
        assert rev[VehicleType.CAR] == 2.0

    def test_multiple_reservations_same_spot_no_overlap(self):
        lot = ParkingLot({SpotSize.MEDIUM: [2]})
        r1 = lot.reserve("C1", VehicleType.CAR, 0, 3600)
        r2 = lot.reserve("C2", VehicleType.CAR, 3600, 7200)
        assert r1 == 1
        assert r2 == 2

    def test_reservation_auto_increment(self):
        lot = self._make_lot()
        r1 = lot.reserve("C1", VehicleType.CAR, 0, 3600)
        r2 = lot.reserve("C2", VehicleType.CAR, 0, 3600)
        assert r1 == 1
        assert r2 == 2

    def test_utilization_accumulates(self):
        lot = self._make_lot()
        lot.park("C1", VehicleType.CAR, timestamp=0)
        lot.leave(2, timestamp=3600)   # 1 hour
        lot.park("C2", VehicleType.CAR, timestamp=3600)
        lot.leave(2, timestamp=7200)   # 1 hour
        util = lot.spot_utilization()
        assert util[2] == pytest.approx(2.0)