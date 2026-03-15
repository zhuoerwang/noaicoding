from enum import Enum
from abc import ABC, abstractmethod
import copy


class Color(Enum):
    WHITE = "white"
    BLACK = "black"


class Piece(ABC):
    def __init__(self, color: Color):
        self.color = color

    @abstractmethod
    def is_valid_move(self, start_row, start_col, end_row, end_col, board) -> bool:
        pass

    @abstractmethod
    def get_symbol(self) -> str:
        pass

    def __repr__(self):
        return self.get_symbol()


class Pawn(Piece):
    def is_valid_move(self, start_row, start_col, end_row, end_col, board) -> bool:
        direction = -1 if self.color == Color.WHITE else 1
        start_rank = 6 if self.color == Color.WHITE else 1
        dr = end_row - start_row
        dc = end_col - start_col
        target = board[end_row][end_col]

        # Forward move (no capture)
        if dc == 0 and target is None:
            if dr == direction:
                return True
            if dr == 2 * direction and start_row == start_rank:
                mid_row = start_row + direction
                return board[mid_row][start_col] is None
            return False

        # Diagonal capture
        if abs(dc) == 1 and dr == direction:
            return target is not None and target.color != self.color
        return False

    def get_symbol(self) -> str:
        return "P" if self.color == Color.WHITE else "p"


class Rook(Piece):
    def is_valid_move(self, start_row, start_col, end_row, end_col, board) -> bool:
        if start_row != end_row and start_col != end_col:
            return False
        if not MovementUtil.is_path_clear_straight(start_row, start_col, end_row, end_col, board):
            return False
        target = board[end_row][end_col]
        return target is None or target.color != self.color

    def get_symbol(self) -> str:
        return "R" if self.color == Color.WHITE else "r"


class Knight(Piece):
    def is_valid_move(self, start_row, start_col, end_row, end_col, board) -> bool:
        dr = abs(end_row - start_row)
        dc = abs(end_col - start_col)
        if not ((dr == 2 and dc == 1) or (dr == 1 and dc == 2)):
            return False
        target = board[end_row][end_col]
        return target is None or target.color != self.color

    def get_symbol(self) -> str:
        return "N" if self.color == Color.WHITE else "n"


class Bishop(Piece):
    def is_valid_move(self, start_row, start_col, end_row, end_col, board) -> bool:
        if abs(end_row - start_row) != abs(end_col - start_col):
            return False
        if not MovementUtil.is_path_clear_diagonal(start_row, start_col, end_row, end_col, board):
            return False
        target = board[end_row][end_col]
        return target is None or target.color != self.color

    def get_symbol(self) -> str:
        return "B" if self.color == Color.WHITE else "b"


class Queen(Piece):
    def is_valid_move(self, start_row, start_col, end_row, end_col, board) -> bool:
        dr = abs(end_row - start_row)
        dc = abs(end_col - start_col)
        is_straight = (start_row == end_row or start_col == end_col)
        is_diagonal = (dr == dc)
        if not is_straight and not is_diagonal:
            return False
        if is_straight:
            if not MovementUtil.is_path_clear_straight(start_row, start_col, end_row, end_col, board):
                return False
        else:
            if not MovementUtil.is_path_clear_diagonal(start_row, start_col, end_row, end_col, board):
                return False
        target = board[end_row][end_col]
        return target is None or target.color != self.color

    def get_symbol(self) -> str:
        return "Q" if self.color == Color.WHITE else "q"


class King(Piece):
    def is_valid_move(self, start_row, start_col, end_row, end_col, board) -> bool:
        dr = abs(end_row - start_row)
        dc = abs(end_col - start_col)
        if dr > 1 or dc > 1:
            return False
        target = board[end_row][end_col]
        return target is None or target.color != self.color

    def get_symbol(self) -> str:
        return "K" if self.color == Color.WHITE else "k"


class MovementUtil:
    @staticmethod
    def is_path_clear_straight(start_row, start_col, end_row, end_col, board) -> bool:
        if start_row == end_row:
            step = 1 if end_col > start_col else -1
            for c in range(start_col + step, end_col, step):
                if board[start_row][c] is not None:
                    return False
        else:
            step = 1 if end_row > start_row else -1
            for r in range(start_row + step, end_row, step):
                if board[r][start_col] is not None:
                    return False
        return True

    @staticmethod
    def is_path_clear_diagonal(start_row, start_col, end_row, end_col, board) -> bool:
        row_step = 1 if end_row > start_row else -1
        col_step = 1 if end_col > start_col else -1
        r, c = start_row + row_step, start_col + col_step
        while r != end_row and c != end_col:
            if board[r][c] is not None:
                return False
            r += row_step
            c += col_step
        return True


