"""Connect Four — Reference Solution (all levels)."""

from __future__ import annotations


class Game:
    def __init__(self, rows: int, cols: int, target: int) -> None:
        self._rows = rows
        self._cols = cols
        self._target = target
        self._board: list[list[int]] = [[0] * cols for _ in range(rows)]
        self._current_player = 1
        self._winner: int | None = None
        self._move_count = 0

        # Level 2
        self._score: dict[int, int] = {1: 0, 2: 0}
        self._rounds_played = 0
        self._first_player = 1

        # Level 3
        self._history: list[tuple[int, int, int]] = []  # (player, col, row)
        self._redo_stack: list[tuple[int, int, int]] = []

    # ── Level 1 ────────────────────────────────────────────────────

    def drop(self, player: int, col: int) -> int:
        if self._winner is not None:
            raise ValueError("Game is already won")
        if player != self._current_player:
            raise ValueError(f"Not player {player}'s turn")
        if col < 0 or col >= self._cols:
            raise ValueError(f"Column {col} out of bounds")

        # Find lowest empty row
        row = self._find_row(col)
        if row is None:
            raise ValueError(f"Column {col} is full")

        self._board[row][col] = player
        self._move_count += 1
        self._history.append((player, col, row))
        self._redo_stack.clear()

        if self._check_win(row, col, player):
            self._winner = player
            self._score[player] += 1

        self._current_player = 3 - player  # toggle 1↔2
        return row

    def get_winner(self) -> int | None:
        return self._winner

    def get_board(self) -> list[list[int]]:
        return [row[:] for row in self._board]

    # ── Level 2 ────────────────────────────────────────────────────

    def reset(self) -> None:
        if self._winner is not None:
            loser = 3 - self._winner
            self._first_player = loser
        else:
            self._first_player = 1

        self._rounds_played += 1
        self._board = [[0] * self._cols for _ in range(self._rows)]
        self._current_player = self._first_player
        self._winner = None
        self._move_count = 0
        self._history.clear()
        self._redo_stack.clear()

    def get_score(self) -> dict[int, int]:
        return dict(self._score)

    def is_draw(self) -> bool:
        return self._winner is None and self._move_count == self._rows * self._cols

    # ── Level 3 ────────────────────────────────────────────────────

    def undo(self) -> tuple[int, int]:
        if not self._history:
            raise ValueError("No moves to undo")
        player, col, row = self._history.pop()
        self._board[row][col] = 0
        self._move_count -= 1
        self._redo_stack.append((player, col, row))

        # Reverse win
        if self._winner == player:
            self._winner = None
            self._score[player] -= 1

        self._current_player = player  # it's now this player's turn again
        return player, col

    def redo(self) -> tuple[int, int]:
        if not self._redo_stack:
            raise ValueError("No moves to redo")
        player, col, row = self._redo_stack.pop()
        self._board[row][col] = player
        self._move_count += 1
        self._history.append((player, col, row))

        if self._check_win(row, col, player):
            self._winner = player
            self._score[player] += 1

        self._current_player = 3 - player
        return player, col

    def get_move_history(self) -> list[tuple[int, int]]:
        return [(p, c) for p, c, _ in self._history]

    # ── Level 4 ────────────────────────────────────────────────────

    def display(self) -> str:
        symbols = {0: ".", 1: "X", 2: "O"}
        lines = []
        for row in self._board:
            lines.append(" ".join(symbols[c] for c in row))
        return "\n".join(lines)

    def get_stats(self) -> dict:
        return {
            "total_moves": self._move_count,
            "rounds_played": self._rounds_played,
            "score": self.get_score(),
            "longest_streak": self._compute_longest_streak(),
        }

    def get_column_heights(self) -> list[int]:
        heights = []
        for c in range(self._cols):
            count = sum(1 for r in range(self._rows) if self._board[r][c] != 0)
            heights.append(count)
        return heights

    # ── Internals ─────────────────────────────────────────────────

    def _find_row(self, col: int) -> int | None:
        for r in range(self._rows - 1, -1, -1):
            if self._board[r][col] == 0:
                return r
        return None

    def _check_win(self, row: int, col: int, player: int) -> bool:
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dr, dc in directions:
            count = 1
            for sign in (1, -1):
                r, c = row + dr * sign, col + dc * sign
                while 0 <= r < self._rows and 0 <= c < self._cols and self._board[r][c] == player:
                    count += 1
                    r += dr * sign
                    c += dc * sign
            if count >= self._target:
                return True
        return False

    def _compute_longest_streak(self) -> int:
        best = 0
        for r in range(self._rows):
            for c in range(self._cols):
                if self._board[r][c] == 0:
                    continue
                player = self._board[r][c]
                for dr, dc in [(0, 1), (1, 0), (1, 1), (1, -1)]:
                    count = 0
                    rr, cc = r, c
                    while 0 <= rr < self._rows and 0 <= cc < self._cols and self._board[rr][cc] == player:
                        count += 1
                        rr += dr
                        cc += dc
                    best = max(best, count)
        return best
