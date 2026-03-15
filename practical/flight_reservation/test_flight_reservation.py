"""Flight Reservation System — Tests by Level

Run all:       pytest test_flight_reservation.py
Run by level:  pytest test_flight_reservation.py -k "TestLevel1"
               pytest test_flight_reservation.py -k "TestLevel2"
               pytest test_flight_reservation.py -k "TestLevel3"
               pytest test_flight_reservation.py -k "TestLevel4"
"""

import pytest

from solution import Flight, FlightSystem, SeatClass


# ── Level 1: Basic Reservation ────────────────────────────────────


class TestLevel1:
    def test_reserve_returns_id(self):
        f = Flight("UA100", 5)
        assert f.reserve("Alice", 0) == 1

    def test_reserve_auto_increments(self):
        f = Flight("UA100", 5)
        assert f.reserve("Alice", 0) == 1
        assert f.reserve("Bob", 1) == 2

    def test_reserve_invalid_seat_raises(self):
        f = Flight("UA100", 3)
        with pytest.raises(ValueError):
            f.reserve("Alice", 5)

    def test_reserve_taken_seat_raises(self):
        f = Flight("UA100", 3)
        f.reserve("Alice", 0)
        with pytest.raises(ValueError):
            f.reserve("Bob", 0)

    def test_cancel_frees_seat(self):
        f = Flight("UA100", 3)
        f.reserve("Alice", 0)
        f.cancel(1)
        assert 0 in f.get_available_seats()

    def test_cancel_invalid_raises(self):
        f = Flight("UA100", 3)
        with pytest.raises(ValueError):
            f.cancel(999)

    def test_get_available_seats(self):
        f = Flight("UA100", 5)
        f.reserve("Alice", 1)
        f.reserve("Bob", 3)
        assert f.get_available_seats() == [0, 2, 4]

    def test_all_seats_available_initially(self):
        f = Flight("UA100", 3)
        assert f.get_available_seats() == [0, 1, 2]

    def test_same_passenger_multiple_seats(self):
        f = Flight("UA100", 5)
        f.reserve("Alice", 0)
        f.reserve("Alice", 1)
        assert f.get_available_seats() == [2, 3, 4]

    def test_cancel_then_rebook(self):
        f = Flight("UA100", 1)
        f.reserve("Alice", 0)
        f.cancel(1)
        assert f.reserve("Bob", 0) == 2


# ── Level 2: Seat Classes ────────────────────────────────────────


class TestLevel2:
    def _make_flight(self):
        return Flight("UA100", {
            SeatClass.ECONOMY: [0, 1, 2, 3],
            SeatClass.BUSINESS: [10, 11],
            SeatClass.FIRST: [20],
        })

    def test_reserve_by_class(self):
        f = self._make_flight()
        rid, fare = f.reserve("Alice", SeatClass.ECONOMY)
        assert rid == 1

    def test_assigns_lowest_seat_in_class(self):
        f = self._make_flight()
        f.reserve("Alice", SeatClass.ECONOMY)  # seat 0
        f.reserve("Bob", SeatClass.ECONOMY)    # seat 1
        avail = f.get_availability(SeatClass.ECONOMY)
        assert avail == [2, 3]

    def test_get_availability(self):
        f = self._make_flight()
        assert f.get_availability(SeatClass.BUSINESS) == [10, 11]

    def test_class_full_raises(self):
        f = self._make_flight()
        f.reserve("Alice", SeatClass.FIRST)
        with pytest.raises(ValueError):
            f.reserve("Bob", SeatClass.FIRST)

    def test_cancel_restores_class_availability(self):
        f = self._make_flight()
        rid, _ = f.reserve("Alice", SeatClass.FIRST)
        f.cancel(rid)
        assert f.get_availability(SeatClass.FIRST) == [20]

    def test_different_classes_independent(self):
        f = self._make_flight()
        f.reserve("Alice", SeatClass.FIRST)
        assert len(f.get_availability(SeatClass.ECONOMY)) == 4

    def test_get_available_seats_all_classes(self):
        f = self._make_flight()
        f.reserve("Alice", SeatClass.BUSINESS)
        avail = f.get_available_seats()
        assert avail == [0, 1, 2, 3, 11, 20]

    def test_reserve_returns_fare(self):
        f = self._make_flight()
        _, fare = f.reserve("Alice", SeatClass.ECONOMY)
        assert fare == 200.0


