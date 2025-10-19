from __future__ import annotations

from typing import Tuple

import chess


def _count_non_pawn_material(board: chess.Board) -> Tuple[int, bool]:
    """Return (npm_total, queens_present) where npm_total sums Q=9,R=5,B=3,N=3 for both sides."""
    piece_values = {
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
    }
    npm_total = 0
    queens_present = False
    for piece_type, value in piece_values.items():
        count = len(board.pieces(piece_type, chess.WHITE)) + len(
            board.pieces(piece_type, chess.BLACK)
        )
        if piece_type == chess.QUEEN and count > 0:
            queens_present = True
        npm_total += count * value
    return npm_total, queens_present


def get_game_phase(board: chess.Board) -> str:
    """
    Material + move-number hybrid heuristic for Opening/MiddleGame/EndGame.

    Rules (recommended):
    - Opening: if fullmove_number <= 10 and npm_total >= 28 and queens present
    - EndGame: if npm_total <= 14 OR (not queens_present and npm_total <= 18)
    - MiddleGame: otherwise

    Tie-breakers:
    - If a king has moved early (castling rights lost) before move 6, treat as MiddleGame.
    """
    npm_total, queens_present = _count_non_pawn_material(board)

    fullmove = board.fullmove_number

    # Detect early king activity (lost castling rights or king not on home square)
    def king_moved_early(color: chess.Color) -> bool:
        king_sq = board.king(color)
        if king_sq is None:
            return False
        # home squares: e1 for white, e8 for black
        home_square = chess.E1 if color == chess.WHITE else chess.E8
        # If castling rights missing or king not on home, consider as moved/active
        rights = board.has_castling_rights(color)
        return (not rights and fullmove <= 6) or king_sq != home_square

    if fullmove <= 10 and npm_total >= 28 and queens_present:
        return "Opening"

    if npm_total <= 14 or (not queens_present and npm_total <= 18):
        return "EndGame"

    if (
        king_moved_early(chess.WHITE) or king_moved_early(chess.BLACK)
    ) and fullmove <= 6:
        return "MiddleGame"

    return "MiddleGame"


__all__ = ["get_game_phase"]
