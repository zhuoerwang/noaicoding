# Chess

Design and implement a chess game engine with piece movement validation, turn enforcement, check/checkmate detection, and game state tracking. All interaction is programmatic via method calls (no user input).

## Concepts

- **Color**: Enum with WHITE and BLACK
- **Piece**: Abstract base class with `is_valid_move()` and `get_symbol()`
- **Pieces**: Pawn, Rook, Knight, Bishop, Queen, King — each with correct movement rules
- **Board**: 8x8 grid of squares, each square holds an optional Piece
- **MovementUtil**: Validates straight and diagonal paths for blocking pieces
- **No special moves**: En passant, castling, and promotion are out of scope

### Piece Symbols

| Piece  | White | Black |
|--------|-------|-------|
| Pawn   | P     | p     |
| Rook   | R     | r     |
| Knight | N     | n     |
| Bishop | B     | b     |
| Queen  | Q     | q     |
| King   | K     | k     |

## Level 1 — Board and Piece Movement

Implement `Board()` which initializes the standard chess starting layout.

- `board.move(start_row, start_col, end_row, end_col) -> bool`
  - Returns True if the move was executed, False if invalid.
  - Validates piece-specific movement rules:
    - **Pawn**: Forward 1 square (or 2 from starting row). Captures diagonally forward by 1.
    - **Rook**: Any number of squares in a straight line (horizontal or vertical).
    - **Knight**: L-shape (2+1 or 1+2). Can jump over other pieces.
    - **Bishop**: Any number of squares diagonally.
    - **Queen**: Any number of squares in a straight line or diagonally.
    - **King**: 1 square in any direction.
  - Path blocking: All pieces except Knight are blocked by pieces in their path.
  - A piece can capture an opponent's piece on the destination square.

## Level 2 — Game and Turn Enforcement

Implement `ChessGame()` which wraps the board and manages turns.

- White moves first. Turns alternate after each successful move.
- `game.move(start_row, start_col, end_row, end_col) -> bool`
  - Cannot move an opponent's piece.
  - Cannot capture your own piece.
  - Validates board boundaries (0-7).
- `game.get_current_turn() -> Color`
- `game.get_board_display() -> str` — returns a string representation of the board.

## Level 3 — Check Detection

- `game.is_in_check(color) -> bool` — True if the given color's king is threatened by any opponent piece.
- `game.move()` must prevent moving into check (the move is rejected if it would leave your own king in check).
- If currently in check, the player must make a move that escapes check.

## Level 4 — Checkmate, Stalemate, and History

- `game.is_checkmate(color) -> bool` — True if the color is in check and has no legal move to escape.
- `game.is_stalemate(color) -> bool` — True if the color is not in check but has no legal move.
- `game.is_game_over() -> bool` — True if checkmate or stalemate has occurred for the current player.
- `game.get_move_history() -> list` — list of tuples `(start_row, start_col, end_row, end_col)` for all executed moves.
- `game.get_captured_pieces() -> dict[Color, list[str]]` — maps each color to the list of piece symbols captured from that color.
