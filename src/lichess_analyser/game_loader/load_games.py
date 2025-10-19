import chess.pgn


class LichessGameLoader:
    def __init__(self, pgn_file_path):
        self.pgn_file_path = pgn_file_path

    def load_games(self):
        games = []
        with open(self.pgn_file_path, "r", encoding="utf-8") as pgn_file:
            while True:
                game = chess.pgn.read_game(pgn_file)
                if game is None:
                    break
                games.append(game)
        return games

    def get_last_n_games(self, games, n):
        return games[-n:] if len(games) >= n else games


if __name__ == "__main__":
    loader = LichessGameLoader("data/lichess_games.pgn")
    all_games = loader.load_games()
    print(f"Total games loaded: {len(all_games)}")

    recent_games = loader.get_last_n_games(all_games, 5)
    print(f"Last 5 games loaded: {len(recent_games)}")

    for game in recent_games:
        print(game.headers)
