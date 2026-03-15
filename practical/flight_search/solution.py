from datetime import datetime, timezone


class FlightSearch:
    def __init__(self):
        self.flights = []      # list of flight dicts
        self.schedules = []    # list of schedule dicts

    # ---- Level 1 ----

    def add_flight(self, flight_id: str, origin: str, destination: str,
                   departure: int, arrival: int, price: float):
        if arrival <= departure:
            raise ValueError("Arrival must be after departure")
        flight = {
            "flight_id": flight_id,
            "origin": origin,
            "destination": destination,
            "departure": departure,
            "arrival": arrival,
            "price": price,
            "duration": arrival - departure,
        }
        self.flights.append(flight)

    def search(self, origin: str, destination: str, **kwargs) -> list[dict]:
        results = [
            f for f in self.flights
            if f["origin"] == origin and f["destination"] == destination
        ]

        # Level 2 filters
        if "date" in kwargs:
            day = kwargs["date"]
            results = [f for f in results if f["departure"] // 86400 == day]
        if "min_price" in kwargs:
            results = [f for f in results if f["price"] >= kwargs["min_price"]]
        if "max_price" in kwargs:
            results = [f for f in results if f["price"] <= kwargs["max_price"]]
        if "departure_after" in kwargs:
            results = [f for f in results if f["departure"] >= kwargs["departure_after"]]
        if "departure_before" in kwargs:
            results = [f for f in results if f["departure"] <= kwargs["departure_before"]]

        results.sort(key=lambda f: f["departure"])
        return results

    # ---- Level 2 ----

    def sort_by(self, results: list[dict], key: str) -> list[dict]:
        if key not in ("price", "departure", "duration", "arrival"):
            raise ValueError(f"Invalid sort key: {key}")
        return sorted(results, key=lambda f: f[key])

    # ---- Level 3 ----

    def search_connections(self, origin: str, destination: str,
                           max_stops: int = 1) -> list[dict]:
        connections = []
        self._find_connections(origin, destination, max_stops, [], connections)
        return connections

    def _find_connections(self, current: str, destination: str,
                          stops_remaining: int, path: list[dict],
                          connections: list[dict]):
        # Get all flights departing from current location
        departing = [f for f in self.flights if f["origin"] == current]
        departing.sort(key=lambda f: f["departure"])

        for flight in departing:
            # Check layover constraint with previous leg
            if path:
                last_arrival = path[-1]["arrival"]
                layover = flight["departure"] - last_arrival
                if layover < 3600 or layover > 28800:
                    continue

            # Avoid cycles: don't revisit airports already in the path
            visited = {leg["origin"] for leg in path}
            visited.add(current)
            if flight["destination"] in visited:
                continue

            new_path = path + [flight]

            if flight["destination"] == destination:
                # Only include multi-leg connections (at least 2 legs)
                if len(new_path) >= 2:
                    total_price = sum(leg["price"] for leg in new_path)
                    total_duration = new_path[-1]["arrival"] - new_path[0]["departure"]
                    connections.append({
                        "legs": new_path,
                        "total_price": total_price,
                        "total_duration": total_duration,
                    })
            elif stops_remaining > 0:
                self._find_connections(
                    flight["destination"], destination,
                    stops_remaining - 1, new_path, connections
                )

    # ---- Level 4 ----

    def add_schedule(self, flight_id: str, origin: str, destination: str,
                     departure_time_of_day: int, duration: int, price: float,
                     days: list[int]):
        schedule = {
            "flight_id": flight_id,
            "origin": origin,
            "destination": destination,
            "departure_time_of_day": departure_time_of_day,
            "duration": duration,
            "price": price,
            "days": days,
        }
        self.schedules.append(schedule)

    def generate_flights(self, start_date: int, end_date: int):
        # Iterate day by day from start_date to end_date (exclusive)
        # Align start_date to day boundary
        day_start = (start_date // 86400) * 86400
        while day_start < end_date:
            dt = datetime.fromtimestamp(day_start, tz=timezone.utc)
            weekday = dt.weekday()  # 0=Mon, 6=Sun

            for schedule in self.schedules:
                if weekday in schedule["days"]:
                    departure = day_start + schedule["departure_time_of_day"]
                    if departure < start_date or departure >= end_date:
                        continue
                    arrival = departure + schedule["duration"]
                    generated_id = f"{schedule['flight_id']}_{day_start}"
                    self.add_flight(
                        generated_id,
                        schedule["origin"],
                        schedule["destination"],
                        departure,
                        arrival,
                        schedule["price"],
                    )

            day_start += 86400

    def get_cheapest(self, origin: str, destination: str) -> dict:
        matches = [
            f for f in self.flights
            if f["origin"] == origin and f["destination"] == destination
        ]
        if not matches:
            return None
        return min(matches, key=lambda f: f["price"])

    def get_route_stats(self, origin: str, destination: str) -> dict:
        matches = [
            f for f in self.flights
            if f["origin"] == origin and f["destination"] == destination
        ]
        if not matches:
            return {"avg_price": 0, "min_price": 0, "max_price": 0, "flight_count": 0}
        prices = [f["price"] for f in matches]
        return {
            "avg_price": sum(prices) / len(prices),
            "min_price": min(prices),
            "max_price": max(prices),
            "flight_count": len(matches),
        }
