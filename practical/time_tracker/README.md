# Employee Time Tracker

> ICF-Style System Design — 4 progressive levels, ~90 minutes

Design and implement an employee time tracking system with overtime rules, departments, and payroll reports.

---

## Level 1: Basic Check-in / Check-out

Implement a system where workers clock in and out.

### Constructor

```python
TimeTracker()
```

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `add_worker(worker_id: str, hourly_wage: float)` | `None` | Register a worker |
| `check_in(worker_id: str, timestamp: int)` | `None` | Clock in (epoch seconds) |
| `check_out(worker_id: str, timestamp: int)` | `None` | Clock out (epoch seconds) |

### Rules

- Timestamps are integers (epoch seconds)
- A worker must be registered before clocking in
- A worker must check in before checking out
- A worker cannot check in twice without checking out
- `check_out` timestamp must be > `check_in` timestamp
- Raise `ValueError` for any violations

### Example

```python
tracker = TimeTracker()
tracker.add_worker("W1", 15.0)
tracker.check_in("W1", 1000)
tracker.check_out("W1", 4600)  # 1 hour session
```

---

## Level 2: Hours and Pay

Track total hours worked and compute pay.

**All Level 1 tests must still pass.**

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `get_total_hours(worker_id: str)` | `float` | Total hours worked (2 decimal places) |
| `get_pay(worker_id: str)` | `float` | Total hours × hourly wage |
| `get_sessions(worker_id: str)` | `list[tuple[int, int]]` | List of (check_in, check_out) tuples |

### Rules

- Hours = `(check_out - check_in) / 3600`, rounded to 2 decimal places
- A worker currently checked in has their completed sessions counted (not the ongoing one)

### Example

```python
tracker.get_total_hours("W1")  # → 1.0
tracker.get_pay("W1")          # → 15.0
tracker.get_sessions("W1")    # → [(1000, 4600)]
```

---

## Level 3: Overtime

Add overtime pay rules.

**All Level 1–2 tests must still pass.**

### Overtime Rules

| Rule | Threshold | Rate |
|------|-----------|------|
| Daily overtime | > 8 hours in a calendar day | 1.5× for excess hours |
| Weekly overtime | > 40 hours in a calendar week | 2× for excess hours |

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `get_pay(worker_id: str)` | `float` | Pay with overtime applied |
| `get_overtime_hours(worker_id: str)` | `dict` | `{"daily": float, "weekly": float}` |

### Rules

- Calendar day: based on UTC (timestamp // 86400)
- Calendar week: ISO week (Monday–Sunday)
- Daily OT is calculated first; weekly OT applies to remaining regular hours
- Hours that already receive daily OT do not also receive weekly OT
- Round overtime hours to 2 decimal places

### Pay Calculation

```
regular_hours = total_hours - daily_ot_hours - weekly_ot_hours
pay = (regular_hours * wage) + (daily_ot_hours * wage * 1.5) + (weekly_ot_hours * wage * 2.0)
```

---

## Level 4: Departments and Reports

Add department grouping and payroll reports.

**All Level 1–3 tests must still pass.**

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `add_department(dept_id: str)` | `None` | Create a department |
| `assign_worker(worker_id: str, dept_id: str)` | `None` | Assign worker to department |
| `get_department_payroll(dept_id: str, start: int, end: int)` | `dict` | Payroll for department in time range |
| `get_top_earners(n: int)` | `list[tuple[str, float]]` | Top N workers by total pay, descending |
| `generate_report(start: int, end: int)` | `dict` | Summary across all departments |

### Department Payroll

```python
get_department_payroll("ENG", start, end)
# → {
#     "dept_id": "ENG",
#     "workers": [
#         {"worker_id": "W1", "hours": 45.0, "pay": 750.0},
#         ...
#     ],
#     "total_hours": 85.0,
#     "total_pay": 1400.0,
# }
```

- Only include sessions where `check_in >= start` and `check_out <= end`

### Report

```python
generate_report(start, end)
# → {
#     "departments": {"ENG": {...}, "SALES": {...}},
#     "total_hours": 200.0,
#     "total_pay": 3500.0,
# }
```
