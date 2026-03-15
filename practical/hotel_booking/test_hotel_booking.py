"""Hotel Booking System — Tests by Level

Run all:       pytest test_hotel_booking.py
Run by level:  pytest test_hotel_booking.py -k "TestLevel1"
               pytest test_hotel_booking.py -k "TestLevel2"
               pytest test_hotel_booking.py -k "TestLevel3"
               pytest test_hotel_booking.py -k "TestLevel4"
"""

import pytest

from solution import Hotel, RoomType


# ── Level 1: Basic Booking ────────────────────────────────────────


class TestLevel1:
    def test_book_returns_id(self):
        hotel = Hotel([101, 102, 103])
        assert hotel.book("Alice", 1, 5) == 1

    def test_book_auto_increments(self):
        hotel = Hotel([101, 102])
        assert hotel.book("Alice", 1, 3) == 1
        assert hotel.book("Bob", 1, 3) == 2

    def test_book_assigns_lowest_room(self):
        hotel = Hotel([103, 101, 102])
        hotel.book("Alice", 1, 5)
        # Cancel and rebook to verify room 101 was assigned
        hotel.cancel(1)
        # Now all rooms free, should get 101 again
        assert hotel.book("Bob", 1, 5) == 2

    def test_book_no_overlap_same_room(self):
        hotel = Hotel([101])
        hotel.book("Alice", 1, 3)
        hotel.book("Bob", 3, 5)  # day 3-4, no overlap with 1-2

    def test_book_overlap_different_room(self):
        hotel = Hotel([101, 102])
        hotel.book("Alice", 1, 5)
        hotel.book("Bob", 3, 7)  # overlaps Alice, gets room 102

    def test_book_full_raises(self):
        hotel = Hotel([101])
        hotel.book("Alice", 1, 5)
        with pytest.raises(ValueError):
            hotel.book("Bob", 2, 4)

    def test_cancel_frees_room(self):
        hotel = Hotel([101])
        hotel.book("Alice", 1, 5)
        hotel.cancel(1)
        hotel.book("Bob", 1, 5)  # should succeed

    def test_cancel_invalid_raises(self):
        hotel = Hotel([101])
        with pytest.raises(ValueError):
            hotel.cancel(999)

    def test_cancel_twice_raises(self):
        hotel = Hotel([101])
        hotel.book("Alice", 1, 5)
        hotel.cancel(1)
        with pytest.raises(ValueError):
            hotel.cancel(1)

    def test_adjacent_bookings_no_overlap(self):
        hotel = Hotel([101])
        hotel.book("Alice", 1, 3)
        hotel.book("Bob", 3, 5)
        hotel.book("Carol", 5, 7)


# ── Level 2: Room Types and Availability ──────────────────────────


class TestLevel2:
    def _make_hotel(self):
        return Hotel({
            RoomType.SINGLE: [101, 102],
            RoomType.DOUBLE: [201, 202],
            RoomType.SUITE: [301],
        })

    def test_book_by_type(self):
        hotel = self._make_hotel()
        hotel.book("Alice", 1, 5, RoomType.DOUBLE)

    def test_book_assigns_lowest_of_type(self):
        hotel = self._make_hotel()
        hotel.book("Alice", 1, 5, RoomType.SINGLE)
        hotel.book("Bob", 1, 5, RoomType.SINGLE)
        # Both singles taken for days 1-4
        with pytest.raises(ValueError):
            hotel.book("Carol", 2, 4, RoomType.SINGLE)

    def test_availability_all_free(self):
        hotel = self._make_hotel()
        avail = hotel.get_availability(RoomType.SINGLE, 1, 5)
        assert avail == [101, 102]

    def test_availability_one_booked(self):
        hotel = self._make_hotel()
        hotel.book("Alice", 1, 5, RoomType.SINGLE)
        avail = hotel.get_availability(RoomType.SINGLE, 1, 5)
        assert avail == [102]

    def test_availability_none_available(self):
        hotel = self._make_hotel()
        hotel.book("Alice", 1, 5, RoomType.SUITE)
        avail = hotel.get_availability(RoomType.SUITE, 1, 5)
        assert avail == []

    def test_availability_non_overlapping_dates(self):
        hotel = self._make_hotel()
        hotel.book("Alice", 1, 3, RoomType.SINGLE)
        avail = hotel.get_availability(RoomType.SINGLE, 3, 5)
        assert avail == [101, 102]

    def test_different_types_independent(self):
        hotel = self._make_hotel()
        hotel.book("Alice", 1, 5, RoomType.SINGLE)
        hotel.book("Bob", 1, 5, RoomType.SINGLE)
        # Doubles should still be available
        avail = hotel.get_availability(RoomType.DOUBLE, 1, 5)
        assert avail == [201, 202]

    def test_book_wrong_type_full_raises(self):
        hotel = Hotel({RoomType.SUITE: [301]})
        hotel.book("Alice", 1, 5, RoomType.SUITE)
        with pytest.raises(ValueError):
            hotel.book("Bob", 1, 5, RoomType.SUITE)


# ── Level 3: Pricing and Loyalty ──────────────────────────────────


