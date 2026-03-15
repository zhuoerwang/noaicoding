"""Library Management System — Tests by Level

Run all:       pytest test_library.py
Run by level:  pytest test_library.py -k "TestLevel1"
               pytest test_library.py -k "TestLevel2"
               pytest test_library.py -k "TestLevel3"
               pytest test_library.py -k "TestLevel4"
"""

import pytest

from solution import Library


# ── Level 1: Basic Library ────────────────────────────────────────


class TestLevel1:
    def test_add_and_checkout(self):
        lib = Library()
        lib.add_book("B1", "Clean Code", "programming")
        lib.checkout("M1", "B1", 14)

    def test_return_book(self):
        lib = Library()
        lib.add_book("B1", "Clean Code", "programming")
        lib.checkout("M1", "B1", 14)
        lib.return_book("B1", 10)

    def test_checkout_unknown_book_raises(self):
        lib = Library()
        with pytest.raises(ValueError):
            lib.checkout("M1", "FAKE", 14)

    def test_checkout_already_out_single_copy(self):
        lib = Library()
        lib.add_book("B1", "Clean Code", "programming")
        lib.checkout("M1", "B1", 14)
        # Second checkout goes to waitlist (L2 behavior) — verify
        # the book is still unavailable
        assert lib.get_available_copies("B1") == 0

    def test_return_not_checked_out_raises(self):
        lib = Library()
        lib.add_book("B1", "Clean Code", "programming")
        with pytest.raises(ValueError):
            lib.return_book("B1", 10)

    def test_return_unknown_book_raises(self):
        lib = Library()
        with pytest.raises(ValueError):
            lib.return_book("FAKE", 10)

    def test_checkout_after_return(self):
        lib = Library()
        lib.add_book("B1", "Clean Code", "programming")
        lib.checkout("M1", "B1", 14)
        lib.return_book("B1", 10)
        lib.checkout("M2", "B1", 20)

    def test_multiple_books(self):
        lib = Library()
        lib.add_book("B1", "Clean Code", "programming")
        lib.add_book("B2", "Design Patterns", "programming")
        lib.checkout("M1", "B1", 14)
        lib.checkout("M1", "B2", 14)

    def test_multiple_members(self):
        lib = Library()
        lib.add_book("B1", "Clean Code", "programming")
        lib.add_book("B2", "Design Patterns", "programming")
        lib.checkout("M1", "B1", 14)
        lib.checkout("M2", "B2", 14)


# ── Level 2: Multiple Copies and Waitlist ─────────────────────────


class TestLevel2:
    def test_multiple_copies(self):
        lib = Library()
        lib.add_book("B1", "Clean Code", "programming")
        lib.add_book("B1", "Clean Code", "programming")
        lib.checkout("M1", "B1", 14)
        lib.checkout("M2", "B1", 14)

    def test_available_copies(self):
        lib = Library()
        lib.add_book("B1", "Clean Code", "programming")
        lib.add_book("B1", "Clean Code", "programming")
        assert lib.get_available_copies("B1") == 2
        lib.checkout("M1", "B1", 14)
        assert lib.get_available_copies("B1") == 1

    def test_waitlist_when_no_copies(self):
        lib = Library()
        lib.add_book("B1", "Clean Code", "programming")
        lib.checkout("M1", "B1", 14)
        lib.checkout("M2", "B1", 14)  # waitlisted
        assert lib.get_waitlist("B1") == ["M2"]

    def test_auto_checkout_on_return(self):
        lib = Library()
        lib.add_book("B1", "Clean Code", "programming")
        lib.checkout("M1", "B1", 14)
        lib.checkout("M2", "B1", 20)  # waitlisted
        lib.return_book("B1", 10)     # auto-assigns to M2
        assert lib.get_available_copies("B1") == 0
        assert lib.get_waitlist("B1") == []

    def test_waitlist_order(self):
        lib = Library()
        lib.add_book("B1", "Clean Code", "programming")
        lib.checkout("M1", "B1", 14)
        lib.checkout("M2", "B1", 14)
        lib.checkout("M3", "B1", 14)
        assert lib.get_waitlist("B1") == ["M2", "M3"]

    def test_three_copies(self):
        lib = Library()
        for _ in range(3):
            lib.add_book("B1", "Clean Code", "programming")
        lib.checkout("M1", "B1", 14)
        lib.checkout("M2", "B1", 14)
        lib.checkout("M3", "B1", 14)
        assert lib.get_available_copies("B1") == 0

    def test_return_one_of_many(self):
        lib = Library()
        lib.add_book("B1", "Clean Code", "programming")
        lib.add_book("B1", "Clean Code", "programming")
        lib.checkout("M1", "B1", 14)
        lib.checkout("M2", "B1", 14)
        lib.return_book("B1", 10)
        assert lib.get_available_copies("B1") == 1

    def test_available_copies_unknown_book(self):
        lib = Library()
        assert lib.get_available_copies("FAKE") == 0


