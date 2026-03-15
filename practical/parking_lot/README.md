# Parking Lot System

> ICF-Style System Design — 4 progressive levels, ~90 minutes

Design and implement a parking lot management system that handles vehicle parking, fee calculation, reservations, and analytics.

---

## Level 1: Basic Parking

Implement a simple parking lot with fixed capacity.

### Constructor

```python
ParkingLot(capacity: int)
```

Creates a parking lot with `capacity` spots numbered `0` to `capacity - 1`.

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `park(vehicle_id: str)` | `int` | Park a vehicle, return assigned spot ID |
| `leave(spot_id: int)` | `str` | Remove vehicle from spot, return vehicle ID |

### Rules

- Assign the **lowest available** spot number
- `park()` raises `ValueError` if the lot is full
- `leave()` raises `ValueError` if `spot_id` is invalid or empty
- Each `vehicle_id` can only be parked once at a time

### Complexity

- `park()`: O(capacity) worst case
- `leave()`: O(1)

### Example

```python
lot = ParkingLot(3)
lot.park("CAR-1")   # → 0
lot.park("CAR-2")   # → 1
lot.leave(0)        # → "CAR-1"
lot.park("CAR-3")   # → 0  (reuses freed spot)
```

---

## Level 2: Vehicle Types and Spot Sizes

Extend the system with different vehicle types and spot sizes.

**All Level 1 tests must still pass.**

### Enums

```python
class VehicleType(Enum):
    MOTORCYCLE = "motorcycle"
    CAR = "car"
    TRUCK = "truck"

class SpotSize(Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
```

### Constructor

```python
ParkingLot(spots: dict[SpotSize, list[int]])
```

Takes a mapping of spot size → list of spot IDs.

### Fitting Rules

| Vehicle | Can fit in |
|---------|-----------|
| MOTORCYCLE | SMALL, MEDIUM, LARGE |
| CAR | MEDIUM, LARGE |
| TRUCK | LARGE only |

### Updated Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `park(vehicle_id: str, vehicle_type: VehicleType)` | `int` | Park vehicle in smallest fitting spot, then lowest ID |
| `leave(spot_id: int)` | `str` | Same as Level 1 |

### Rules

- Assign the **smallest fitting** spot size first, then **lowest spot ID** within that size
- Raise `ValueError` if no fitting spot is available

### Example

```python
lot = ParkingLot({
    SpotSize.SMALL: [0, 1],
    SpotSize.MEDIUM: [2, 3],
    SpotSize.LARGE: [4],
})
lot.park("M-1", VehicleType.MOTORCYCLE)  # → 0 (small, lowest)
lot.park("C-1", VehicleType.CAR)         # → 2 (medium, lowest)
lot.park("T-1", VehicleType.TRUCK)       # → 4 (large only)
```

---

## Level 3: Fee Calculation

Add time-based fee calculation when vehicles leave.

**All Level 1–2 tests must still pass.**

### Updated Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `park(vehicle_id: str, vehicle_type: VehicleType, timestamp: int)` | `int` | Park with check-in time (epoch seconds) |
| `leave(spot_id: int, timestamp: int)` | `tuple[str, float]` | Return `(vehicle_id, fee)` |
| `get_revenue()` | `float` | Total fees collected so far |

### Hourly Rates

| Vehicle Type | Rate per hour |
|-------------|--------------|
| MOTORCYCLE | $1 |
| CAR | $2 |
| TRUCK | $3 |

### Fee Formula

```
hours = ceil((checkout_time - checkin_time) / 3600)
fee = hours * hourly_rate
```

- Partial hours are **rounded up** (use `math.ceil`)
- Minimum charge is 1 hour

### Example

```python
lot.park("C-1", VehicleType.CAR, timestamp=0)
lot.leave(2, timestamp=5400)  # 5400s = 1.5h → ceil = 2h → $4
# → ("C-1", 4.0)
lot.get_revenue()  # → 4.0
```

---

## Level 4: Reservations, Peak Pricing, and Analytics

Add reservation system, dynamic pricing, and usage analytics.

**All Level 1–3 tests must still pass.**

### New Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `reserve(vehicle_id: str, vehicle_type: VehicleType, start: int, end: int)` | `int` | Reserve a spot for a time window, return spot ID |
| `cancel_reservation(reservation_id: int)` | `None` | Cancel a reservation |
| `set_peak_hours(start_hour: int, end_hour: int, multiplier: float)` | `None` | Set peak pricing (hours 0–23) |
| `spot_utilization()` | `dict[int, float]` | Spot ID → total hours used |
| `revenue_by_type()` | `dict[VehicleType, float]` | Revenue breakdown by vehicle type |

### Reservation Rules

- `reserve()` allocates a spot following the same fitting rules as `park()`
- A reserved spot is **unavailable** during its `[start, end)` window
- `park()` cannot use a spot that has an active reservation covering the park timestamp
- Reservation IDs auto-increment from 1
- Raise `ValueError` if no fitting spot is available for the time window

### Peak Pricing

- `set_peak_hours(9, 17, 1.5)` means hours 9:00–17:00 have a 1.5x multiplier
- Peak pricing applies based on the **check-in hour** (hour of day from timestamp)
- Default multiplier is 1.0

### Analytics

- `spot_utilization()` returns hours each spot was occupied (from completed park/leave cycles)
- `revenue_by_type()` returns total revenue grouped by vehicle type

### Example

```python
lot.set_peak_hours(9, 17, 1.5)
# Park during peak (hour 10): rate = $2 * 1.5 = $3/hr
lot.park("C-1", VehicleType.CAR, timestamp=36000)  # 10:00 AM
lot.leave(2, timestamp=39600)  # 11:00 AM, 1 hour → $3.0
lot.revenue_by_type()  # → {VehicleType.CAR: 3.0}
```