class TestLevel3:
    def _make_hotel(self):
        hotel = Hotel({
            RoomType.SINGLE: [101, 102],
            RoomType.DOUBLE: [201, 202],
            RoomType.SUITE: [301],
        })
        # Need at least one season to trigger cost return
        hotel.set_season("default", 1, 365, 1.0)
        return hotel

    def test_book_returns_cost(self):
        hotel = self._make_hotel()
        bid, cost = hotel.book("Alice", 1, 4, RoomType.SINGLE)
        assert bid == 1
        assert cost == 300.0  # 3 nights * $100

    def test_double_pricing(self):
        hotel = self._make_hotel()
        _, cost = hotel.book("Alice", 1, 3, RoomType.DOUBLE)
        assert cost == 400.0  # 2 nights * $200

    def test_suite_pricing(self):
        hotel = self._make_hotel()
        _, cost = hotel.book("Alice", 1, 2, RoomType.SUITE)
        assert cost == 500.0  # 1 night * $500

    def test_season_multiplier(self):
        hotel = Hotel({RoomType.SINGLE: [101]})
        hotel.set_season("peak", 10, 20, 2.0)
        _, cost = hotel.book("Alice", 10, 13, RoomType.SINGLE)
        assert cost == 600.0  # 3 nights * $100 * 2.0

    def test_mixed_season_nights(self):
        hotel = Hotel({RoomType.SINGLE: [101]})
        hotel.set_season("peak", 5, 7, 2.0)
        _, cost = hotel.book("Alice", 4, 8, RoomType.SINGLE)
        # day 4: $100*1.0, day 5: $100*2.0, day 6: $100*2.0, day 7: $100*1.0
        assert cost == 600.0

    def test_loyalty_points(self):
        hotel = self._make_hotel()
        hotel.book("Alice", 1, 3, RoomType.SINGLE)  # $200
        assert hotel.get_loyalty_points("Alice") == 2000  # 200 * 10

    def test_loyalty_accumulates(self):
        hotel = self._make_hotel()
        hotel.book("Alice", 1, 2, RoomType.SINGLE)   # $100
        hotel.book("Alice", 5, 6, RoomType.SINGLE)   # $100
        assert hotel.get_loyalty_points("Alice") == 2000

    def test_loyalty_zero_for_unknown_guest(self):
        hotel = self._make_hotel()
        assert hotel.get_loyalty_points("Nobody") == 0

    def test_highest_season_multiplier_wins(self):
        hotel = Hotel({RoomType.SINGLE: [101]})
        hotel.set_season("peak", 1, 10, 2.0)
        hotel.set_season("holiday", 5, 15, 3.0)
        _, cost = hotel.book("Alice", 5, 6, RoomType.SINGLE)
        assert cost == 300.0  # max(2.0, 3.0) = 3.0


# ── Level 4: Overbooking, Waitlist, Upgrades, Reports ─────────────


class TestLevel4:
    def _make_hotel(self):
        hotel = Hotel({
            RoomType.SINGLE: [101, 102],
            RoomType.DOUBLE: [201, 202],
            RoomType.SUITE: [301],
        })
        hotel.set_season("default", 1, 365, 1.0)
        return hotel

    def test_waitlist_returns_position(self):
        hotel = self._make_hotel()
        hotel.book("Alice", 1, 5, RoomType.SUITE)
        pos = hotel.waitlist("Bob", 1, 5, RoomType.SUITE)
        assert pos == 1

    def test_waitlist_auto_book_on_cancel(self):
        hotel = self._make_hotel()
        hotel.book("Alice", 1, 5, RoomType.SUITE)
        hotel.waitlist("Bob", 1, 5, RoomType.SUITE)
        hotel.cancel(1)  # Should auto-book Bob
        # Suite should now be taken by Bob
        avail = hotel.get_availability(RoomType.SUITE, 1, 5)
        assert avail == []

    def test_upgrade_single_to_double(self):
        hotel = self._make_hotel()
        hotel.book("Alice", 1, 5, RoomType.SINGLE)
        new_room = hotel.upgrade(1)
        assert new_room in [201, 202]

    def test_upgrade_suite_raises(self):
        hotel = self._make_hotel()
        hotel.book("Alice", 1, 5, RoomType.SUITE)
        with pytest.raises(ValueError):
            hotel.upgrade(1)

    def test_upgrade_no_availability_raises(self):
        hotel = self._make_hotel()
        hotel.book("Alice", 1, 5, RoomType.SINGLE)
        hotel.book("X", 1, 5, RoomType.DOUBLE)
        hotel.book("Y", 1, 5, RoomType.DOUBLE)
        with pytest.raises(ValueError):
            hotel.upgrade(1)

    def test_revenue_report(self):
        hotel = self._make_hotel()
        hotel.book("Alice", 1, 3, RoomType.SINGLE)  # $200
        hotel.book("Bob", 2, 4, RoomType.DOUBLE)     # $400
        report = hotel.revenue_report(1, 5)
        assert report["SINGLE"] == 200.0
        assert report["DOUBLE"] == 400.0
        assert report["total"] == 600.0

    def test_revenue_report_excludes_outside_range(self):
        hotel = self._make_hotel()
        hotel.book("Alice", 1, 3, RoomType.SINGLE)   # check_in=1, in range
        hotel.book("Bob", 10, 12, RoomType.SINGLE)    # check_in=10, out of range
        report = hotel.revenue_report(1, 5)
        assert report["SINGLE"] == 200.0
        assert report["total"] == 200.0

    def test_revenue_report_excludes_cancelled(self):
        hotel = self._make_hotel()
        hotel.book("Alice", 1, 3, RoomType.SINGLE)
        hotel.cancel(1)
        report = hotel.revenue_report(1, 5)
        assert report["total"] == 0.0

    def test_waitlist_multiple_positions(self):
        hotel = self._make_hotel()
        hotel.book("Alice", 1, 5, RoomType.SUITE)
        assert hotel.waitlist("Bob", 1, 5, RoomType.SUITE) == 1
        assert hotel.waitlist("Carol", 1, 5, RoomType.SUITE) == 2

    def test_upgrade_invalid_booking_raises(self):
        hotel = self._make_hotel()
        with pytest.raises(ValueError):
            hotel.upgrade(999)
