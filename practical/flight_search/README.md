# Flight Search System

An ICF-style system design project inspired by real flight search systems.

## Level 1: Basic Flight Search

Implement `FlightSearch` with:

- `add_flight(flight_id: str, origin: str, destination: str, departure: int, arrival: int, price: float)` — Add a flight. Departure and arrival are epoch seconds. Raise `ValueError` if `arrival <= departure`.
- `search(origin: str, destination: str) -> list[dict]` — Return all flights matching the origin/destination pair, sorted by departure time. Each flight is a dict with keys: `flight_id`, `origin`, `destination`, `departure`, `arrival`, `price`, `duration`.

Duration is computed as `arrival - departure`.

## Level 2: Filters and Sorting

Extend `search()` to accept optional keyword arguments:

- `date` (int) — Day number, computed as `departure // 86400`. Only return flights on this day.
- `min_price` / `max_price` (float) — Filter by price range.
- `departure_after` / `departure_before` (int, epoch seconds) — Filter by departure time window.

Add a method:

- `sort_by(results: list[dict], key: str) -> list[dict]` — Sort a list of flight dicts by the given key. Valid keys: `"price"`, `"departure"`, `"duration"`, `"arrival"`.

## Level 3: Connecting Flights

- `search_connections(origin: str, destination: str, max_stops: int = 1) -> list[dict]` — Find connecting flight itineraries from origin to destination with at most `max_stops` intermediate stops.

Each connection dict contains:
- `legs` — List of flight dicts (sorted by departure).
- `total_price` — Sum of all leg prices.
- `total_duration` — Time from first departure to last arrival.

Layover constraints:
- Minimum layover: 1 hour (3600 seconds).
- Maximum layover: 8 hours (28800 seconds).

## Level 4: Recurring Schedules

- `add_schedule(flight_id: str, origin: str, destination: str, departure_time_of_day: int, duration: int, price: float, days: list[int])` — Register a recurring flight schedule. `departure_time_of_day` is seconds since midnight UTC. `days` is a list of weekday numbers (0=Monday, 6=Sunday).
- `generate_flights(start_date: int, end_date: int)` — Generate concrete `Flight` instances for each scheduled day within the date range (epoch seconds). Each generated flight gets an ID like `"{flight_id}_{date}"` where date is the epoch timestamp of that day's midnight.
- `get_cheapest(origin: str, destination: str) -> dict` — Return the cheapest flight between origin and destination.
- `get_route_stats(origin: str, destination: str) -> dict` — Return stats dict with `avg_price`, `min_price`, `max_price`, `flight_count` for the route.

## Notes

- All timestamps are epoch seconds (integers).
- Day number = `timestamp // 86400`.
- For schedules, use `datetime.fromtimestamp(ts, tz=timezone.utc).weekday()` to determine the weekday.
- No external dependencies required.
