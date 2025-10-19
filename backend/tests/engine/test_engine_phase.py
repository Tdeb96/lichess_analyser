import random

import chess

from lichess_analyser.game_utils import get_game_phase


def test_opening_phase_initial_position():
    board = chess.Board()  # starting position
    phase = get_game_phase(board)
    assert phase == "Opening"


def test_opening_phase_after_10_random_moves():
    # Random quiet (non-capturing) moves for 10 plies should still be Opening
    board = chess.Board()
    random.seed(42)
    for _ in range(10):
        quiet_moves = [m for m in board.legal_moves if not board.is_capture(m)]
        if not quiet_moves:
            break
        board.push(random.choice(quiet_moves))
    phase = get_game_phase(board)
    assert phase == "Opening"


def test_middle_game_after_minor_trades():
    board = chess.Board()
    # Simulate a few common opening moves then some trades to reduce material
    moves = [
        "e4",
        "e5",
        "Nf3",
        "Nc6",
        "Bb5",
        "a6",
        "Bxc6",
        "dxc6",  # trade bishop for knight
        "Nxe5",  # speculative capture increasing imbalances
    ]
    for san in moves:
        move = board.parse_san(san)
        board.push(move)
    # Remove both queens to force transition if still present
    for square in list(board.pieces(chess.QUEEN, chess.WHITE)):
        board.remove_piece_at(square)
    for square in list(board.pieces(chess.QUEEN, chess.BLACK)):
        board.remove_piece_at(square)
    phase = get_game_phase(board)
    # With queens removed but still plenty of material, expect EndGame or MiddleGame depending on heuristic thresholds.
    assert phase in {"MiddleGame", "EndGame"}


def test_endgame_low_material():
    board = chess.Board()
    # Clear board except kings and a few pawns to reach clear endgame criteria
    for piece_type in [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]:
        for color in [chess.WHITE, chess.BLACK]:
            for square in list(board.pieces(piece_type, color)):
                board.remove_piece_at(square)
    # Leave just kings and pawns
    phase = get_game_phase(board)
    assert phase == "EndGame"


def test_endgame_extremely_low_npm_with_lone_queen():
    board = chess.Board()
    # Remove all pieces except a lone white queen and both kings
    for piece_type in [chess.ROOK, chess.BISHOP, chess.KNIGHT, chess.QUEEN]:
        for color in [chess.WHITE, chess.BLACK]:
            for square in list(board.pieces(piece_type, color)):
                board.remove_piece_at(square)
    # Add back a single white queen
    board.set_piece_at(chess.D1, chess.Piece(chess.QUEEN, chess.WHITE))
    phase = get_game_phase(board)
    assert phase == "EndGame"  # heuristic handles <=12 NPM as EndGame even with a queen
