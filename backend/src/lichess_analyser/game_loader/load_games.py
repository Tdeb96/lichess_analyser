from pathlib import Path
from typing import List, Sequence

import chess.pgn


class LichessGameLoader:
    """Loader for Lichess PGN files (typing-only version)."""

    def __init__(self, pgn_file_path: str | Path) -> None:
        self.pgn_file_path: Path = Path(pgn_file_path)

    def load_games(self) -> List[chess.pgn.Game]:
        games: List[chess.pgn.Game] = []
        with open(self.pgn_file_path, "r", encoding="utf-8") as pgn_file:
            while True:
                game = chess.pgn.read_game(pgn_file)
                if game is None:
                    break
                games.append(game)
        return games

    def get_last_n_games(
        self, games: Sequence[chess.pgn.Game], n: int
    ) -> List[chess.pgn.Game]:
        return list(games[-n:]) if len(games) >= n else list(games)


if __name__ == "__main__":
    loader = LichessGameLoader("data/lichess_games.pgn")
    all_games = loader.load_games()
    print(f"Total games loaded: {len(all_games)}")

    recent_games = loader.get_last_n_games(all_games, 5)
    print(f"Last 5 games loaded: {len(recent_games)}")

    for game in recent_games:
        print(game.headers)
