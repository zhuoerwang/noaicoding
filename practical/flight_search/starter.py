class FlightSearch:
    def __init__(self):
        pass

    # ---- Level 1 ----

    def add_flight(self, flight_id: str, origin: str, destination: str,
                   departure: int, arrival: int, price: float):
        """Add a flight. Raise ValueError if arrival <= departure."""
        pass

    def search(self, origin: str, destination: str, **kwargs) -> list[dict]:
        """Return flights matching origin/destination, sorted by departure.

        Optional kwargs (Level 2):
            date (int): day number (departure // 86400)
            min_price (float): minimum price filter
            max_price (float): maximum price filter
            departure_after (int): epoch seconds lower bound
            departure_before (int): epoch seconds upper bound
        """
        pass

    # ---- Level 2 ----

    def sort_by(self, results: list[dict], key: str) -> list[dict]:
        """Sort flight results by key: 'price', 'departure', 'duration', or 'arrival'."""
        pass

    # ---- Level 3 ----

    def search_connections(self, origin: str, destination: str,
                           max_stops: int = 1) -> list[dict]:
        """Find connecting itineraries with at most max_stops intermediate stops.

        Each result has 'legs', 'total_price', 'total_duration'.
        Layover: min 1 hour, max 8 hours.
        """
        pass

    # ---- Level 4 ----

    def add_schedule(self, flight_id: str, origin: str, destination: str,
                     departure_time_of_day: int, duration: int, price: float,
                     days: list[int]):
        """Register a recurring flight schedule.

        departure_time_of_day: seconds since midnight UTC.
        days: list of weekday numbers (0=Mon, 6=Sun).
        """
        pass

    def generate_flights(self, start_date: int, end_date: int):
        """Generate Flight instances for each scheduled day in [start_date, end_date)."""
        pass

    def get_cheapest(self, origin: str, destination: str) -> dict:
        """Return the cheapest flight between origin and destination."""
        pass

    def get_route_stats(self, origin: str, destination: str) -> dict:
        """Return dict with avg_price, min_price, max_price, flight_count."""
        pass
