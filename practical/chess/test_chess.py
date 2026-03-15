import pytest
from solution import (
    Color, Piece, Pawn, Rook, Knight, Bishop, Queen, King,
    Board, ChessGame, MovementUtil,
)


# ---------------------------------------------------------------------------
# Level 1 — Board and Piece Movement
# ---------------------------------------------------------------------------
class TestLevel1:
    def test_initial_board_setup(self):
        board = Board()
        assert isinstance(board.get_piece(0, 0), Rook)
        assert board.get_piece(0, 0).color == Color.BLACK
        assert isinstance(board.get_piece(7, 4), King)
        assert board.get_piece(7, 4).color == Color.WHITE
        assert isinstance(board.get_piece(1, 3), Pawn)
        assert board.get_piece(1, 3).color == Color.BLACK
        assert isinstance(board.get_piece(6, 0), Pawn)
        assert board.get_piece(6, 0).color == Color.WHITE
        assert board.get_piece(4, 4) is None

    def test_pawn_single_forward(self):
        board = Board()
        assert board.move(6, 0, 5, 0) is True
        assert board.get_piece(5, 0).get_symbol() == "P"
        assert board.get_piece(6, 0) is None

    def test_pawn_double_forward(self):
        board = Board()
        assert board.move(6, 3, 4, 3) is True
        assert board.get_piece(4, 3).get_symbol() == "P"

    def test_pawn_double_forward_blocked(self):
        board = Board()
        board.set_piece(5, 3, Pawn(Color.BLACK))
        assert board.move(6, 3, 4, 3) is False

    def test_pawn_invalid_backward(self):
        board = Board()
        board.move(6, 0, 5, 0)
        assert board.move(5, 0, 6, 0) is False

    def test_pawn_diagonal_capture(self):
        board = Board()
        board.set_piece(5, 1, Pawn(Color.BLACK))
        assert board.move(6, 0, 5, 1) is True
        assert board.get_piece(5, 1).get_symbol() == "P"

    def test_pawn_diagonal_no_capture(self):
        board = Board()
        assert board.move(6, 0, 5, 1) is False

    def test_rook_straight_move(self):
        board = Board()
        board.grid = [[None]*8 for _ in range(8)]
        board.set_piece(4, 4, Rook(Color.WHITE))
        assert board.move(4, 4, 4, 7) is True
        assert board.get_piece(4, 7).get_symbol() == "R"

    def test_rook_blocked(self):
        board = Board()
        board.grid = [[None]*8 for _ in range(8)]
        board.set_piece(4, 0, Rook(Color.WHITE))
        board.set_piece(4, 3, Pawn(Color.WHITE))
        assert board.move(4, 0, 4, 5) is False

    def test_knight_l_shape(self):
        board = Board()
        assert board.move(7, 1, 5, 2) is True
        assert board.get_piece(5, 2).get_symbol() == "N"

    def test_knight_can_jump(self):
        board = Board()
        # Knight at 7,1 can jump over pawns on row 6
        assert board.move(7, 1, 5, 0) is True

    def test_bishop_diagonal(self):
        board = Board()
        board.grid = [[None]*8 for _ in range(8)]
        board.set_piece(4, 4, Bishop(Color.WHITE))
        assert board.move(4, 4, 2, 6) is True

    def test_bishop_blocked(self):
        board = Board()
        board.grid = [[None]*8 for _ in range(8)]
        board.set_piece(4, 4, Bishop(Color.WHITE))
        board.set_piece(3, 5, Pawn(Color.BLACK))
        assert board.move(4, 4, 2, 6) is False

    def test_queen_straight_and_diagonal(self):
        board = Board()
        board.grid = [[None]*8 for _ in range(8)]
        board.set_piece(4, 4, Queen(Color.WHITE))
        assert board.move(4, 4, 4, 7) is True
        board.set_piece(4, 4, Queen(Color.WHITE))
        assert board.move(4, 4, 2, 2) is True

    def test_king_one_square(self):
        board = Board()
        board.grid = [[None]*8 for _ in range(8)]
        board.set_piece(4, 4, King(Color.WHITE))
        assert board.move(4, 4, 3, 4) is True
        assert board.move(3, 4, 1, 4) is False  # too far


