"""Employee Time Tracker — Tests by Level

Run all:       pytest test_time_tracker.py
Run by level:  pytest test_time_tracker.py -k "TestLevel1"
               pytest test_time_tracker.py -k "TestLevel2"
               pytest test_time_tracker.py -k "TestLevel3"
               pytest test_time_tracker.py -k "TestLevel4"
"""

import pytest

from solution import TimeTracker


# Helper: epoch seconds for a given hour offset from day 0
def ts(day: int = 0, hour: float = 0.0) -> int:
    """Return epoch timestamp for the given day and hour (UTC)."""
    return int(day * 86400 + hour * 3600)


# ── Level 1: Basic Check-in / Check-out ───────────────────────────


class TestLevel1:
    def test_add_worker(self):
        t = TimeTracker()
        t.add_worker("W1", 15.0)

    def test_add_duplicate_worker_raises(self):
        t = TimeTracker()
        t.add_worker("W1", 15.0)
        with pytest.raises(ValueError):
            t.add_worker("W1", 20.0)

    def test_check_in_and_out(self):
        t = TimeTracker()
        t.add_worker("W1", 15.0)
        t.check_in("W1", ts(0, 9))
        t.check_out("W1", ts(0, 17))

    def test_check_in_unknown_worker_raises(self):
        t = TimeTracker()
        with pytest.raises(ValueError):
            t.check_in("UNKNOWN", ts(0, 9))

    def test_check_out_unknown_worker_raises(self):
        t = TimeTracker()
        with pytest.raises(ValueError):
            t.check_out("UNKNOWN", ts(0, 17))

    def test_double_check_in_raises(self):
        t = TimeTracker()
        t.add_worker("W1", 15.0)
        t.check_in("W1", ts(0, 9))
        with pytest.raises(ValueError):
            t.check_in("W1", ts(0, 10))

    def test_check_out_without_check_in_raises(self):
        t = TimeTracker()
        t.add_worker("W1", 15.0)
        with pytest.raises(ValueError):
            t.check_out("W1", ts(0, 17))

    def test_check_out_before_check_in_raises(self):
        t = TimeTracker()
        t.add_worker("W1", 15.0)
        t.check_in("W1", ts(0, 17))
        with pytest.raises(ValueError):
            t.check_out("W1", ts(0, 9))

    def test_multiple_sessions(self):
        t = TimeTracker()
        t.add_worker("W1", 15.0)
        t.check_in("W1", ts(0, 9))
        t.check_out("W1", ts(0, 12))
        t.check_in("W1", ts(0, 13))
        t.check_out("W1", ts(0, 17))

    def test_multiple_workers(self):
        t = TimeTracker()
        t.add_worker("W1", 15.0)
        t.add_worker("W2", 20.0)
        t.check_in("W1", ts(0, 9))
        t.check_in("W2", ts(0, 9))
        t.check_out("W1", ts(0, 17))
        t.check_out("W2", ts(0, 17))


# ── Level 2: Hours and Pay ────────────────────────────────────────


class TestLevel2:
    def test_total_hours_single_session(self):
        t = TimeTracker()
        t.add_worker("W1", 15.0)
        t.check_in("W1", ts(0, 9))
        t.check_out("W1", ts(0, 17))
        assert t.get_total_hours("W1") == 8.0

    def test_total_hours_multiple_sessions(self):
        t = TimeTracker()
        t.add_worker("W1", 15.0)
        t.check_in("W1", ts(0, 9))
        t.check_out("W1", ts(0, 12))
        t.check_in("W1", ts(0, 13))
        t.check_out("W1", ts(0, 17))
        assert t.get_total_hours("W1") == 7.0

    def test_total_hours_no_sessions(self):
        t = TimeTracker()
        t.add_worker("W1", 15.0)
        assert t.get_total_hours("W1") == 0.0

    def test_pay_simple(self):
        t = TimeTracker()
        t.add_worker("W1", 15.0)
        t.check_in("W1", ts(0, 9))
        t.check_out("W1", ts(0, 17))
        assert t.get_pay("W1") == 120.0  # 8h * $15

    def test_pay_different_wage(self):
        t = TimeTracker()
        t.add_worker("W1", 25.0)
        t.check_in("W1", ts(0, 9))
        t.check_out("W1", ts(0, 13))
        assert t.get_pay("W1") == 100.0  # 4h * $25

    def test_get_sessions(self):
        t = TimeTracker()
        t.add_worker("W1", 15.0)
        t.check_in("W1", ts(0, 9))
        t.check_out("W1", ts(0, 12))
        t.check_in("W1", ts(0, 13))
        t.check_out("W1", ts(0, 17))
        sessions = t.get_sessions("W1")
        assert len(sessions) == 2
        assert sessions[0] == (ts(0, 9), ts(0, 12))
        assert sessions[1] == (ts(0, 13), ts(0, 17))

    def test_partial_hours(self):
        t = TimeTracker()
        t.add_worker("W1", 10.0)
        t.check_in("W1", ts(0, 0))
        t.check_out("W1", ts(0, 1.5))
        assert t.get_total_hours("W1") == 1.5

    def test_total_hours_unknown_worker_raises(self):
        t = TimeTracker()
        with pytest.raises(ValueError):
            t.get_total_hours("FAKE")


