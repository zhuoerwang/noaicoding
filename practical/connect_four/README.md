# Connect Four

> ICF-Style System Design — 4 progressive levels, ~90 minutes

Design and implement a Connect Four game with variable grid size, win detection, score tracking, and undo/redo.

---

## Level 1: Basic Game

Implement a two-player Connect Four game on a variable-size grid.

### Constructor

```python
Game(rows: int, cols: int, target: int)
```

Creates a game with the given grid dimensions. `target` is how many in a row to win (e.g., 4).

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `drop(player: int, col: int)` | `int` | Drop a disc in column, return the row it lands on |
| `get_winner()` | `int \| None` | Return winning player (1 or 2) or None |
| `get_board()` | `list[list[int]]` | Return the board state (0=empty, 1=P1, 2=P2) |

### Rules

- Two players: player 1 and player 2
- Discs drop to the lowest empty row in the column (gravity)
- Win = `target` consecutive discs horizontally, vertically, or diagonally
- `drop()` raises `ValueError` if column is full or out of bounds
- `drop()` raises `ValueError` if it's not that player's turn (player 1 goes first)
- `drop()` raises `ValueError` if the game is already won

### Example

```python
game = Game(6, 7, 4)
game.drop(1, 3)  # → 5 (bottom row)
game.drop(2, 3)  # → 4
game.drop(1, 4)  # → 5
```

---

## Level 2: Score Tracking and Series

Add score tracking across multiple rounds with best-of-N series.

**All Level 1 tests must still pass.**

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `reset()` | `None` | Clear the board for a new round (loser goes first, or player 1 if draw) |
| `get_score()` | `dict[int, int]` | Return `{1: wins_p1, 2: wins_p2}` |
| `is_draw()` | `bool` | True if board is full with no winner |

### Rules

- When a player wins, their score increments automatically
- `reset()` starts a new round; the losing player goes first next round
- If the round was a draw, player 1 goes first

---

## Level 3: Undo / Redo and Move History

Add undo, redo, and move history tracking.

**All Level 1–2 tests must still pass.**

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `undo()` | `tuple[int, int]` | Undo last move, return `(player, col)` |
| `redo()` | `tuple[int, int]` | Redo last undone move, return `(player, col)` |
| `get_move_history()` | `list[tuple[int, int]]` | Return list of `(player, col)` moves |

### Rules

- `undo()` raises `ValueError` if no moves to undo
- `redo()` raises `ValueError` if no moves to redo
- Making a new `drop()` after `undo()` clears the redo stack
- Undo reverses the win state if the last move was a winning move

---

## Level 4: Board Display and Game Statistics

Add string board representation and game statistics.

**All Level 1–3 tests must still pass.**

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `display()` | `str` | Pretty-print the board (`.` for empty, `X` for P1, `O` for P2) |
| `get_stats()` | `dict` | Game statistics |
| `get_column_heights()` | `list[int]` | Number of discs in each column |

### Stats

```python
get_stats()
# → {
#     "total_moves": 12,
#     "rounds_played": 3,
#     "score": {1: 2, 2: 1},
#     "longest_streak": 4,  # longest consecutive by any player this round
# }
```