class Board:
    def __init__(self):
        self.grid = [[None for _ in range(8)] for _ in range(8)]
        self._setup_pieces()

    def _setup_pieces(self):
        # Black pieces (top: rows 0-1)
        self.grid[0] = [
            Rook(Color.BLACK), Knight(Color.BLACK), Bishop(Color.BLACK), Queen(Color.BLACK),
            King(Color.BLACK), Bishop(Color.BLACK), Knight(Color.BLACK), Rook(Color.BLACK),
        ]
        for c in range(8):
            self.grid[1][c] = Pawn(Color.BLACK)

        # White pieces (bottom: rows 6-7)
        for c in range(8):
            self.grid[6][c] = Pawn(Color.WHITE)
        self.grid[7] = [
            Rook(Color.WHITE), Knight(Color.WHITE), Bishop(Color.WHITE), Queen(Color.WHITE),
            King(Color.WHITE), Bishop(Color.WHITE), Knight(Color.WHITE), Rook(Color.WHITE),
        ]

    def get_piece(self, row, col):
        return self.grid[row][col]

    def set_piece(self, row, col, piece):
        self.grid[row][col] = piece

    def move(self, start_row, start_col, end_row, end_col) -> bool:
        piece = self.grid[start_row][start_col]
        if piece is None:
            return False
        if start_row == end_row and start_col == end_col:
            return False
        if not piece.is_valid_move(start_row, start_col, end_row, end_col, self.grid):
            return False
        self.grid[end_row][end_col] = piece
        self.grid[start_row][start_col] = None
        return True

    def find_king(self, color: Color):
        for r in range(8):
            for c in range(8):
                p = self.grid[r][c]
                if p is not None and isinstance(p, King) and p.color == color:
                    return (r, c)
        return None

    def is_square_attacked_by(self, row, col, attacker_color: Color) -> bool:
        for r in range(8):
            for c in range(8):
                p = self.grid[r][c]
                if p is not None and p.color == attacker_color:
                    if p.is_valid_move(r, c, row, col, self.grid):
                        return True
        return False

    def clone(self):
        new_board = Board.__new__(Board)
        new_board.grid = copy.deepcopy(self.grid)
        return new_board


class ChessGame:
    def __init__(self):
        self.board = Board()
        self._current_turn = Color.WHITE
        self._move_history = []
        self._captured_pieces = {Color.WHITE: [], Color.BLACK: []}

    def get_current_turn(self) -> Color:
        return self._current_turn

    def get_board_display(self) -> str:
        lines = []
        for r in range(8):
            row_str = ""
            for c in range(8):
                p = self.board.grid[r][c]
                row_str += p.get_symbol() if p else "."
                if c < 7:
                    row_str += " "
            lines.append(row_str)
        return "\n".join(lines)

    def move(self, start_row, start_col, end_row, end_col) -> bool:
        # Boundary check
        for v in (start_row, start_col, end_row, end_col):
            if v < 0 or v > 7:
                return False

        piece = self.board.get_piece(start_row, start_col)
        if piece is None:
            return False

        # Turn enforcement
        if piece.color != self._current_turn:
            return False

        # Same square
        if start_row == end_row and start_col == end_col:
            return False

        # Cannot capture own piece
        target = self.board.get_piece(end_row, end_col)
        if target is not None and target.color == self._current_turn:
            return False

        # Validate piece movement
        if not piece.is_valid_move(start_row, start_col, end_row, end_col, self.board.grid):
            return False

        # Simulate move to check if it leaves own king in check
        sim_board = self.board.clone()
        sim_board.grid[end_row][end_col] = sim_board.grid[start_row][start_col]
        sim_board.grid[start_row][start_col] = None
        opponent = Color.BLACK if self._current_turn == Color.WHITE else Color.WHITE
        king_pos = sim_board.find_king(self._current_turn)
        if king_pos is None:
            return False
        if sim_board.is_square_attacked_by(king_pos[0], king_pos[1], opponent):
            return False

        # Execute move
        captured = self.board.get_piece(end_row, end_col)
        if captured is not None:
            self._captured_pieces[captured.color].append(captured.get_symbol())
        self.board.grid[end_row][end_col] = piece
        self.board.grid[start_row][start_col] = None
        self._move_history.append((start_row, start_col, end_row, end_col))
        self._current_turn = opponent
        return True

    def is_in_check(self, color: Color) -> bool:
        king_pos = self.board.find_king(color)
        if king_pos is None:
            return False
        opponent = Color.BLACK if color == Color.WHITE else Color.WHITE
        return self.board.is_square_attacked_by(king_pos[0], king_pos[1], opponent)

    def _has_any_legal_move(self, color: Color) -> bool:
        for r in range(8):
            for c in range(8):
                p = self.board.get_piece(r, c)
                if p is None or p.color != color:
                    continue
                for er in range(8):
                    for ec in range(8):
                        if r == er and c == ec:
                            continue
                        if not p.is_valid_move(r, c, er, ec, self.board.grid):
                            continue
                        target = self.board.get_piece(er, ec)
                        if target is not None and target.color == color:
                            continue
                        sim_board = self.board.clone()
                        sim_board.grid[er][ec] = sim_board.grid[r][c]
                        sim_board.grid[r][c] = None
                        opponent = Color.BLACK if color == Color.WHITE else Color.WHITE
                        king_pos = sim_board.find_king(color)
                        if king_pos and not sim_board.is_square_attacked_by(king_pos[0], king_pos[1], opponent):
                            return True
        return False

    def is_checkmate(self, color: Color) -> bool:
        return self.is_in_check(color) and not self._has_any_legal_move(color)

    def is_stalemate(self, color: Color) -> bool:
        return not self.is_in_check(color) and not self._has_any_legal_move(color)

    def is_game_over(self) -> bool:
        return self.is_checkmate(self._current_turn) or self.is_stalemate(self._current_turn)

    def get_move_history(self) -> list:
        return list(self._move_history)

    def get_captured_pieces(self) -> dict:
        return {k: list(v) for k, v in self._captured_pieces.items()}
