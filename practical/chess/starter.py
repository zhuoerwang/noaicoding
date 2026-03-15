from enum import Enum
from abc import ABC, abstractmethod


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


class Pawn(Piece):
    def is_valid_move(self, start_row, start_col, end_row, end_col, board) -> bool:
        pass

    def get_symbol(self) -> str:
        pass


class Rook(Piece):
    def is_valid_move(self, start_row, start_col, end_row, end_col, board) -> bool:
        pass

    def get_symbol(self) -> str:
        pass


class Knight(Piece):
    def is_valid_move(self, start_row, start_col, end_row, end_col, board) -> bool:
        pass

    def get_symbol(self) -> str:
        pass


class Bishop(Piece):
    def is_valid_move(self, start_row, start_col, end_row, end_col, board) -> bool:
        pass

    def get_symbol(self) -> str:
        pass


class Queen(Piece):
    def is_valid_move(self, start_row, start_col, end_row, end_col, board) -> bool:
        pass

    def get_symbol(self) -> str:
        pass


class King(Piece):
    def is_valid_move(self, start_row, start_col, end_row, end_col, board) -> bool:
        pass

    def get_symbol(self) -> str:
        pass


class MovementUtil:
    @staticmethod
    def is_path_clear_straight(start_row, start_col, end_row, end_col, board) -> bool:
        pass

    @staticmethod
    def is_path_clear_diagonal(start_row, start_col, end_row, end_col, board) -> bool:
        pass


class Board:
    def __init__(self):
        self.grid = [[None for _ in range(8)] for _ in range(8)]

    def move(self, start_row, start_col, end_row, end_col) -> bool:
        pass


class ChessGame:
    def __init__(self):
        self.board = Board()

    def move(self, start_row, start_col, end_row, end_col) -> bool:
        pass

    def get_current_turn(self) -> Color:
        pass

    def get_board_display(self) -> str:
        pass

    def is_in_check(self, color: Color) -> bool:
        pass

    def is_checkmate(self, color: Color) -> bool:
        pass

    def is_stalemate(self, color: Color) -> bool:
        pass

    def is_game_over(self) -> bool:
        pass

    def get_move_history(self) -> list:
        pass

    def get_captured_pieces(self) -> dict:
        pass