# ── Level 3: Fines ───────────────────────────────────────────────


class TestLevel3:
    def test_no_fine_on_time(self):
        lib = Library()
        lib.add_book("B1", "Clean Code", "programming")
        lib.checkout("M1", "B1", 14)
        lib.return_book("B1", 14)
        assert lib.get_fines("M1") == 0.0

    def test_fine_for_overdue(self):
        lib = Library()
        lib.add_book("B1", "Clean Code", "programming")
        lib.checkout("M1", "B1", 14)
        lib.return_book("B1", 17)  # 3 days late
        assert lib.get_fines("M1") == 3.0

    def test_fine_blocks_checkout(self):
        lib = Library()
        lib.add_book("B1", "Clean Code", "programming")
        lib.add_book("B2", "Design Patterns", "programming")
        lib.checkout("M1", "B1", 10)
        lib.return_book("B1", 15)  # 5 days late, $5 fine
        with pytest.raises(ValueError):
            lib.checkout("M1", "B2", 20)

    def test_pay_fine_allows_checkout(self):
        lib = Library()
        lib.add_book("B1", "Clean Code", "programming")
        lib.add_book("B2", "Design Patterns", "programming")
        lib.checkout("M1", "B1", 10)
        lib.return_book("B1", 15)  # $5 fine
        lib.pay_fine("M1", 5.0)
        lib.checkout("M1", "B2", 20)  # should work now

    def test_partial_fine_payment(self):
        lib = Library()
        lib.add_book("B1", "Clean Code", "programming")
        lib.checkout("M1", "B1", 10)
        lib.return_book("B1", 15)  # $5 fine
        lib.pay_fine("M1", 3.0)
        assert lib.get_fines("M1") == 2.0

    def test_overpay_raises(self):
        lib = Library()
        lib.add_book("B1", "Clean Code", "programming")
        lib.checkout("M1", "B1", 10)
        lib.return_book("B1", 12)  # $2 fine
        with pytest.raises(ValueError):
            lib.pay_fine("M1", 5.0)

    def test_member_history(self):
        lib = Library()
        lib.add_book("B1", "Clean Code", "programming")
        lib.checkout("M1", "B1", 14)
        lib.return_book("B1", 16)
        history = lib.get_member_history("M1")
        assert len(history) == 1
        assert history[0]["book_id"] == "B1"
        assert history[0]["fine"] == 2.0

    def test_no_fine_early_return(self):
        lib = Library()
        lib.add_book("B1", "Clean Code", "programming")
        lib.checkout("M1", "B1", 14)
        lib.return_book("B1", 7)
        assert lib.get_fines("M1") == 0.0

    def test_fines_accumulate(self):
        lib = Library()
        lib.add_book("B1", "Clean Code", "programming")
        lib.add_book("B2", "Design Patterns", "programming")
        lib.checkout("M1", "B1", 10)
        lib.return_book("B1", 12)  # $2
        lib.pay_fine("M1", 2.0)
        lib.checkout("M1", "B2", 10)
        lib.return_book("B2", 13)  # $3
        assert lib.get_fines("M1") == 3.0

    def test_history_empty_for_new_member(self):
        lib = Library()
        assert lib.get_member_history("NEW") == []


