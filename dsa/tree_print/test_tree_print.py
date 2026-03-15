"""
Tests for Pretty Print Binary Tree
Run: pytest test_tree_print.py -v
"""

import pytest

from tree_print import pretty_print


class TestPrettyPrint:
    def test_single_node(self):
        assert pretty_print([1]) == ['1']

    def test_height_2_complete(self):
        assert pretty_print([1, 2, 3]) == [' 1', '2 3']

    def test_height_2_missing_right(self):
        assert pretty_print([5, 3, None]) == [' 5', '3 *']

    def test_height_2_missing_left(self):
        assert pretty_print([1, None, 3]) == [' 1', '* 3']

    def test_height_3_complete(self):
        assert pretty_print([1, 2, 3, 4, 5, 6, 7]) == [
            '   1',
            ' 2   3',
            '4 5 6 7'
        ]

    def test_height_3_some_missing(self):
        assert pretty_print([1, 2, 3, None, 5, None, 7]) == [
            '   1',
            ' 2   3',
            '* 5 * 7'
        ]

    def test_height_3_missing_internal_children(self):
        assert pretty_print([1, 2, 3, 4, None, None, 7]) == [
            '   1',
            ' 2   3',
            '4 * * 7'
        ]

    def test_height_3_left_heavy(self):
        """Trailing Nones omitted — right subtree leaves are all *."""
        assert pretty_print([1, 2, 3, 4, 5]) == [
            '   1',
            ' 2   3',
            '4 5 * *'
        ]

    def test_height_3_right_heavy(self):
        assert pretty_print([1, 2, 3, None, None, 6, 7]) == [
            '   1',
            ' 2   3',
            '* * 6 7'
        ]

    def test_height_3_missing_right_subtree(self):
        """Right child of root is None, its children become * *."""
        assert pretty_print([1, 2, None, 4, 5]) == [
            '   1',
            ' 2   *',
            '4 5 * *'
        ]

    def test_height_4_partial(self):
        """Only nodes 8 and 9 exist at level 3, rest are *."""
        assert pretty_print([1, 2, 3, 4, 5, 6, 7, 8, 9]) == [
            '       1',
            '   2       3',
            ' 4   5   6   7',
            '8 9 * * * * * *'
        ]

    def test_height_4_complete(self):
        assert pretty_print([1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 1, 2, 3, 4, 5]) == [
            '       1',
            '   2       3',
            ' 4   5   6   7',
            '8 9 0 1 2 3 4 5'
        ]

    def test_single_chain_left(self):
        """Tree that only branches left: 1 -> 2 -> 4."""
        assert pretty_print([1, 2, None, 4]) == [
            '   1',
            ' 2   *',
            '4 * * *'
        ]

    def test_height_2_both_present(self):
        assert pretty_print([9, 0, 1]) == [' 9', '0 1']