# ── Level 3: Overtime ─────────────────────────────────────────────


class TestLevel3:
    def test_no_overtime_under_8h(self):
        t = TimeTracker()
        t.add_worker("W1", 20.0)
        t.check_in("W1", ts(0, 9))
        t.check_out("W1", ts(0, 17))
        ot = t.get_overtime_hours("W1")
        assert ot["daily"] == 0.0
        assert ot["weekly"] == 0.0

    def test_daily_overtime_over_8h(self):
        t = TimeTracker()
        t.add_worker("W1", 20.0)
        t.check_in("W1", ts(0, 8))
        t.check_out("W1", ts(0, 18))  # 10 hours
        ot = t.get_overtime_hours("W1")
        assert ot["daily"] == 2.0

    def test_daily_overtime_pay(self):
        t = TimeTracker()
        t.add_worker("W1", 20.0)
        t.check_in("W1", ts(0, 8))
        t.check_out("W1", ts(0, 18))  # 10h: 8 regular + 2 daily OT
        pay = t.get_pay("W1")
        # 8 * 20 + 2 * 20 * 1.5 = 160 + 60 = 220
        assert pay == 220.0

    def test_weekly_overtime_over_40h(self):
        t = TimeTracker()
        t.add_worker("W1", 20.0)
        # Work 8h/day Mon-Fri = 40h, then 4h on Saturday
        # Day 0 = Thursday Jan 1 1970, let's use specific days
        # Use days 4-8 (Mon-Fri of first full week) and day 9 (Sat)
        for day in range(4, 9):  # Mon(4) to Fri(8)
            t.check_in("W1", ts(day, 9))
            t.check_out("W1", ts(day, 17))
        # Saturday: 4 more hours
        t.check_in("W1", ts(9, 9))
        t.check_out("W1", ts(9, 13))
        ot = t.get_overtime_hours("W1")
        assert ot["daily"] == 0.0
        assert ot["weekly"] == 4.0

    def test_weekly_overtime_pay(self):
        t = TimeTracker()
        t.add_worker("W1", 10.0)
        # 5 days × 8h = 40h + 2h on day 6
        for day in range(4, 9):
            t.check_in("W1", ts(day, 9))
            t.check_out("W1", ts(day, 17))
        t.check_in("W1", ts(9, 9))
        t.check_out("W1", ts(9, 11))  # 2h
        pay = t.get_pay("W1")
        # 40 * 10 + 2 * 10 * 2.0 = 400 + 40 = 440
        assert pay == 440.0

    def test_combined_daily_and_weekly_overtime(self):
        t = TimeTracker()
        t.add_worker("W1", 10.0)
        # Work 10h/day for 5 days = 50h total
        # Daily OT: 2h/day * 5 = 10h
        # Regular hours: 8h/day * 5 = 40h — no weekly OT
        for day in range(4, 9):
            t.check_in("W1", ts(day, 7))
            t.check_out("W1", ts(day, 17))  # 10h
        ot = t.get_overtime_hours("W1")
        assert ot["daily"] == 10.0
        assert ot["weekly"] == 0.0

    def test_overtime_session_spans_midnight(self):
        t = TimeTracker()
        t.add_worker("W1", 20.0)
        # 10h session spanning midnight
        t.check_in("W1", ts(0, 20))
        t.check_out("W1", ts(1, 6))
        ot = t.get_overtime_hours("W1")
        # Day 0: 4h, Day 1: 6h — neither exceeds 8
        assert ot["daily"] == 0.0

    def test_no_sessions_no_overtime(self):
        t = TimeTracker()
        t.add_worker("W1", 20.0)
        ot = t.get_overtime_hours("W1")
        assert ot["daily"] == 0.0
        assert ot["weekly"] == 0.0


