import pytest
from datetime import datetime, timezone
from solution import FlightSearch


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

DAY = 86400
HOUR = 3600

# A fixed base timestamp: Monday 2024-01-01 00:00:00 UTC
BASE = int(datetime(2024, 1, 1, tzinfo=timezone.utc).timestamp())


def make_fs_with_flights():
    """Return a FlightSearch preloaded with several flights."""
    fs = FlightSearch()
    # Same-day flights SFO -> JFK
    fs.add_flight("F1", "SFO", "JFK", BASE + 6 * HOUR, BASE + 12 * HOUR, 300.0)
    fs.add_flight("F2", "SFO", "JFK", BASE + 8 * HOUR, BASE + 14 * HOUR, 250.0)
    fs.add_flight("F3", "SFO", "JFK", BASE + 10 * HOUR, BASE + 16 * HOUR, 400.0)
    # Next-day flight
    fs.add_flight("F4", "SFO", "JFK", BASE + DAY + 7 * HOUR, BASE + DAY + 13 * HOUR, 280.0)
    # Different route
    fs.add_flight("F5", "JFK", "LAX", BASE + 14 * HOUR, BASE + 20 * HOUR, 200.0)
    fs.add_flight("F6", "LAX", "ORD", BASE + 22 * HOUR, BASE + DAY + 2 * HOUR, 150.0)
    return fs


# ===========================================================================
# Level 1: Basic Flight Search
# ===========================================================================

class TestLevel1:
    def test_add_and_search_basic(self):
        fs = FlightSearch()
        fs.add_flight("F1", "SFO", "JFK", 1000, 5000, 300.0)
        results = fs.search("SFO", "JFK")
        assert len(results) == 1
        assert results[0]["flight_id"] == "F1"

    def test_duration_computed(self):
        fs = FlightSearch()
        fs.add_flight("F1", "SFO", "JFK", 1000, 5000, 300.0)
        results = fs.search("SFO", "JFK")
        assert results[0]["duration"] == 4000

    def test_invalid_flight_arrival_before_departure(self):
        fs = FlightSearch()
        with pytest.raises(ValueError):
            fs.add_flight("F1", "SFO", "JFK", 5000, 1000, 300.0)

    def test_invalid_flight_arrival_equals_departure(self):
        fs = FlightSearch()
        with pytest.raises(ValueError):
            fs.add_flight("F1", "SFO", "JFK", 5000, 5000, 300.0)

    def test_search_sorted_by_departure(self):
        fs = FlightSearch()
        fs.add_flight("F2", "SFO", "JFK", 2000, 6000, 250.0)
        fs.add_flight("F1", "SFO", "JFK", 1000, 5000, 300.0)
        fs.add_flight("F3", "SFO", "JFK", 3000, 7000, 200.0)
        results = fs.search("SFO", "JFK")
        assert [r["flight_id"] for r in results] == ["F1", "F2", "F3"]

    def test_search_no_results(self):
        fs = FlightSearch()
        fs.add_flight("F1", "SFO", "JFK", 1000, 5000, 300.0)
        results = fs.search("JFK", "SFO")
        assert results == []

    def test_search_multiple_routes(self):
        fs = FlightSearch()
        fs.add_flight("F1", "SFO", "JFK", 1000, 5000, 300.0)
        fs.add_flight("F2", "SFO", "LAX", 1000, 3000, 100.0)
        fs.add_flight("F3", "JFK", "LAX", 6000, 10000, 200.0)
        assert len(fs.search("SFO", "JFK")) == 1
        assert len(fs.search("SFO", "LAX")) == 1
        assert len(fs.search("JFK", "LAX")) == 1

    def test_flight_dict_keys(self):
        fs = FlightSearch()
        fs.add_flight("F1", "SFO", "JFK", 1000, 5000, 300.0)
        result = fs.search("SFO", "JFK")[0]
        expected_keys = {"flight_id", "origin", "destination", "departure",
                         "arrival", "price", "duration"}
        assert set(result.keys()) == expected_keys

    def test_multiple_flights_same_route(self):
        fs = FlightSearch()
        for i in range(5):
            fs.add_flight(f"F{i}", "SFO", "JFK", 1000 + i * 1000,
                          5000 + i * 1000, 200.0 + i * 50)
        results = fs.search("SFO", "JFK")
        assert len(results) == 5
        departures = [r["departure"] for r in results]
        assert departures == sorted(departures)

    def test_price_stored_correctly(self):
        fs = FlightSearch()
        fs.add_flight("F1", "SFO", "JFK", 1000, 5000, 299.99)
        assert fs.search("SFO", "JFK")[0]["price"] == 299.99


