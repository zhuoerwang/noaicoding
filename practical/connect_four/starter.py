"""Connect Four — ICF-Style System Design

Implement a Connect Four game across 4 progressive levels.

Run tests by level:
    pytest test_connect_four.py -k "TestLevel1"
    pytest test_connect_four.py -k "TestLevel2"
    pytest test_connect_four.py -k "TestLevel3"
    pytest test_connect_four.py -k "TestLevel4"
"""

from __future__ import annotations


class Game:
    """Connect Four game with variable grid, score tracking,
    undo/redo, and statistics."""

    def __init__(self, rows: int, cols: int, target: int) -> None:
        """Initialize the game board.

        Args:
            rows: Number of rows.
            cols: Number of columns.
            target: Number of consecutive discs needed to win.
        """
        pass

    # ── Level 1 ────────────────────────────────────────────────────

    def drop(self, player: int, col: int) -> int:
        """Drop a disc in a column. Returns the row it lands on."""
        pass

    def get_winner(self) -> int | None:
        """Return the winning player (1 or 2) or None."""
        pass

    def get_board(self) -> list[list[int]]:
        """Return the board state (0=empty, 1=P1, 2=P2)."""
        pass

    # ── Level 2 ────────────────────────────────────────────────────

    def reset(self) -> None:
        """Clear the board for a new round."""
        pass

    def get_score(self) -> dict[int, int]:
        """Return {1: wins_p1, 2: wins_p2}."""
        pass

    def is_draw(self) -> bool:
        """True if board is full with no winner."""
        pass

    # ── Level 3 ────────────────────────────────────────────────────

    def undo(self) -> tuple[int, int]:
        """Undo last move, return (player, col)."""
        pass

    def redo(self) -> tuple[int, int]:
        """Redo last undone move, return (player, col)."""
        pass

    def get_move_history(self) -> list[tuple[int, int]]:
        """Return list of (player, col) moves."""
        pass

    # ── Level 4 ────────────────────────────────────────────────────

    def display(self) -> str:
        """Pretty-print the board."""
        pass

    def get_stats(self) -> dict:
        """Return game statistics."""
        pass

    def get_column_heights(self) -> list[int]:
        """Return number of discs in each column."""
        pass
