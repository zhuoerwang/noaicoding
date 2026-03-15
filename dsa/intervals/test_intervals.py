"""
Tests for Interval-Based Usage Billing
Run: pytest test_intervals.py -v
"""

import pytest

from intervals import calculate_charge


# ============================================================
# Level 1: Single Price Override
# ============================================================

class TestLevel1:
    def test_no_overlap_usage_before(self):
        assert calculate_charge([[1, 5]], 10, [[6, 10, 2]]) == 40

    def test_no_overlap_usage_after(self):
        assert calculate_charge([[10, 15]], 10, [[1, 5, 2]]) == 50

    def test_full_overlap_usage_within_override(self):
        assert calculate_charge([[3, 7]], 10, [[1, 10, 2]]) == 8

    def test_full_overlap_exact_match(self):
        assert calculate_charge([[1, 10]], 10, [[1, 10, 2]]) == 18

    def test_partial_overlap_override_starts_mid_usage(self):
        """Override starts in the middle of the usage interval."""
        assert calculate_charge([[1, 8]], 10, [[5, 15, 3]]) == 49  # 4×10 + 3×3

    def test_partial_overlap_override_ends_mid_usage(self):
        """Override ends in the middle of the usage interval."""
        assert calculate_charge([[5, 15]], 10, [[1, 10, 3]]) == 65  # 5×3 + 5×10

    def test_override_inside_usage(self):
        """Override is entirely inside usage — splits into 3 segments."""
        assert calculate_charge([[1, 10]], 5, [[3, 7, 2]]) == 33  # 2×5 + 4×2 + 3×5

    def test_multiple_usages(self):
        assert calculate_charge([[1, 5], [8, 12]], 5, [[3, 10, 2]]) == 28

    def test_empty_usages(self):
        assert calculate_charge([], 10, [[1, 5, 2]]) == 0

    def test_zero_width_usage(self):
        assert calculate_charge([[5, 5]], 10, [[1, 10, 2]]) == 0

    def test_adjacent_no_overlap(self):
        """Half-open intervals: [1,5) and [5,10) don't overlap."""
        assert calculate_charge([[1, 5]], 10, [[5, 10, 2]]) == 40

    def test_single_unit_usage(self):
        assert calculate_charge([[3, 4]], 10, [[3, 7, 2]]) == 2

    def test_single_unit_usage_no_overlap(self):
        assert calculate_charge([[3, 4]], 10, [[5, 7, 2]]) == 10

    def test_override_price_higher_than_default(self):
        """Override can be more expensive than default."""
        assert calculate_charge([[1, 5]], 2, [[1, 5, 10]]) == 40

    def test_many_usages_some_overlap(self):
        """Multiple usages, some overlap override, some don't."""
        usages = [[1, 3], [5, 8], [12, 15]]
        # override covers [4, 10)
        # [1,3) → 2×10 = 20 (no overlap)
        # [5,8) → 3×2 = 6 (full overlap)
        # [12,15) → 3×10 = 30 (no overlap)
        assert calculate_charge(usages, 10, [[4, 10, 2]]) == 56


# ============================================================
# Level 2: Multiple Non-Overlapping Overrides
# ============================================================

class TestLevel2:
    def test_single_override(self):
        """Single override in list — same as Level 1."""
        assert calculate_charge([[1, 5]], 10, [[6, 10, 2]]) == 40

    def test_usage_spans_multiple_overrides(self):
        # [1,5)=4×10 + [5,10)=5×2 + [10,15)=5×10 + [15,20)=5×3
        assert calculate_charge([[1, 20]], 10, [[5, 10, 2], [15, 25, 3]]) == 115

    def test_overrides_unsorted(self):
        """Overrides given out of order — same result."""
        assert calculate_charge([[1, 20]], 10, [[15, 25, 3], [5, 10, 2]]) == 115

    def test_usage_in_gap_between_overrides(self):
        assert calculate_charge([[11, 14]], 10, [[5, 10, 2], [15, 25, 3]]) == 30

    def test_no_overrides(self):
        assert calculate_charge([[1, 10]], 5, []) == 45

    def test_multiple_usages_multiple_overrides(self):
        # [1,3)=2×10 + [3,5)=2×2 + [8,9)=1×2 + [9,12)=3×10 + [18,20)=2×3 + [20,22)=2×10
        assert calculate_charge(
            [[1, 5], [8, 12], [18, 22]], 10,
            [[3, 9, 2], [15, 20, 3]]
        ) == 82

    def test_usage_within_single_override(self):
        assert calculate_charge([[6, 8]], 10, [[5, 10, 2], [15, 25, 3]]) == 4

    def test_usage_spans_override_exactly(self):
        assert calculate_charge([[5, 10]], 10, [[5, 10, 2]]) == 10

    def test_empty_usages(self):
        assert calculate_charge([], 10, [[5, 10, 2]]) == 0

    def test_many_overrides(self):
        """Usage passes through many small overrides."""
        # overrides: [2,4) at 1, [6,8) at 1, [10,12) at 1
        # usage: [0, 14)
        # [0,2)=2×10 + [2,4)=2×1 + [4,6)=2×10 + [6,8)=2×1 + [8,10)=2×10 + [10,12)=2×1 + [12,14)=2×10
        assert calculate_charge(
            [[0, 14]], 10,
            [[2, 4, 1], [6, 8, 1], [10, 12, 1]]
        ) == 86
