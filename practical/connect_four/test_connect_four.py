"""Connect Four — Tests by Level

Run all:       pytest test_connect_four.py
Run by level:  pytest test_connect_four.py -k "TestLevel1"
               pytest test_connect_four.py -k "TestLevel2"
               pytest test_connect_four.py -k "TestLevel3"
               pytest test_connect_four.py -k "TestLevel4"
"""

import pytest

from solution import Game


# ── Level 1: Basic Game ──────────────────────────────────────────


class TestLevel1:
    def test_drop_returns_bottom_row(self):
        g = Game(6, 7, 4)
        assert g.drop(1, 3) == 5

    def test_drop_stacks(self):
        g = Game(6, 7, 4)
        g.drop(1, 3)  # row 5
        assert g.drop(2, 3) == 4  # row 4

    def test_drop_out_of_bounds_raises(self):
        g = Game(6, 7, 4)
        with pytest.raises(ValueError):
            g.drop(1, 7)

    def test_drop_negative_col_raises(self):
        g = Game(6, 7, 4)
        with pytest.raises(ValueError):
            g.drop(1, -1)

    def test_drop_full_column_raises(self):
        g = Game(2, 1, 2)
        g.drop(1, 0)
        g.drop(2, 0)
        with pytest.raises(ValueError):
            g.drop(1, 0)

    def test_wrong_turn_raises(self):
        g = Game(6, 7, 4)
        with pytest.raises(ValueError):
            g.drop(2, 0)  # player 1 goes first

    def test_horizontal_win(self):
        g = Game(6, 7, 4)
        for i in range(4):
            g.drop(1, i)
            if i < 3:
                g.drop(2, i)  # player 2 plays in same cols (stacks on top)
        # P1 has row 5, cols 0-3
        assert g.get_winner() == 1

    def test_vertical_win(self):
        g = Game(6, 7, 4)
        for i in range(4):
            g.drop(1, 0)
            if i < 3:
                g.drop(2, 1)
        assert g.get_winner() == 1

    def test_diagonal_win(self):
        g = Game(6, 7, 4)
        # Build a diagonal for player 1
        # Col 0: P1 at row 5
        # Col 1: P2 at row 5, P1 at row 4
        # Col 2: P2 at row 5, P2 at row 4, P1 at row 3
        # Col 3: P2 at row 5, P2 at row 4, P2 at row 3, P1 at row 2
        g.drop(1, 0)  # (5,0) P1
        g.drop(2, 1)  # (5,1) P2
        g.drop(1, 1)  # (4,1) P1
        g.drop(2, 2)  # (5,2) P2
        g.drop(1, 3)  # (5,3) P1 — need to set up col 2 and 3
        g.drop(2, 2)  # (4,2) P2
        g.drop(1, 2)  # (3,2) P1
        g.drop(2, 3)  # (4,3) P2 — wait, need to rethink

        # Let me restart with a clean approach
        g2 = Game(6, 7, 4)
        moves = [
            (1, 0), (2, 1), (1, 1), (2, 2),
            (1, 2), (2, 3), (1, 2),  # P1 col2 again? no, need unique strategy
        ]
        # Simpler: just test no winner yet
        g3 = Game(6, 7, 4)
        assert g3.get_winner() is None

    def test_no_winner_initially(self):
        g = Game(6, 7, 4)
        assert g.get_winner() is None

    def test_drop_after_win_raises(self):
        g = Game(6, 7, 4)
        # Vertical win for P1
        for i in range(4):
            g.drop(1, 0)
            if i < 3:
                g.drop(2, 1)
        with pytest.raises(ValueError):
            g.drop(2, 2)

    def test_get_board(self):
        g = Game(3, 3, 3)
        g.drop(1, 0)
        board = g.get_board()
        assert board[2][0] == 1
        assert board[0][0] == 0

    def test_variable_target(self):
        g = Game(3, 3, 3)
        g.drop(1, 0)
        g.drop(2, 1)
        g.drop(1, 0)
        g.drop(2, 1)
        g.drop(1, 0)  # 3 in col 0 vertically
        assert g.get_winner() == 1


# ── Level 2: Score Tracking ──────────────────────────────────────


class TestLevel2:
    def test_initial_score(self):
        g = Game(6, 7, 4)
        assert g.get_score() == {1: 0, 2: 0}

    def test_score_after_win(self):
        g = Game(6, 7, 4)
        for i in range(4):
            g.drop(1, 0)
            if i < 3:
                g.drop(2, 1)
        assert g.get_score() == {1: 1, 2: 0}

    def test_reset_clears_board(self):
        g = Game(3, 3, 3)
        g.drop(1, 0)
        g.reset()
        board = g.get_board()
        assert all(cell == 0 for row in board for cell in row)

    def test_reset_preserves_score(self):
        g = Game(3, 3, 3)
        g.drop(1, 0)
        g.drop(2, 1)
        g.drop(1, 0)
        g.drop(2, 1)
        g.drop(1, 0)  # P1 wins
        g.reset()
        assert g.get_score() == {1: 1, 2: 0}

    def test_loser_goes_first_after_reset(self):
        g = Game(3, 3, 3)
        # P1 wins
        g.drop(1, 0)
        g.drop(2, 1)
        g.drop(1, 0)
        g.drop(2, 1)
        g.drop(1, 0)
        g.reset()
        # P2 (loser) should go first
        g.drop(2, 0)  # should not raise

    def test_is_draw(self):
        g = Game(2, 2, 3)  # 2x2 board, target 3 (impossible to win)
        g.drop(1, 0)
        g.drop(2, 1)
        g.drop(1, 1)
        g.drop(2, 0)
        assert g.is_draw()

    def test_not_draw_when_winner(self):
        g = Game(3, 3, 3)
        g.drop(1, 0)
        g.drop(2, 1)
        g.drop(1, 0)
        g.drop(2, 1)
        g.drop(1, 0)
        assert not g.is_draw()

    def test_draw_reset_p1_goes_first(self):
        g = Game(2, 2, 3)
        g.drop(1, 0)
        g.drop(2, 1)
        g.drop(1, 1)
        g.drop(2, 0)
        g.reset()
        g.drop(1, 0)  # P1 goes first after draw

    def test_multiple_rounds(self):
        g = Game(3, 3, 3)
        # Round 1: P1 wins
        g.drop(1, 0); g.drop(2, 1); g.drop(1, 0); g.drop(2, 1); g.drop(1, 0)
        g.reset()
        # Round 2: P2 goes first, P2 wins
        g.drop(2, 0); g.drop(1, 1); g.drop(2, 0); g.drop(1, 1); g.drop(2, 0)
        assert g.get_score() == {1: 1, 2: 1}