# ── Level 4: Departments and Reports ─────────────────────────────


class TestLevel4:
    def _setup_tracker(self):
        t = TimeTracker()
        t.add_worker("W1", 20.0)
        t.add_worker("W2", 25.0)
        t.add_worker("W3", 15.0)
        t.add_department("ENG")
        t.add_department("SALES")
        t.assign_worker("W1", "ENG")
        t.assign_worker("W2", "ENG")
        t.assign_worker("W3", "SALES")
        return t

    def test_add_department(self):
        t = TimeTracker()
        t.add_department("ENG")

    def test_add_duplicate_department_raises(self):
        t = TimeTracker()
        t.add_department("ENG")
        with pytest.raises(ValueError):
            t.add_department("ENG")

    def test_assign_worker(self):
        t = TimeTracker()
        t.add_worker("W1", 15.0)
        t.add_department("ENG")
        t.assign_worker("W1", "ENG")

    def test_assign_unknown_worker_raises(self):
        t = TimeTracker()
        t.add_department("ENG")
        with pytest.raises(ValueError):
            t.assign_worker("FAKE", "ENG")

    def test_assign_unknown_dept_raises(self):
        t = TimeTracker()
        t.add_worker("W1", 15.0)
        with pytest.raises(ValueError):
            t.assign_worker("W1", "FAKE")

    def test_department_payroll(self):
        t = self._setup_tracker()
        t.check_in("W1", ts(0, 9))
        t.check_out("W1", ts(0, 17))  # 8h
        t.check_in("W2", ts(0, 9))
        t.check_out("W2", ts(0, 13))  # 4h
        report = t.get_department_payroll("ENG", 0, ts(1, 0))
        assert report["dept_id"] == "ENG"
        assert report["total_hours"] == 12.0
        assert len(report["workers"]) == 2

    def test_department_payroll_time_filter(self):
        t = self._setup_tracker()
        t.check_in("W1", ts(0, 9))
        t.check_out("W1", ts(0, 17))
        t.check_in("W1", ts(5, 9))
        t.check_out("W1", ts(5, 17))
        # Only include day 0
        report = t.get_department_payroll("ENG", 0, ts(1, 0))
        w1 = next(w for w in report["workers"] if w["worker_id"] == "W1")
        assert w1["hours"] == 8.0

    def test_top_earners(self):
        t = self._setup_tracker()
        t.check_in("W1", ts(0, 9))
        t.check_out("W1", ts(0, 17))  # 8h * $20 = $160
        t.check_in("W2", ts(0, 9))
        t.check_out("W2", ts(0, 17))  # 8h * $25 = $200
        t.check_in("W3", ts(0, 9))
        t.check_out("W3", ts(0, 13))  # 4h * $15 = $60
        top = t.get_top_earners(2)
        assert top[0] == ("W2", 200.0)
        assert top[1] == ("W1", 160.0)

    def test_generate_report(self):
        t = self._setup_tracker()
        t.check_in("W1", ts(0, 9))
        t.check_out("W1", ts(0, 17))
        t.check_in("W3", ts(0, 9))
        t.check_out("W3", ts(0, 13))
        report = t.generate_report(0, ts(1, 0))
        assert "ENG" in report["departments"]
        assert "SALES" in report["departments"]
        assert report["total_hours"] == 12.0

    def test_top_earners_empty(self):
        t = TimeTracker()
        assert t.get_top_earners(5) == []

    def test_department_payroll_unknown_raises(self):
        t = TimeTracker()
        with pytest.raises(ValueError):
            t.get_department_payroll("FAKE", 0, 100)
