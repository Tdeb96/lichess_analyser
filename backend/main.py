from lichess_analyser.game_loader import LichessGameLoader


def main():
    game_loader = LichessGameLoader("data/lichess_games.pgn")
    games = game_loader.load_games()
    print(f"Total games loaded: {len(games)}")


if __name__ == "__main__":
    main()