# ---------------------------------------------------------------------------
# Level 2 — Game and Turn Enforcement
# ---------------------------------------------------------------------------
class TestLevel2:
    def test_white_moves_first(self):
        game = ChessGame()
        assert game.get_current_turn() == Color.WHITE

    def test_turn_alternates(self):
        game = ChessGame()
        game.move(6, 4, 4, 4)  # white pawn
        assert game.get_current_turn() == Color.BLACK
        game.move(1, 4, 3, 4)  # black pawn
        assert game.get_current_turn() == Color.WHITE

    def test_cannot_move_opponent_piece(self):
        game = ChessGame()
        assert game.move(1, 0, 2, 0) is False  # black pawn on white's turn

    def test_cannot_capture_own_piece(self):
        game = ChessGame()
        assert game.move(7, 0, 6, 0) is False  # rook into own pawn

    def test_boundary_validation(self):
        game = ChessGame()
        assert game.move(6, 0, 4, -1) is False
        assert game.move(6, 0, 8, 0) is False

    def test_move_empty_square(self):
        game = ChessGame()
        assert game.move(4, 4, 3, 4) is False

    def test_board_display(self):
        game = ChessGame()
        display = game.get_board_display()
        lines = display.strip().split("\n")
        assert len(lines) == 8
        assert lines[0] == "r n b q k b n r"
        assert lines[7] == "R N B Q K B N R"
        assert lines[6] == "P P P P P P P P"

    def test_failed_move_no_turn_change(self):
        game = ChessGame()
        game.move(6, 0, 3, 0)  # invalid pawn triple forward
        assert game.get_current_turn() == Color.WHITE

    def test_sequence_of_moves(self):
        game = ChessGame()
        assert game.move(6, 4, 4, 4) is True  # e2-e4
        assert game.move(1, 4, 3, 4) is True  # e7-e5
        assert game.move(7, 6, 5, 5) is True  # Nf3
        assert game.move(0, 1, 2, 2) is True  # Nc6

    def test_same_square_move(self):
        game = ChessGame()
        assert game.move(6, 0, 6, 0) is False


# ---------------------------------------------------------------------------
# Level 3 — Check Detection
# ---------------------------------------------------------------------------
class TestLevel3:
    def _clear_and_place(self, game, pieces):
        """Helper: clear board and place pieces. pieces = [(row, col, PieceInstance), ...]"""
        game.board.grid = [[None]*8 for _ in range(8)]
        for r, c, p in pieces:
            game.board.set_piece(r, c, p)

    def test_not_in_check_initial(self):
        game = ChessGame()
        assert game.is_in_check(Color.WHITE) is False
        assert game.is_in_check(Color.BLACK) is False

    def test_rook_gives_check(self):
        game = ChessGame()
        self._clear_and_place(game, [
            (0, 4, King(Color.BLACK)),
            (7, 4, King(Color.WHITE)),
            (0, 0, Rook(Color.WHITE)),
        ])
        assert game.is_in_check(Color.BLACK) is True

    def test_bishop_gives_check(self):
        game = ChessGame()
        self._clear_and_place(game, [
            (0, 0, King(Color.BLACK)),
            (7, 7, King(Color.WHITE)),
            (3, 3, Bishop(Color.WHITE)),
        ])
        assert game.is_in_check(Color.BLACK) is True

    def test_knight_gives_check(self):
        game = ChessGame()
        self._clear_and_place(game, [
            (0, 4, King(Color.BLACK)),
            (7, 4, King(Color.WHITE)),
            (2, 3, Knight(Color.WHITE)),
        ])
        assert game.is_in_check(Color.BLACK) is True

    def test_cannot_move_into_check(self):
        game = ChessGame()
        self._clear_and_place(game, [
            (0, 0, Rook(Color.BLACK)),
            (7, 1, King(Color.WHITE)),
        ])
        game._current_turn = Color.WHITE
        # Moving king to col 0 would put it on the rook's file
        assert game.move(7, 1, 7, 0) is False

    def test_must_escape_check(self):
        game = ChessGame()
        self._clear_and_place(game, [
            (0, 0, Rook(Color.BLACK)),
            (7, 0, King(Color.WHITE)),
            (6, 5, Pawn(Color.WHITE)),
        ])
        game._current_turn = Color.WHITE
        assert game.is_in_check(Color.WHITE) is True
        # Moving a pawn doesn't resolve check
        assert game.move(6, 5, 5, 5) is False
        # Moving king out of the file resolves check
        assert game.move(7, 0, 7, 1) is True

    def test_block_check(self):
        game = ChessGame()
        self._clear_and_place(game, [
            (0, 4, Rook(Color.BLACK)),
            (7, 4, King(Color.WHITE)),
            (5, 3, Rook(Color.WHITE)),
        ])
        game._current_turn = Color.WHITE
        assert game.is_in_check(Color.WHITE) is True
        # Block the check with our rook
        assert game.move(5, 3, 5, 4) is True
        assert game.is_in_check(Color.WHITE) is False

    def test_capture_attacker_to_escape_check(self):
        game = ChessGame()
        self._clear_and_place(game, [
            (6, 4, Rook(Color.BLACK)),
            (7, 4, King(Color.WHITE)),
        ])
        game._current_turn = Color.WHITE
        assert game.is_in_check(Color.WHITE) is True
        assert game.move(7, 4, 6, 4) is True  # King captures rook
        assert game.is_in_check(Color.WHITE) is False

    def test_pinned_piece_cannot_move(self):
        game = ChessGame()
        self._clear_and_place(game, [
            (0, 4, Rook(Color.BLACK)),
            (4, 4, Bishop(Color.WHITE)),  # pinned to king
            (7, 4, King(Color.WHITE)),
        ])
        game._current_turn = Color.WHITE
        # Bishop is pinned — moving it off the file exposes king
        assert game.move(4, 4, 3, 3) is False

    def test_queen_gives_check(self):
        game = ChessGame()
        self._clear_and_place(game, [
            (0, 0, King(Color.BLACK)),
            (7, 7, King(Color.WHITE)),
            (0, 5, Queen(Color.WHITE)),
        ])
        assert game.is_in_check(Color.BLACK) is True