# ── Level 3: Fares and Upgrades ──────────────────────────────────


class TestLevel3:
    def _make_flight(self):
        return Flight("UA100", {
            SeatClass.ECONOMY: [0, 1, 2, 3],
            SeatClass.BUSINESS: [10, 11],
            SeatClass.FIRST: [20],
        })

    def test_economy_fare(self):
        f = self._make_flight()
        _, fare = f.reserve("Alice", SeatClass.ECONOMY)
        assert fare == 200.0

    def test_business_fare(self):
        f = self._make_flight()
        _, fare = f.reserve("Alice", SeatClass.BUSINESS)
        assert fare == 500.0

    def test_first_fare(self):
        f = self._make_flight()
        _, fare = f.reserve("Alice", SeatClass.FIRST)
        assert fare == 1000.0

    def test_add_baggage_first_free(self):
        f = self._make_flight()
        rid, _ = f.reserve("Alice", SeatClass.ECONOMY)
        total = f.add_baggage(rid)
        assert total == 200.0  # first bag free

    def test_add_baggage_second_costs(self):
        f = self._make_flight()
        rid, _ = f.reserve("Alice", SeatClass.ECONOMY)
        f.add_baggage(rid)
        total = f.add_baggage(rid)
        assert total == 230.0  # $200 + $30

    def test_add_baggage_third_costs(self):
        f = self._make_flight()
        rid, _ = f.reserve("Alice", SeatClass.ECONOMY)
        f.add_baggage(rid)
        f.add_baggage(rid)
        total = f.add_baggage(rid)
        assert total == 260.0  # $200 + $60

    def test_add_baggage_max_raises(self):
        f = self._make_flight()
        rid, _ = f.reserve("Alice", SeatClass.ECONOMY)
        f.add_baggage(rid)
        f.add_baggage(rid)
        f.add_baggage(rid)
        with pytest.raises(ValueError):
            f.add_baggage(rid)

    def test_upgrade_economy_to_business(self):
        f = self._make_flight()
        rid, _ = f.reserve("Alice", SeatClass.ECONOMY)
        new_seat, cost = f.request_upgrade(rid, SeatClass.BUSINESS)
        assert new_seat == 10
        assert cost == 300.0

    def test_upgrade_frees_old_seat(self):
        f = self._make_flight()
        rid, _ = f.reserve("Alice", SeatClass.ECONOMY)
        f.request_upgrade(rid, SeatClass.BUSINESS)
        assert 0 in f.get_availability(SeatClass.ECONOMY)

    def test_upgrade_to_lower_raises(self):
        f = self._make_flight()
        rid, _ = f.reserve("Alice", SeatClass.BUSINESS)
        with pytest.raises(ValueError):
            f.request_upgrade(rid, SeatClass.ECONOMY)

    def test_upgrade_no_availability_raises(self):
        f = self._make_flight()
        f.reserve("X", SeatClass.FIRST)
        rid, _ = f.reserve("Alice", SeatClass.ECONOMY)
        with pytest.raises(ValueError):
            f.request_upgrade(rid, SeatClass.FIRST)

    def test_get_total_cost(self):
        f = self._make_flight()
        rid, _ = f.reserve("Alice", SeatClass.ECONOMY)
        f.add_baggage(rid)
        f.add_baggage(rid)
        assert f.get_total_cost(rid) == 230.0


