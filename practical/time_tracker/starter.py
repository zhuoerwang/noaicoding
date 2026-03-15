"""Employee Time Tracker — ICF-Style System Design

Implement a time tracking system across 4 progressive levels.

Run tests by level:
    pytest test_time_tracker.py -k "TestLevel1"
    pytest test_time_tracker.py -k "TestLevel2"
    pytest test_time_tracker.py -k "TestLevel3"
    pytest test_time_tracker.py -k "TestLevel4"
"""

from __future__ import annotations


class TimeTracker:
    """Employee time tracking with overtime and department management."""

    def __init__(self) -> None:
        pass

    # ── Level 1 ────────────────────────────────────────────────────

    def add_worker(self, worker_id: str, hourly_wage: float) -> None:
        """Register a new worker."""
        pass

    def check_in(self, worker_id: str, timestamp: int) -> None:
        """Clock in a worker."""
        pass

    def check_out(self, worker_id: str, timestamp: int) -> None:
        """Clock out a worker."""
        pass

    # ── Level 2 ────────────────────────────────────────────────────

    def get_total_hours(self, worker_id: str) -> float:
        """Return total hours worked, rounded to 2 decimals."""
        pass

    def get_pay(self, worker_id: str) -> float:
        """Return total pay (with overtime in Level 3+)."""
        pass

    def get_sessions(self, worker_id: str) -> list[tuple[int, int]]:
        """Return list of (check_in, check_out) tuples."""
        pass

    # ── Level 3 ────────────────────────────────────────────────────

    def get_overtime_hours(self, worker_id: str) -> dict[str, float]:
        """Return {'daily': float, 'weekly': float} overtime hours."""
        pass

    # ── Level 4 ────────────────────────────────────────────────────

    def add_department(self, dept_id: str) -> None:
        """Create a department."""
        pass

    def assign_worker(self, worker_id: str, dept_id: str) -> None:
        """Assign a worker to a department."""
        pass

    def get_department_payroll(self, dept_id: str,
                               start: int, end: int) -> dict:
        """Payroll report for a department within a time range."""
        pass

    def get_top_earners(self, n: int) -> list[tuple[str, float]]:
        """Top N workers by total pay, descending."""
        pass

    def generate_report(self, start: int, end: int) -> dict:
        """Summary report across all departments."""
        pass