# ===========================================================================
# Level 2: Filters and Sorting
# ===========================================================================

class TestLevel2:
    def test_filter_by_date(self):
        fs = make_fs_with_flights()
        day_num = BASE // DAY
        results = fs.search("SFO", "JFK", date=day_num)
        assert len(results) == 3  # F1, F2, F3
        assert all(r["departure"] // DAY == day_num for r in results)

    def test_filter_by_date_next_day(self):
        fs = make_fs_with_flights()
        day_num = (BASE + DAY) // DAY
        results = fs.search("SFO", "JFK", date=day_num)
        assert len(results) == 1
        assert results[0]["flight_id"] == "F4"

    def test_filter_by_min_price(self):
        fs = make_fs_with_flights()
        results = fs.search("SFO", "JFK", min_price=290.0)
        assert all(r["price"] >= 290.0 for r in results)
        assert len(results) == 2  # F1 (300) and F3 (400)

    def test_filter_by_max_price(self):
        fs = make_fs_with_flights()
        results = fs.search("SFO", "JFK", max_price=280.0)
        assert all(r["price"] <= 280.0 for r in results)
        ids = {r["flight_id"] for r in results}
        assert ids == {"F2", "F4"}

    def test_filter_by_price_range(self):
        fs = make_fs_with_flights()
        results = fs.search("SFO", "JFK", min_price=260.0, max_price=310.0)
        assert len(results) == 2  # F1 (300), F4 (280)

    def test_filter_by_departure_after(self):
        fs = make_fs_with_flights()
        cutoff = BASE + 9 * HOUR
        results = fs.search("SFO", "JFK", departure_after=cutoff)
        assert all(r["departure"] >= cutoff for r in results)

    def test_filter_by_departure_before(self):
        fs = make_fs_with_flights()
        cutoff = BASE + 9 * HOUR
        results = fs.search("SFO", "JFK", departure_before=cutoff)
        assert all(r["departure"] <= cutoff for r in results)
        assert len(results) == 2  # F1, F2

    def test_combined_filters(self):
        fs = make_fs_with_flights()
        day_num = BASE // DAY
        results = fs.search("SFO", "JFK", date=day_num, max_price=300.0)
        assert len(results) == 2  # F1 (300) and F2 (250)

    def test_sort_by_price(self):
        fs = make_fs_with_flights()
        results = fs.search("SFO", "JFK")
        sorted_results = fs.sort_by(results, "price")
        prices = [r["price"] for r in sorted_results]
        assert prices == sorted(prices)

    def test_sort_by_duration(self):
        fs = FlightSearch()
        fs.add_flight("F1", "A", "B", 1000, 8000, 100.0)   # dur 7000
        fs.add_flight("F2", "A", "B", 2000, 5000, 200.0)   # dur 3000
        fs.add_flight("F3", "A", "B", 3000, 9000, 150.0)   # dur 6000
        results = fs.search("A", "B")
        sorted_results = fs.sort_by(results, "duration")
        durations = [r["duration"] for r in sorted_results]
        assert durations == [3000, 6000, 7000]

    def test_sort_by_arrival(self):
        fs = make_fs_with_flights()
        results = fs.search("SFO", "JFK")
        sorted_results = fs.sort_by(results, "arrival")
        arrivals = [r["arrival"] for r in sorted_results]
        assert arrivals == sorted(arrivals)

    def test_sort_by_invalid_key(self):
        fs = FlightSearch()
        with pytest.raises(ValueError):
            fs.sort_by([], "invalid_key")


# ===========================================================================
# Level 3: Connecting Flights
# ===========================================================================

class TestLevel3:
    def test_direct_not_in_connections(self):
        """search_connections should not return direct flights."""
        fs = FlightSearch()
        fs.add_flight("F1", "SFO", "JFK", 1000, 5000, 300.0)
        connections = fs.search_connections("SFO", "JFK")
        assert len(connections) == 0

    def test_one_stop_connection(self):
        fs = FlightSearch()
        fs.add_flight("F1", "SFO", "DEN", BASE, BASE + 3 * HOUR, 150.0)
        fs.add_flight("F2", "DEN", "JFK", BASE + 5 * HOUR, BASE + 9 * HOUR, 200.0)
        connections = fs.search_connections("SFO", "JFK", max_stops=1)
        assert len(connections) == 1
        c = connections[0]
        assert len(c["legs"]) == 2
        assert c["total_price"] == 350.0
        assert c["total_duration"] == 9 * HOUR

    def test_layover_too_short(self):
        fs = FlightSearch()
        fs.add_flight("F1", "SFO", "DEN", BASE, BASE + 3 * HOUR, 150.0)
        # Layover only 30 min — too short
        fs.add_flight("F2", "DEN", "JFK", BASE + 3 * HOUR + 1800,
                       BASE + 7 * HOUR, 200.0)
        connections = fs.search_connections("SFO", "JFK")
        assert len(connections) == 0

    def test_layover_too_long(self):
        fs = FlightSearch()
        fs.add_flight("F1", "SFO", "DEN", BASE, BASE + 3 * HOUR, 150.0)
        # Layover 10 hours — too long
        fs.add_flight("F2", "DEN", "JFK", BASE + 13 * HOUR,
                       BASE + 17 * HOUR, 200.0)
        connections = fs.search_connections("SFO", "JFK")
        assert len(connections) == 0

    def test_layover_exact_min(self):
        """Layover of exactly 1 hour should be valid."""
        fs = FlightSearch()
        fs.add_flight("F1", "SFO", "DEN", BASE, BASE + 3 * HOUR, 150.0)
        fs.add_flight("F2", "DEN", "JFK", BASE + 4 * HOUR,
                       BASE + 8 * HOUR, 200.0)
        connections = fs.search_connections("SFO", "JFK")
        assert len(connections) == 1

    def test_layover_exact_max(self):
        """Layover of exactly 8 hours should be valid."""
        fs = FlightSearch()
        fs.add_flight("F1", "SFO", "DEN", BASE, BASE + 3 * HOUR, 150.0)
        fs.add_flight("F2", "DEN", "JFK", BASE + 11 * HOUR,
                       BASE + 15 * HOUR, 200.0)
        connections = fs.search_connections("SFO", "JFK")
        assert len(connections) == 1

    def test_two_stop_connection(self):
        fs = FlightSearch()
        fs.add_flight("F1", "SFO", "DEN", BASE, BASE + 3 * HOUR, 100.0)
        fs.add_flight("F2", "DEN", "ORD", BASE + 5 * HOUR,
                       BASE + 8 * HOUR, 120.0)
        fs.add_flight("F3", "ORD", "JFK", BASE + 10 * HOUR,
                       BASE + 13 * HOUR, 130.0)
        connections = fs.search_connections("SFO", "JFK", max_stops=2)
        assert len(connections) == 1
        c = connections[0]
        assert len(c["legs"]) == 3
        assert c["total_price"] == 350.0
        assert c["total_duration"] == 13 * HOUR

    def test_two_stop_blocked_by_max_stops_1(self):
        fs = FlightSearch()
        fs.add_flight("F1", "SFO", "DEN", BASE, BASE + 3 * HOUR, 100.0)
        fs.add_flight("F2", "DEN", "ORD", BASE + 5 * HOUR,
                       BASE + 8 * HOUR, 120.0)
        fs.add_flight("F3", "ORD", "JFK", BASE + 10 * HOUR,
                       BASE + 13 * HOUR, 130.0)
        connections = fs.search_connections("SFO", "JFK", max_stops=1)
        assert len(connections) == 0

    def test_multiple_connection_options(self):
        fs = FlightSearch()
        # Path via DEN
        fs.add_flight("F1", "SFO", "DEN", BASE, BASE + 3 * HOUR, 150.0)
        fs.add_flight("F2", "DEN", "JFK", BASE + 5 * HOUR,
                       BASE + 9 * HOUR, 200.0)
        # Path via LAX
        fs.add_flight("F3", "SFO", "LAX", BASE, BASE + 2 * HOUR, 100.0)
        fs.add_flight("F4", "LAX", "JFK", BASE + 4 * HOUR,
                       BASE + 10 * HOUR, 250.0)
        connections = fs.search_connections("SFO", "JFK", max_stops=1)
        assert len(connections) == 2

    def test_no_cycle(self):
        """Connections should not revisit an airport."""
        fs = FlightSearch()
        fs.add_flight("F1", "SFO", "DEN", BASE, BASE + 3 * HOUR, 100.0)
        fs.add_flight("F2", "DEN", "SFO", BASE + 5 * HOUR,
                       BASE + 8 * HOUR, 100.0)
        fs.add_flight("F3", "SFO", "JFK", BASE + 10 * HOUR,
                       BASE + 14 * HOUR, 200.0)
        connections = fs.search_connections("SFO", "JFK", max_stops=2)
        assert len(connections) == 0

    def test_connection_legs_sorted(self):
        fs = FlightSearch()
        fs.add_flight("F1", "SFO", "DEN", BASE, BASE + 3 * HOUR, 150.0)
        fs.add_flight("F2", "DEN", "JFK", BASE + 5 * HOUR,
                       BASE + 9 * HOUR, 200.0)
        connections = fs.search_connections("SFO", "JFK")
        for c in connections:
            departures = [leg["departure"] for leg in c["legs"]]
            assert departures == sorted(departures)


# ===========================================================================
# Level 4: Recurring Schedules
# ===========================================================================

class TestLevel4:
    def test_add_schedule_and_generate(self):
        fs = FlightSearch()
        # Every Monday (0) and Wednesday (2)
        fs.add_schedule("UA100", "SFO", "JFK",
                        departure_time_of_day=8 * HOUR,
                        duration=5 * HOUR,
                        price=300.0,
                        days=[0, 2])
        # Generate for one week starting Monday 2024-01-01
        fs.generate_flights(BASE, BASE + 7 * DAY)
        results = fs.search("SFO", "JFK")
        assert len(results) == 2  # Monday and Wednesday

    def test_generate_flight_ids(self):
        fs = FlightSearch()
        fs.add_schedule("UA100", "SFO", "JFK",
                        departure_time_of_day=8 * HOUR,
                        duration=5 * HOUR,
                        price=300.0,
                        days=[0])  # Monday only
        fs.generate_flights(BASE, BASE + 7 * DAY)
        results = fs.search("SFO", "JFK")
        assert len(results) == 1
        assert results[0]["flight_id"] == f"UA100_{BASE}"

    def test_generate_correct_times(self):
        fs = FlightSearch()
        fs.add_schedule("UA100", "SFO", "JFK",
                        departure_time_of_day=8 * HOUR,
                        duration=5 * HOUR,
                        price=300.0,
                        days=[0])
        fs.generate_flights(BASE, BASE + 7 * DAY)
        result = fs.search("SFO", "JFK")[0]
        assert result["departure"] == BASE + 8 * HOUR
        assert result["arrival"] == BASE + 13 * HOUR
        assert result["duration"] == 5 * HOUR

    def test_generate_multiple_weeks(self):
        fs = FlightSearch()
        fs.add_schedule("UA100", "SFO", "JFK",
                        departure_time_of_day=10 * HOUR,
                        duration=5 * HOUR,
                        price=300.0,
                        days=[0])  # Monday
        fs.generate_flights(BASE, BASE + 21 * DAY)  # 3 weeks
        results = fs.search("SFO", "JFK")
        assert len(results) == 3

    def test_generate_every_day(self):
        fs = FlightSearch()
        fs.add_schedule("DL200", "LAX", "ORD",
                        departure_time_of_day=6 * HOUR,
                        duration=4 * HOUR,
                        price=200.0,
                        days=[0, 1, 2, 3, 4, 5, 6])
        fs.generate_flights(BASE, BASE + 7 * DAY)
        results = fs.search("LAX", "ORD")
        assert len(results) == 7

    def test_get_cheapest(self):
        fs = FlightSearch()
        fs.add_flight("F1", "SFO", "JFK", 1000, 5000, 300.0)
        fs.add_flight("F2", "SFO", "JFK", 2000, 6000, 200.0)
        fs.add_flight("F3", "SFO", "JFK", 3000, 7000, 400.0)
        cheapest = fs.get_cheapest("SFO", "JFK")
        assert cheapest["flight_id"] == "F2"
        assert cheapest["price"] == 200.0

    def test_get_cheapest_no_flights(self):
        fs = FlightSearch()
        assert fs.get_cheapest("SFO", "JFK") is None

    def test_get_route_stats(self):
        fs = FlightSearch()
        fs.add_flight("F1", "SFO", "JFK", 1000, 5000, 300.0)
        fs.add_flight("F2", "SFO", "JFK", 2000, 6000, 200.0)
        fs.add_flight("F3", "SFO", "JFK", 3000, 7000, 400.0)
        stats = fs.get_route_stats("SFO", "JFK")
        assert stats["flight_count"] == 3
        assert stats["min_price"] == 200.0
        assert stats["max_price"] == 400.0
        assert stats["avg_price"] == 300.0

    def test_get_route_stats_no_flights(self):
        fs = FlightSearch()
        stats = fs.get_route_stats("SFO", "JFK")
        assert stats["flight_count"] == 0

    def test_schedule_with_generate_then_stats(self):
        fs = FlightSearch()
        fs.add_schedule("UA100", "SFO", "JFK",
                        departure_time_of_day=8 * HOUR,
                        duration=5 * HOUR,
                        price=300.0,
                        days=[0, 2, 4])  # Mon, Wed, Fri
        fs.add_schedule("DL200", "SFO", "JFK",
                        departure_time_of_day=14 * HOUR,
                        duration=5 * HOUR,
                        price=250.0,
                        days=[0, 2, 4])
        fs.generate_flights(BASE, BASE + 7 * DAY)
        stats = fs.get_route_stats("SFO", "JFK")
        assert stats["flight_count"] == 6  # 3 days * 2 schedules
        assert stats["min_price"] == 250.0
        assert stats["max_price"] == 300.0

    def test_schedule_weekday_check(self):
        """2024-01-01 is Monday. Tuesday is 2024-01-02."""
        fs = FlightSearch()
        fs.add_schedule("UA100", "SFO", "JFK",
                        departure_time_of_day=8 * HOUR,
                        duration=5 * HOUR,
                        price=300.0,
                        days=[1])  # Tuesday only
        fs.generate_flights(BASE, BASE + 7 * DAY)
        results = fs.search("SFO", "JFK")
        assert len(results) == 1
        dep = results[0]["departure"]
        dt = datetime.fromtimestamp(dep, tz=timezone.utc)
        assert dt.weekday() == 1  # Tuesday
