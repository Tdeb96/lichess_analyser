import chess

from lichess_analyser.mistake_report import MistakeCategory, analyze_mistakes


def make_game_from_san(moves: list[str]) -> chess.pgn.Game:
    game = chess.pgn.Game()
    node = game
    board = game.board()
    for san in moves:
        move = board.parse_san(san)
        node = node.add_variation(move)
        board.push(move)
    game.headers["Result"] = "1-0"
    return game


def test_detect_single_blunder_white():
    # Simple game where White loses 200 centipawns on move 3
    moves = ["e4", "e5", "Qh5", "Nc6", "Bc4", "Nf6"]
    game = make_game_from_san(moves)

    # evals after each ply (White perspective). Start from 0.
    # Ply indices: 0:e4,1:e5,2:Qh5,3:Nc6,4:Bc4,5:Nf6
    evals = [20, 25, -180, -190, -170, -175]

    report = analyze_mistakes(game, evals, player_color=chess.WHITE)
    moves = report["all_moves"]
    # should have entries for each player's move (White moves at plies 0,2,4 -> 3 entries)
    assert len(moves) == 3
    bl = moves[1]  # second white move at ply 2
    assert bl["ply"] == 2
    assert bl["move_number"] == 2
    assert bl["side"] == "White"
    assert bl["category"] == MistakeCategory.MISTAKE
