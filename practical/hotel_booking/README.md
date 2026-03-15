# Hotel Booking System

> ICF-Style System Design — 4 progressive levels, ~90 minutes

Design and implement a hotel booking system with room management, pricing, loyalty programs, and overbooking logic.

---

## Level 1: Basic Booking

Implement a simple hotel with room booking and cancellation.

### Constructor

```python
Hotel(rooms: list[int])
```

Creates a hotel with the given room IDs.

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `book(guest: str, check_in: int, check_out: int)` | `int` | Book a room, return booking ID |
| `cancel(booking_id: int)` | `None` | Cancel a booking |

### Rules

- Dates are integers (day numbers: 1, 2, 3, …)
- A room is unavailable if it has a booking overlapping the requested dates
- Overlap: two ranges `[a, b)` and `[c, d)` overlap if NOT (`b <= c` or `d <= a`)
- Assign the **lowest available** room ID
- Booking IDs auto-increment from 1
- `book()` raises `ValueError` if no rooms are available
- `cancel()` raises `ValueError` if booking ID is invalid

### Example

```python
hotel = Hotel([101, 102, 103])
hotel.book("Alice", 1, 5)   # → 1 (room 101, days 1-4)
hotel.book("Bob", 3, 7)     # → 2 (room 102, days 3-6)
hotel.book("Carol", 1, 3)   # → 3 (room 102? No overlap with Bob)
hotel.cancel(1)              # Frees room 101 for days 1-4
```

---

## Level 2: Room Types and Availability

Add room types and availability queries.

**All Level 1 tests must still pass.**

### Enum

```python
class RoomType(Enum):
    SINGLE = "single"
    DOUBLE = "double"
    SUITE = "suite"
```

### Constructor

```python
Hotel(rooms: dict[RoomType, list[int]])
```

Maps room types to lists of room IDs.

### Updated Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `book(guest: str, check_in: int, check_out: int, room_type: RoomType)` | `int` | Book a room of the given type |
| `get_availability(room_type: RoomType, check_in: int, check_out: int)` | `list[int]` | Available room IDs of this type for the date range |

### Rules

- Assign lowest available room ID of the requested type
- `get_availability()` returns sorted list of room IDs with no overlapping bookings

---

## Level 3: Pricing and Loyalty

Add pricing with seasonal rates and a loyalty points system.

**All Level 1–2 tests must still pass.**

### Base Rates (per night)

| Room Type | Base Rate |
|-----------|----------|
| SINGLE | $100 |
| DOUBLE | $200 |
| SUITE | $500 |

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `book(guest, check_in, check_out, room_type)` | `tuple[int, float]` | Return `(booking_id, total_cost)` |
| `set_season(name: str, start: int, end: int, multiplier: float)` | `None` | Define a season with price multiplier |
| `get_loyalty_points(guest: str)` | `int` | Return loyalty points for a guest |

### Pricing

```
total = sum(nightly_rate * season_multiplier for each night)
nightly_rate = base_rate[room_type]
```

- Each night `[day, day+1)` checks if `day` falls within any season
- If multiple seasons overlap, use the **highest** multiplier
- Default multiplier is 1.0

### Loyalty

- 10 points per dollar spent (truncated to int)
- Points accumulate across all bookings for the same guest name

---

## Level 4: Overbooking, Waitlist, Upgrades, Reports

**All Level 1–3 tests must still pass.**

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `set_overbooking_ratio(ratio: float)` | `None` | Allow overbooking (e.g., 1.1 = 110% capacity) |
| `waitlist(guest: str, check_in: int, check_out: int, room_type: RoomType)` | `int` | Add to waitlist, return waitlist position |
| `upgrade(booking_id: int)` | `int` | Upgrade to next tier room, return new room ID |
| `revenue_report(start: int, end: int)` | `dict` | Revenue breakdown by room type and total |

### Overbooking

- `set_overbooking_ratio(1.1)` allows booking up to `ceil(num_rooms * 1.1)` rooms of a type per day
- Default ratio is 1.0 (no overbooking)

### Waitlist

- When no rooms available (even with overbooking), guest goes to waitlist
- Position is 1-indexed within the room type
- When a booking is cancelled, first waitlisted guest is automatically booked

### Upgrades

- SINGLE → DOUBLE → SUITE
- `upgrade()` moves booking to next tier if available, raises `ValueError` if at SUITE or no availability

### Revenue Report

```python
revenue_report(1, 30)
# → {"SINGLE": 500.0, "DOUBLE": 1200.0, "SUITE": 0.0, "total": 1700.0}
```

- Includes revenue from bookings whose check-in falls within `[start, end)`