# ── Level 4: Multi-Leg FlightSystem ──────────────────────────────


class TestLevel4:
    def _make_system(self):
        system = FlightSystem()
        f1 = Flight("UA100", {
            SeatClass.ECONOMY: [0, 1, 2],
            SeatClass.BUSINESS: [10, 11],
            SeatClass.FIRST: [20],
        })
        f2 = Flight("UA200", {
            SeatClass.ECONOMY: [0, 1],
            SeatClass.BUSINESS: [10],
            SeatClass.FIRST: [20],
        })
        system.add_flight(f1)
        system.add_flight(f2)
        return system

    def test_book_connection_returns_pnr(self):
        system = self._make_system()
        pnr = system.book_connection("Alice", [
            ("UA100", SeatClass.ECONOMY),
            ("UA200", SeatClass.BUSINESS),
        ])
        assert pnr == "PNR-1"

    def test_pnr_auto_increments(self):
        system = self._make_system()
        pnr1 = system.book_connection("Alice", [("UA100", SeatClass.ECONOMY)])
        pnr2 = system.book_connection("Bob", [("UA100", SeatClass.ECONOMY)])
        assert pnr1 == "PNR-1"
        assert pnr2 == "PNR-2"

    def test_get_itinerary(self):
        system = self._make_system()
        pnr = system.book_connection("Alice", [
            ("UA100", SeatClass.ECONOMY),
            ("UA200", SeatClass.FIRST),
        ])
        itin = system.get_itinerary(pnr)
        assert len(itin) == 2
        assert itin[0]["flight_id"] == "UA100"
        assert itin[0]["seat_class"] == SeatClass.ECONOMY
        assert itin[1]["flight_id"] == "UA200"
        assert itin[1]["fare"] == 1000.0

    def test_cancel_pnr(self):
        system = self._make_system()
        pnr = system.book_connection("Alice", [
            ("UA100", SeatClass.FIRST),
            ("UA200", SeatClass.FIRST),
        ])
        system.cancel_pnr(pnr)
        # Seats should be free again
        f1 = system._flights["UA100"]
        assert 20 in f1.get_availability(SeatClass.FIRST)

    def test_cancel_invalid_pnr_raises(self):
        system = self._make_system()
        with pytest.raises(ValueError):
            system.cancel_pnr("PNR-999")

    def test_atomic_booking_rollback(self):
        system = self._make_system()
        # Book all FIRST seats on UA200
        system.book_connection("X", [("UA200", SeatClass.FIRST)])
        # Now try connection that includes UA200 FIRST — should fail
        with pytest.raises(ValueError):
            system.book_connection("Alice", [
                ("UA100", SeatClass.ECONOMY),
                ("UA200", SeatClass.FIRST),
            ])
        # UA100 economy should not have been consumed
        f1 = system._flights["UA100"]
        assert 0 in f1.get_availability(SeatClass.ECONOMY)

    def test_invalid_flight_raises(self):
        system = self._make_system()
        with pytest.raises(ValueError):
            system.book_connection("Alice", [("FAKE", SeatClass.ECONOMY)])

    def test_get_itinerary_invalid_pnr_raises(self):
        system = self._make_system()
        with pytest.raises(ValueError):
            system.get_itinerary("PNR-999")

    def test_single_leg_connection(self):
        system = self._make_system()
        pnr = system.book_connection("Alice", [("UA100", SeatClass.BUSINESS)])
        itin = system.get_itinerary(pnr)
        assert len(itin) == 1
        assert itin[0]["seat_id"] == 10

    def test_multiple_passengers_same_flights(self):
        system = self._make_system()
        system.book_connection("Alice", [("UA100", SeatClass.ECONOMY)])
        system.book_connection("Bob", [("UA100", SeatClass.ECONOMY)])
        f1 = system._flights["UA100"]
        assert f1.get_availability(SeatClass.ECONOMY) == [2]
