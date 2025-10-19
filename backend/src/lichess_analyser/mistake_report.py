from __future__ import annotations

from typing import Any, Dict, List, Optional

import chess

from lichess_analyser.game_utils import get_game_phase


class MistakeCategory:
    INACCURACY = "Inaccuracy"
    MISTAKE = "Mistake"
    BLUNDER = "Blunder"


def categorize_swing(cp: int) -> Optional[str]:
    """Categorize a negative swing (from player's POV) into Inaccuracy/Mistake/Blunder.

    cp is expected to be a positive integer magnitude (how much worse the player's position became).
    """
    if cp >= 250:
        return MistakeCategory.BLUNDER
    if cp >= 100:
        return MistakeCategory.MISTAKE
    if cp >= 50:
        return MistakeCategory.INACCURACY
    return None


def analyze_mistakes(
    game: chess.pgn.Game,
    evals: List[int],
    player_color: Optional[chess.Color] = None,
    player_name: Optional[str] = None,
    inaccuracy_threshold: int = 50,
    mistake_threshold: int = 100,
    blunder_threshold: int = 250,
    capitalize_threshold: int = 50,
    capitalize_plies: int = 1,
    losing_cp_threshold: int = 200,
    losing_min_category: str = MistakeCategory.MISTAKE,
) -> Dict[str, Any]:
    """
    Analyze a game and classify Inaccuracies/Mistakes/Blunders for the given player.

    Returns a dict with:
    - all_moves: list of dicts for all player's moves with category (or None), swing, phase, ply
    - capitalized: list of those moves where the opponent capitalized
    - losing_move: the first move (that was capitalized) after which the player was losing for the rest of the game
    """

    # Infer player color
    if player_color is None:
        if player_name is None:
            raise ValueError("Either player_color or player_name must be provided")
        white_player = game.headers.get("White", "")
        black_player = game.headers.get("Black", "")
        if player_name == white_player:
            player_color = chess.WHITE
        elif player_name == black_player:
            player_color = chess.BLACK
        else:
            raise ValueError(
                f"Player '{player_name}' not found in game. White: '{white_player}', Black: '{black_player}'"
            )

    # Build boards
    boards: List[chess.Board] = []
    board = game.board()
    boards.append(board.copy())
    for move in game.mainline_moves():
        board.push(move)
        boards.append(board.copy())

    num_plies = len(boards) - 1
    if len(evals) != num_plies:
        raise ValueError(f"Expected {num_plies} evals (plies), got {len(evals)}")

    def eval_before(ply: int) -> int:
        return evals[ply - 1] if ply > 0 else 0

    sign = 1 if player_color == chess.WHITE else -1

    player_ply_indices = [
        i
        for i in range(num_plies)
        if (i % 2 == 0 and player_color == chess.WHITE)
        or (i % 2 == 1 and player_color == chess.BLACK)
    ]

    all_moves: List[Dict[str, Any]] = []

    for ply in player_ply_indices:
        before = eval_before(ply)
        after = evals[ply]
        swing = after - before
        player_swing = sign * swing
        magnitude = -player_swing if player_swing < 0 else 0
        category = None
        if magnitude >= blunder_threshold:
            category = MistakeCategory.BLUNDER
        elif magnitude >= mistake_threshold:
            category = MistakeCategory.MISTAKE
        elif magnitude >= inaccuracy_threshold:
            category = MistakeCategory.INACCURACY

        move_entry = {
            "ply": ply,
            "move_number": (ply // 2) + 1,
            "side": "White" if (ply % 2 == 0) else "Black",
            "swing": player_swing,
            "magnitude": magnitude,
            "category": category,
            "phase": get_game_phase(boards[ply + 1]),
            "post_eval": evals[ply],
        }
        all_moves.append(move_entry)

    # Detect capitalized: opponent increases player's disadvantage by >= capitalize_threshold within capitalize_plies
    capitalized: List[Dict[str, Any]] = []
    for mv in all_moves:
        if mv["category"] is None:
            continue
        ply = mv["ply"]
        post_eval = mv["post_eval"]
        cap_found = False
        for k in range(1, capitalize_plies + 1):
            j = ply + k
            if j > len(evals) - 1:
                break
            adv_change = sign * (evals[j] - post_eval)
            if adv_change <= -capitalize_threshold:
                cap_found = True
                break
        if cap_found:
            capitalized.append(mv)

    # Losing move: first move that (a) was capitalized, (b) its category >= losing_min_category, and (c) after which the player was losing (<= -losing_cp_threshold from player's POV) for the rest of the game
    losing_move: Optional[Dict[str, Any]] = None
    category_order = {MistakeCategory.INACCURACY: 0, MistakeCategory.MISTAKE: 1, MistakeCategory.BLUNDER: 2}
    for mv in capitalized:
        if category_order.get(mv["category"], -1) < category_order.get(losing_min_category, 1):
            continue
        ply = mv["ply"]
        # ensure that for all subsequent plies, player's advantage is <= -losing_cp_threshold (player losing by at least losing_cp_threshold cp)
        rest_all_losing = True
        for j in range(ply + 1, len(evals)):
            adv = sign * evals[j]
            if adv > -losing_cp_threshold:
                rest_all_losing = False
                break
        if rest_all_losing:
            losing_move = mv
            break

    return {
        "all_moves": all_moves,
        "capitalized": capitalized,
        "losing_move": losing_move,
    }


__all__ = ["analyze_mistakes", "MistakeCategory"]