# ── Level 4: Recommendations, Bulk, Reports ──────────────────────


class TestLevel4:
    def _setup_lib(self):
        lib = Library()
        lib.add_book("P1", "Clean Code", "programming")
        lib.add_book("P2", "Design Patterns", "programming")
        lib.add_book("P3", "Refactoring", "programming")
        lib.add_book("F1", "Dune", "fiction")
        lib.add_book("F2", "Neuromancer", "fiction")
        lib.add_book("S1", "Cosmos", "science")
        return lib

    def test_recommend_by_genre(self):
        lib = self._setup_lib()
        lib.checkout("M1", "P1", 14)
        lib.return_book("P1", 10)
        lib.checkout("M1", "P2", 14)
        lib.return_book("P2", 10)
        recs = lib.recommend("M1", 2)
        # Should recommend programming books not yet read
        assert "P3" in recs
        assert len(recs) <= 2

    def test_recommend_empty_history(self):
        lib = self._setup_lib()
        recs = lib.recommend("NEW", 5)
        assert recs == []

    def test_recommend_excludes_read(self):
        lib = self._setup_lib()
        lib.checkout("M1", "P1", 14)
        lib.return_book("P1", 10)
        recs = lib.recommend("M1", 10)
        assert "P1" not in recs

    def test_recommend_respects_n(self):
        lib = self._setup_lib()
        lib.checkout("M1", "P1", 14)
        lib.return_book("P1", 10)
        recs = lib.recommend("M1", 1)
        assert len(recs) == 1

    def test_bulk_checkout(self):
        lib = self._setup_lib()
        lib.bulk_checkout("M1", ["P1", "F1", "S1"], 14)
        assert lib.get_available_copies("P1") == 0
        assert lib.get_available_copies("F1") == 0
        assert lib.get_available_copies("S1") == 0

    def test_bulk_checkout_partial_failure(self):
        lib = self._setup_lib()
        lib.checkout("M1", "P1", 14)
        lib.bulk_checkout("M2", ["P1", "F1"], 14)  # P1 goes to waitlist
        assert lib.get_available_copies("F1") == 0

    def test_bulk_return(self):
        lib = self._setup_lib()
        lib.checkout("M1", "P1", 14)
        lib.checkout("M1", "F1", 14)
        lib.bulk_return(["P1", "F1"], 10)
        assert lib.get_available_copies("P1") == 1
        assert lib.get_available_copies("F1") == 1

    def test_overdue_report(self):
        lib = self._setup_lib()
        lib.checkout("M1", "P1", 10)
        lib.checkout("M2", "F1", 20)
        overdue = lib.get_overdue_books(15)
        assert len(overdue) == 1
        assert overdue[0]["book_id"] == "P1"
        assert overdue[0]["days_overdue"] == 5

    def test_overdue_report_empty(self):
        lib = self._setup_lib()
        lib.checkout("M1", "P1", 20)
        overdue = lib.get_overdue_books(15)
        assert overdue == []

    def test_overdue_excludes_returned(self):
        lib = self._setup_lib()
        lib.checkout("M1", "P1", 10)
        lib.return_book("P1", 15)
        overdue = lib.get_overdue_books(15)
        assert overdue == []

    def test_recommend_prioritizes_top_genre(self):
        lib = self._setup_lib()
        # Read 2 programming, 1 fiction
        lib.checkout("M1", "P1", 14)
        lib.return_book("P1", 10)
        lib.checkout("M1", "P2", 14)
        lib.return_book("P2", 10)
        lib.checkout("M1", "F1", 14)
        lib.return_book("F1", 10)
        recs = lib.recommend("M1", 2)
        # Programming should come first (2 vs 1)
        assert recs[0] == "P3"