# ---------------------------------------------------------------------------
# Level 4 — Checkmate, Stalemate, History
# ---------------------------------------------------------------------------
class TestLevel4:
    def _clear_and_place(self, game, pieces):
        game.board.grid = [[None]*8 for _ in range(8)]
        for r, c, p in pieces:
            game.board.set_piece(r, c, p)

    def test_scholars_mate(self):
        """Classic 4-move checkmate."""
        game = ChessGame()
        assert game.move(6, 4, 4, 4) is True   # 1. e4
        assert game.move(1, 4, 3, 4) is True   # 1... e5
        assert game.move(7, 5, 4, 2) is True   # 2. Bc4
        assert game.move(1, 0, 2, 0) is True   # 2... a6
        assert game.move(7, 3, 3, 7) is True   # 3. Qh5
        assert game.move(1, 1, 2, 1) is True   # 3... b6
        assert game.move(3, 7, 1, 5) is True   # 4. Qxf7#
        assert game.is_in_check(Color.BLACK) is True
        assert game.is_checkmate(Color.BLACK) is True
        assert game.is_game_over() is True

    def test_not_checkmate_can_escape(self):
        game = ChessGame()
        self._clear_and_place(game, [
            (0, 4, King(Color.BLACK)),
            (7, 4, King(Color.WHITE)),
            (0, 0, Rook(Color.WHITE)),
        ])
        game._current_turn = Color.BLACK
        assert game.is_in_check(Color.BLACK) is True
        assert game.is_checkmate(Color.BLACK) is False  # king can move

    def test_back_rank_checkmate(self):
        game = ChessGame()
        self._clear_and_place(game, [
            (0, 7, King(Color.BLACK)),
            (1, 5, Pawn(Color.BLACK)),
            (1, 6, Pawn(Color.BLACK)),
            (1, 7, Pawn(Color.BLACK)),
            (7, 4, King(Color.WHITE)),
            (5, 0, Rook(Color.WHITE)),
        ])
        game._current_turn = Color.WHITE
        assert game.move(5, 0, 0, 0) is True  # Rook to back rank
        assert game.is_in_check(Color.BLACK) is True
        assert game.is_checkmate(Color.BLACK) is True

    def test_stalemate_basic(self):
        game = ChessGame()
        self._clear_and_place(game, [
            (0, 0, King(Color.BLACK)),
            (1, 2, Queen(Color.WHITE)),
            (2, 1, King(Color.WHITE)),
        ])
        game._current_turn = Color.BLACK
        assert game.is_in_check(Color.BLACK) is False
        assert game.is_stalemate(Color.BLACK) is True
        assert game.is_game_over() is True

    def test_not_stalemate_has_moves(self):
        game = ChessGame()
        self._clear_and_place(game, [
            (0, 0, King(Color.BLACK)),
            (7, 7, King(Color.WHITE)),
        ])
        game._current_turn = Color.BLACK
        assert game.is_stalemate(Color.BLACK) is False

    def test_game_not_over_initially(self):
        game = ChessGame()
        assert game.is_game_over() is False

    def test_move_history(self):
        game = ChessGame()
        game.move(6, 4, 4, 4)
        game.move(1, 4, 3, 4)
        history = game.get_move_history()
        assert len(history) == 2
        assert history[0] == (6, 4, 4, 4)
        assert history[1] == (1, 4, 3, 4)

    def test_move_history_excludes_invalid(self):
        game = ChessGame()
        game.move(6, 4, 4, 4)
        game.move(6, 3, 4, 3)  # invalid: white again
        history = game.get_move_history()
        assert len(history) == 1

    def test_captured_pieces_tracking(self):
        game = ChessGame()
        self._clear_and_place(game, [
            (4, 4, Pawn(Color.BLACK)),
            (5, 3, Pawn(Color.WHITE)),
            (7, 4, King(Color.WHITE)),
            (0, 4, King(Color.BLACK)),
        ])
        game._current_turn = Color.WHITE
        game.move(5, 3, 4, 4)  # white pawn captures black pawn
        captured = game.get_captured_pieces()
        assert "p" in captured[Color.BLACK]

    def test_captured_pieces_empty_initially(self):
        game = ChessGame()
        captured = game.get_captured_pieces()
        assert captured[Color.WHITE] == []
        assert captured[Color.BLACK] == []

    def test_checkmate_with_two_rooks(self):
        game = ChessGame()
        self._clear_and_place(game, [
            (0, 4, King(Color.BLACK)),
            (7, 4, King(Color.WHITE)),
            (1, 0, Rook(Color.WHITE)),
            (0, 7, Rook(Color.WHITE)),
        ])
        game._current_turn = Color.BLACK
        assert game.is_in_check(Color.BLACK) is True
        assert game.is_checkmate(Color.BLACK) is True

    def test_get_move_history_returns_copy(self):
        game = ChessGame()
        game.move(6, 4, 4, 4)
        h1 = game.get_move_history()
        h1.append((0, 0, 0, 0))
        assert len(game.get_move_history()) == 1
