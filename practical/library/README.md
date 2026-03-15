# Library Management System

> ICF-Style System Design — 4 progressive levels, ~90 minutes

Design and implement a library system with book management, waitlists, fines, and recommendations.

---

## Level 1: Basic Library

Implement a library with book checkout and return.

### Constructor

```python
Library()
```

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `add_book(book_id: str, title: str, genre: str)` | `None` | Add a book to the library |
| `checkout(member_id: str, book_id: str, due_date: int)` | `None` | Check out a book |
| `return_book(book_id: str, return_date: int)` | `None` | Return a book |

### Rules

- Dates are integers (day numbers: 1, 2, 3, …)
- A book can only be checked out once at a time
- `checkout()` raises `ValueError` if the book doesn't exist or is already checked out
- `return_book()` raises `ValueError` if the book isn't checked out
- `add_book()` raises `ValueError` if `book_id` already exists

### Example

```python
lib = Library()
lib.add_book("B1", "Clean Code", "programming")
lib.checkout("M1", "B1", due_date=14)
lib.return_book("B1", return_date=10)
```

---

## Level 2: Multiple Copies and Waitlist

Support multiple copies per title and automatic waitlist processing.

**All Level 1 tests must still pass.**

### Updated Behavior

- `add_book(book_id, title, genre)` can be called multiple times with the **same `book_id`** to add additional copies
- Each copy is tracked internally with a unique copy index
- `checkout(member_id, book_id, due_date)` checks out any available copy
- If all copies are checked out, the member is automatically added to a **waitlist**
- When a copy is returned, the first member on the waitlist is auto-checked-out

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `get_waitlist(book_id: str)` | `list[str]` | Members waiting, in order |
| `get_available_copies(book_id: str)` | `int` | Number of available copies |

### Example

```python
lib = Library()
lib.add_book("B1", "Clean Code", "programming")
lib.add_book("B1", "Clean Code", "programming")  # 2 copies
lib.checkout("M1", "B1", 14)
lib.checkout("M2", "B1", 14)
lib.checkout("M3", "B1", 14)  # waitlisted
lib.get_waitlist("B1")        # → ["M3"]
lib.return_book("B1", 10)     # auto-assigns to M3
```

---

## Level 3: Fines

Add overdue fine calculation and payment tracking.

**All Level 1–2 tests must still pass.**

### Fine Rules

- A return is **overdue** if `return_date > due_date`
- Fine = `$1 per day overdue`
- Members with unpaid fines (`> $0`) **cannot check out** new books

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `get_fines(member_id: str)` | `float` | Outstanding (unpaid) fines |
| `pay_fine(member_id: str, amount: float)` | `None` | Pay toward fines |
| `get_member_history(member_id: str)` | `list[dict]` | Checkout history for a member |

### Fine Payment

- `pay_fine()` reduces outstanding fines by `amount`
- Cannot overpay (raise `ValueError` if `amount > outstanding`)

### Member History

```python
get_member_history("M1")
# → [
#     {"book_id": "B1", "due_date": 14, "return_date": 16, "fine": 2.0},
#     {"book_id": "B2", "due_date": 20, "return_date": 18, "fine": 0.0},
# ]
```

---

## Level 4: Recommendations, Bulk Operations, Reports

**All Level 1–3 tests must still pass.**

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `recommend(member_id: str, n: int)` | `list[str]` | Recommend up to `n` book_ids |
| `bulk_checkout(member_id: str, book_ids: list[str], due_date: int)` | `None` | Check out multiple books |
| `bulk_return(book_ids: list[str], return_date: int)` | `None` | Return multiple books |
| `get_overdue_books(current_date: int)` | `list[dict]` | All currently overdue checkouts |

### Recommendations

- Based on genres the member has previously checked out
- Rank genres by frequency (most-checked-out genre first)
- Within each genre, suggest books the member hasn't read yet
- Return up to `n` book_ids, prioritizing top genres

### Bulk Operations

- `bulk_checkout`: check out all listed books; if any fails, still process the others
- `bulk_return`: return all listed books; if any fails, still process the others

### Overdue Report

```python
get_overdue_books(current_date=15)
# → [
#     {"book_id": "B1", "member_id": "M1", "due_date": 10, "days_overdue": 5},
# ]
```

- Only includes books currently checked out (not yet returned) and past due
