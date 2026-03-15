# Flight Reservation System

> ICF-Style System Design — 4 progressive levels, ~90 minutes

Design and implement a flight reservation system with seat classes, fare calculation, and multi-leg booking.

---

## Level 1: Basic Reservation

Implement a single flight with seat reservation and cancellation.

### Constructor

```python
Flight(flight_id: str, total_seats: int)
```

Creates a flight with seats numbered `0` to `total_seats - 1`.

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `reserve(passenger: str, seat_id: int)` | `int` | Reserve a specific seat, return reservation ID |
| `cancel(reservation_id: int)` | `None` | Cancel a reservation |
| `get_available_seats()` | `list[int]` | Return sorted list of available seat IDs |

### Rules

- Reservation IDs auto-increment from 1
- `reserve()` raises `ValueError` if seat is invalid or already taken
- `cancel()` raises `ValueError` if reservation ID is invalid
- A passenger can hold multiple reservations (different seats)

### Example

```python
flight = Flight("UA100", 5)
flight.reserve("Alice", 0)          # → 1
flight.reserve("Bob", 1)            # → 2
flight.get_available_seats()        # → [2, 3, 4]
flight.cancel(1)
flight.get_available_seats()        # → [0, 2, 3, 4]
```

---

## Level 2: Seat Classes

Add seat class categories with class-level booking.

**All Level 1 tests must still pass.**

### Enum

```python
class SeatClass(Enum):
    ECONOMY = "economy"
    BUSINESS = "business"
    FIRST = "first"
```

### Constructor

```python
Flight(flight_id: str, seats: dict[SeatClass, list[int]])
```

Maps seat classes to lists of seat IDs.

### Updated Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `reserve(passenger: str, seat_class: SeatClass)` | `int` | Reserve lowest available seat in class |
| `get_availability(seat_class: SeatClass)` | `list[int]` | Available seats in a class |

### Rules

- Assign **lowest available** seat ID within the requested class
- Raise `ValueError` if no seats available in the class

---

## Level 3: Fares and Upgrades

Add fare calculation, baggage fees, and seat upgrades.

**All Level 1–2 tests must still pass.**

### Base Fares

| Seat Class | Fare |
|-----------|------|
| ECONOMY | $200 |
| BUSINESS | $500 |
| FIRST | $1000 |

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `reserve(passenger, seat_class)` | `tuple[int, float]` | Return `(reservation_id, fare)` |
| `add_baggage(reservation_id: int)` | `float` | Add a bag, return updated total cost |
| `request_upgrade(reservation_id: int, target_class: SeatClass)` | `tuple[int, float]` | Upgrade seat, return `(new_seat_id, upgrade_cost)` |
| `get_total_cost(reservation_id: int)` | `float` | Total cost for a reservation |

### Baggage

- First bag: free
- Additional bags: $30 each
- Maximum 3 bags total per reservation
- `add_baggage()` raises `ValueError` if at max bags

### Upgrades

- Can only upgrade to a **higher** class (ECONOMY → BUSINESS → FIRST)
- Upgrade cost = target fare − current fare
- Passenger moves to lowest available seat in target class
- Original seat is freed
- Raises `ValueError` if target class has no availability or is not higher

---

## Level 4: Multi-Leg Flights

Add a `FlightSystem` that manages multiple flights and supports connected itineraries.

**All Level 1–3 tests must still pass.**

### FlightSystem

```python
class FlightSystem:
    def add_flight(self, flight: Flight) -> None
    def book_connection(self, passenger: str,
                        legs: list[tuple[str, SeatClass]]) -> str
    def cancel_pnr(self, pnr: str) -> None
    def get_itinerary(self, pnr: str) -> list[dict]
```

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `add_flight(flight)` | `None` | Register a flight |
| `book_connection(passenger, legs)` | `str` | Book multi-leg trip, return PNR |
| `cancel_pnr(pnr)` | `None` | Cancel all legs in a PNR |
| `get_itinerary(pnr)` | `list[dict]` | Return leg details |

### Rules

- PNR format: `"PNR-1"`, `"PNR-2"`, … (auto-increment)
- `legs` is a list of `(flight_id, seat_class)` tuples
- **Atomic booking**: if any leg fails, none are booked (rollback)
- `cancel_pnr()` cancels all reservations in the PNR
- `get_itinerary()` returns list of dicts with `flight_id`, `seat_id`, `seat_class`, `fare`
- Raises `ValueError` for invalid PNR or if any leg cannot be booked

### Example

```python
system = FlightSystem()
system.add_flight(flight_a)
system.add_flight(flight_b)
pnr = system.book_connection("Alice", [
    ("UA100", SeatClass.ECONOMY),
    ("UA200", SeatClass.BUSINESS),
])
# → "PNR-1"
system.get_itinerary("PNR-1")
# → [{"flight_id": "UA100", "seat_id": 0, ...}, ...]
```
