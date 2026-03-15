"""Library Management System — Reference Solution (all levels)."""

from __future__ import annotations

from collections import defaultdict, Counter
from dataclasses import dataclass


@dataclass
class BookInfo:
    book_id: str
    title: str
    genre: str
    total_copies: int = 0


@dataclass
class CopyCheckout:
    copy_idx: int
    member_id: str
    due_date: int
    return_date: int | None = None


class Library:
    def __init__(self) -> None:
        # book_id → BookInfo
        self._books: dict[str, BookInfo] = {}
        # book_id → {copy_idx: CopyCheckout or None}
        self._copies: dict[str, dict[int, CopyCheckout | None]] = defaultdict(dict)
        # book_id → waitlist of (member_id, due_date)
        self._waitlists: dict[str, list[tuple[str, int]]] = defaultdict(list)
        # member_id → outstanding fines
        self._fines: dict[str, float] = defaultdict(float)
        # member_id → list of checkout records
        self._history: dict[str, list[dict]] = defaultdict(list)

    # ── Level 1 ────────────────────────────────────────────────────

    def add_book(self, book_id: str, title: str, genre: str) -> None:
        if book_id not in self._books:
            self._books[book_id] = BookInfo(book_id=book_id, title=title, genre=genre)

        info = self._books[book_id]
        copy_idx = info.total_copies
        info.total_copies += 1
        self._copies[book_id][copy_idx] = None  # None = available

    def checkout(self, member_id: str, book_id: str, due_date: int) -> None:
        if book_id not in self._books:
            raise ValueError(f"Unknown book: {book_id}")

        # Level 3: block if has unpaid fines
        if self._fines[member_id] > 0:
            raise ValueError(f"Member {member_id} has unpaid fines")

        # Find an available copy
        available_copy = self._find_available_copy(book_id)
        if available_copy is None:
            # Level 2: waitlist
            self._waitlists[book_id].append((member_id, due_date))
            return

        self._do_checkout(book_id, available_copy, member_id, due_date)

    def return_book(self, book_id: str, return_date: int) -> None:
        if book_id not in self._books:
            raise ValueError(f"Unknown book: {book_id}")

        # Find a checked-out copy
        checked_out_copy = None
        for idx, co in self._copies[book_id].items():
            if co is not None:
                checked_out_copy = idx
                break

        if checked_out_copy is None:
            raise ValueError(f"Book {book_id} is not checked out")

        co = self._copies[book_id][checked_out_copy]
        assert co is not None
        member_id = co.member_id
        due_date = co.due_date

        # Level 3: calculate fine
        fine = max(0, return_date - due_date) * 1.0
        if fine > 0:
            self._fines[member_id] += fine

        # Record history
        self._history[member_id].append({
            "book_id": book_id,
            "due_date": due_date,
            "return_date": return_date,
            "fine": fine,
        })

        # Free the copy
        self._copies[book_id][checked_out_copy] = None

        # Level 2: process waitlist
        if self._waitlists[book_id]:
            next_member, next_due = self._waitlists[book_id].pop(0)
            self._do_checkout(book_id, checked_out_copy, next_member, next_due)

    # ── Level 2 ────────────────────────────────────────────────────

    def get_waitlist(self, book_id: str) -> list[str]:
        return [m for m, _ in self._waitlists.get(book_id, [])]

    def get_available_copies(self, book_id: str) -> int:
        if book_id not in self._copies:
            return 0
        return sum(1 for co in self._copies[book_id].values() if co is None)

    # ── Level 3 ────────────────────────────────────────────────────

    def get_fines(self, member_id: str) -> float:
        return self._fines[member_id]

    def pay_fine(self, member_id: str, amount: float) -> None:
        if amount > self._fines[member_id]:
            raise ValueError("Cannot overpay fines")
        self._fines[member_id] -= amount

    def get_member_history(self, member_id: str) -> list[dict]:
        return list(self._history[member_id])

    # ── Level 4 ────────────────────────────────────────────────────

    def recommend(self, member_id: str, n: int) -> list[str]:
        # Count genres from history
        genre_counter: Counter[str] = Counter()
        read_books: set[str] = set()
        for record in self._history[member_id]:
            book_id = record["book_id"]
            read_books.add(book_id)
            genre = self._books[book_id].genre
            genre_counter[genre] += 1

        # Also count currently checked out books
        for book_id, copies in self._copies.items():
            for co in copies.values():
                if co is not None and co.member_id == member_id:
                    read_books.add(book_id)
                    genre_counter[self._books[book_id].genre] += 1

        recommendations: list[str] = []
        for genre, _ in genre_counter.most_common():
            for book_id, info in self._books.items():
                if info.genre == genre and book_id not in read_books:
                    recommendations.append(book_id)
                    if len(recommendations) >= n:
                        return recommendations

        return recommendations

    def bulk_checkout(self, member_id: str, book_ids: list[str],
                      due_date: int) -> None:
        for book_id in book_ids:
            try:
                self.checkout(member_id, book_id, due_date)
            except ValueError:
                continue

    def bulk_return(self, book_ids: list[str], return_date: int) -> None:
        for book_id in book_ids:
            try:
                self.return_book(book_id, return_date)
            except ValueError:
                continue

    def get_overdue_books(self, current_date: int) -> list[dict]:
        overdue = []
        for book_id, copies in self._copies.items():
            for co in copies.values():
                if co is not None and current_date > co.due_date:
                    overdue.append({
                        "book_id": book_id,
                        "member_id": co.member_id,
                        "due_date": co.due_date,
                        "days_overdue": current_date - co.due_date,
                    })
        return overdue

    # ── Internals ─────────────────────────────────────────────────

    def _find_available_copy(self, book_id: str) -> int | None:
        for idx, co in self._copies[book_id].items():
            if co is None:
                return idx
        return None

    def _do_checkout(self, book_id: str, copy_idx: int,
                     member_id: str, due_date: int) -> None:
        self._copies[book_id][copy_idx] = CopyCheckout(
            copy_idx=copy_idx, member_id=member_id, due_date=due_date,
        )