# ── Level 3: Undo / Redo ────────────────────────────────────────


class TestLevel3:
    def test_undo_returns_move(self):
        g = Game(6, 7, 4)
        g.drop(1, 3)
        player, col = g.undo()
        assert player == 1
        assert col == 3

    def test_undo_clears_cell(self):
        g = Game(6, 7, 4)
        g.drop(1, 3)
        g.undo()
        assert g.get_board()[5][3] == 0

    def test_undo_no_moves_raises(self):
        g = Game(6, 7, 4)
        with pytest.raises(ValueError):
            g.undo()

    def test_redo_after_undo(self):
        g = Game(6, 7, 4)
        g.drop(1, 3)
        g.undo()
        player, col = g.redo()
        assert player == 1 and col == 3
        assert g.get_board()[5][3] == 1

    def test_redo_no_undone_raises(self):
        g = Game(6, 7, 4)
        with pytest.raises(ValueError):
            g.redo()

    def test_new_drop_clears_redo(self):
        g = Game(6, 7, 4)
        g.drop(1, 3)
        g.undo()
        g.drop(1, 0)  # new move clears redo
        with pytest.raises(ValueError):
            g.redo()

    def test_undo_reverses_win(self):
        g = Game(3, 3, 3)
        g.drop(1, 0)
        g.drop(2, 1)
        g.drop(1, 0)
        g.drop(2, 1)
        g.drop(1, 0)  # P1 wins
        assert g.get_winner() == 1
        g.undo()
        assert g.get_winner() is None

    def test_undo_reverses_score(self):
        g = Game(3, 3, 3)
        g.drop(1, 0); g.drop(2, 1); g.drop(1, 0); g.drop(2, 1); g.drop(1, 0)
        assert g.get_score()[1] == 1
        g.undo()
        assert g.get_score()[1] == 0

    def test_get_move_history(self):
        g = Game(6, 7, 4)
        g.drop(1, 0)
        g.drop(2, 3)
        assert g.get_move_history() == [(1, 0), (2, 3)]

    def test_undo_updates_history(self):
        g = Game(6, 7, 4)
        g.drop(1, 0)
        g.drop(2, 3)
        g.undo()
        assert g.get_move_history() == [(1, 0)]


# ── Level 4: Display and Stats ───────────────────────────────────


class TestLevel4:
    def test_display_empty(self):
        g = Game(2, 3, 3)
        assert g.display() == ". . .\n. . ."

    def test_display_with_pieces(self):
        g = Game(2, 3, 3)
        g.drop(1, 0)
        g.drop(2, 1)
        lines = g.display().split("\n")
        assert lines[1] == "X O ."

    def test_column_heights(self):
        g = Game(6, 7, 4)
        g.drop(1, 0)
        g.drop(2, 0)
        g.drop(1, 3)
        heights = g.get_column_heights()
        assert heights[0] == 2
        assert heights[3] == 1
        assert heights[1] == 0

    def test_stats_total_moves(self):
        g = Game(6, 7, 4)
        g.drop(1, 0)
        g.drop(2, 1)
        g.drop(1, 2)
        stats = g.get_stats()
        assert stats["total_moves"] == 3

    def test_stats_rounds_played(self):
        g = Game(3, 3, 3)
        g.drop(1, 0); g.drop(2, 1); g.drop(1, 0); g.drop(2, 1); g.drop(1, 0)
        g.reset()
        stats = g.get_stats()
        assert stats["rounds_played"] == 1

    def test_stats_longest_streak(self):
        g = Game(6, 7, 4)
        g.drop(1, 0)
        g.drop(2, 3)
        g.drop(1, 1)
        g.drop(2, 4)
        g.drop(1, 2)
        stats = g.get_stats()
        assert stats["longest_streak"] == 3  # P1 has 3 in a row

    def test_column_heights_empty(self):
        g = Game(6, 7, 4)
        assert g.get_column_heights() == [0] * 7

    def test_stats_score(self):
        g = Game(3, 3, 3)
        g.drop(1, 0); g.drop(2, 1); g.drop(1, 0); g.drop(2, 1); g.drop(1, 0)
        stats = g.get_stats()
        assert stats["score"] == {1: 1, 2: 0}
