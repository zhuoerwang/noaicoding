"""Employee Time Tracker — Reference Solution (all levels)."""

from __future__ import annotations

from datetime import datetime, timezone
from collections import defaultdict


class TimeTracker:
    def __init__(self) -> None:
        self._workers: dict[str, float] = {}  # worker_id → hourly_wage
        self._sessions: dict[str, list[tuple[int, int]]] = defaultdict(list)
        self._checked_in: dict[str, int] = {}  # worker_id → check_in timestamp
        self._departments: dict[str, set[str]] = {}  # dept_id → set of worker_ids
        self._worker_dept: dict[str, str] = {}  # worker_id → dept_id

    # ── Level 1 ────────────────────────────────────────────────────

    def add_worker(self, worker_id: str, hourly_wage: float) -> None:
        if worker_id in self._workers:
            raise ValueError(f"Worker {worker_id} already exists")
        self._workers[worker_id] = hourly_wage

    def check_in(self, worker_id: str, timestamp: int) -> None:
        if worker_id not in self._workers:
            raise ValueError(f"Unknown worker: {worker_id}")
        if worker_id in self._checked_in:
            raise ValueError(f"Worker {worker_id} is already checked in")
        self._checked_in[worker_id] = timestamp

    def check_out(self, worker_id: str, timestamp: int) -> None:
        if worker_id not in self._workers:
            raise ValueError(f"Unknown worker: {worker_id}")
        if worker_id not in self._checked_in:
            raise ValueError(f"Worker {worker_id} is not checked in")
        check_in_ts = self._checked_in.pop(worker_id)
        if timestamp <= check_in_ts:
            raise ValueError("Check-out must be after check-in")
        self._sessions[worker_id].append((check_in_ts, timestamp))

    # ── Level 2 ────────────────────────────────────────────────────

    def get_total_hours(self, worker_id: str) -> float:
        self._validate_worker(worker_id)
        total = sum(
            (out - inn) / 3600 for inn, out in self._sessions[worker_id]
        )
        return round(total, 2)

    def get_pay(self, worker_id: str) -> float:
        self._validate_worker(worker_id)
        wage = self._workers[worker_id]
        ot = self._compute_overtime(worker_id)
        total_hours = self.get_total_hours(worker_id)
        daily_ot = ot["daily"]
        weekly_ot = ot["weekly"]
        regular = total_hours - daily_ot - weekly_ot
        return round(regular * wage + daily_ot * wage * 1.5 + weekly_ot * wage * 2.0, 2)

    def get_sessions(self, worker_id: str) -> list[tuple[int, int]]:
        self._validate_worker(worker_id)
        return list(self._sessions[worker_id])

    # ── Level 3 ────────────────────────────────────────────────────

    def get_overtime_hours(self, worker_id: str) -> dict[str, float]:
        self._validate_worker(worker_id)
        return self._compute_overtime(worker_id)

    # ── Level 4 ────────────────────────────────────────────────────

    def add_department(self, dept_id: str) -> None:
        if dept_id in self._departments:
            raise ValueError(f"Department {dept_id} already exists")
        self._departments[dept_id] = set()

    def assign_worker(self, worker_id: str, dept_id: str) -> None:
        self._validate_worker(worker_id)
        if dept_id not in self._departments:
            raise ValueError(f"Unknown department: {dept_id}")
        self._departments[dept_id].add(worker_id)
        self._worker_dept[worker_id] = dept_id

    def get_department_payroll(self, dept_id: str,
                               start: int, end: int) -> dict:
        if dept_id not in self._departments:
            raise ValueError(f"Unknown department: {dept_id}")

        workers_info = []
        total_hours = 0.0
        total_pay = 0.0

        for wid in sorted(self._departments[dept_id]):
            hours, pay = self._compute_pay_for_range(wid, start, end)
            workers_info.append({
                "worker_id": wid, "hours": round(hours, 2),
                "pay": round(pay, 2),
            })
            total_hours += hours
            total_pay += pay

        return {
            "dept_id": dept_id,
            "workers": workers_info,
            "total_hours": round(total_hours, 2),
            "total_pay": round(total_pay, 2),
        }

    def get_top_earners(self, n: int) -> list[tuple[str, float]]:
        earners = []
        for wid in self._workers:
            pay = self.get_pay(wid)
            earners.append((wid, pay))
        earners.sort(key=lambda x: -x[1])
        return earners[:n]

    def generate_report(self, start: int, end: int) -> dict:
        dept_reports = {}
        total_hours = 0.0
        total_pay = 0.0

        for dept_id in self._departments:
            report = self.get_department_payroll(dept_id, start, end)
            dept_reports[dept_id] = report
            total_hours += report["total_hours"]
            total_pay += report["total_pay"]

        return {
            "departments": dept_reports,
            "total_hours": round(total_hours, 2),
            "total_pay": round(total_pay, 2),
        }

    # ── Internals ─────────────────────────────────────────────────

    def _validate_worker(self, worker_id: str) -> None:
        if worker_id not in self._workers:
            raise ValueError(f"Unknown worker: {worker_id}")

    def _compute_overtime(self, worker_id: str,
                          sessions: list[tuple[int, int]] | None = None) -> dict[str, float]:
        if sessions is None:
            sessions = self._sessions[worker_id]

        # Daily overtime: hours > 8 per calendar day
        daily_hours: dict[int, float] = defaultdict(float)
        for inn, out in sessions:
            # Split session across calendar days
            current = inn
            while current < out:
                day = current // 86400
                day_end = (day + 1) * 86400
                segment_end = min(out, day_end)
                hours = (segment_end - current) / 3600
                daily_hours[day] += hours
                current = segment_end

        daily_ot = sum(max(0, h - 8) for h in daily_hours.values())

        # Weekly overtime: hours > 40 per ISO week
        weekly_hours: dict[tuple[int, int], float] = defaultdict(float)
        for day, hours in daily_hours.items():
            dt = datetime.fromtimestamp(day * 86400, tz=timezone.utc)
            iso_year, iso_week, _ = dt.isocalendar()
            weekly_hours[(iso_year, iso_week)] += hours

        weekly_ot = 0.0
        for week_key, total in weekly_hours.items():
            # Subtract daily OT hours for this week to get regular hours
            regular_in_week = 0.0
            for day, hours in daily_hours.items():
                dt = datetime.fromtimestamp(day * 86400, tz=timezone.utc)
                iy, iw, _ = dt.isocalendar()
                if (iy, iw) == week_key:
                    regular_in_week += min(hours, 8)
            weekly_ot += max(0, regular_in_week - 40)

        return {
            "daily": round(daily_ot, 2),
            "weekly": round(weekly_ot, 2),
        }

    def _compute_pay_for_range(self, worker_id: str,
                                start: int, end: int) -> tuple[float, float]:
        sessions = [
            (inn, out) for inn, out in self._sessions[worker_id]
            if inn >= start and out <= end
        ]
        total_hours = round(
            sum((out - inn) / 3600 for inn, out in sessions), 2
        )
        wage = self._workers[worker_id]
        ot = self._compute_overtime(worker_id, sessions)
        regular = total_hours - ot["daily"] - ot["weekly"]
        pay = regular * wage + ot["daily"] * wage * 1.5 + ot["weekly"] * wage * 2.0
        return total_hours, round(pay, 2)
