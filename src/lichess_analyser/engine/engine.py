import os
import shutil

import chess.engine


class StockfishEngine:
    def __init__(self):
        self.path = (
            shutil.which("stockfish")
            or "/opt/homebrew/bin/stockfish"  # Apple Silicon default
            or "/usr/local/bin/stockfish"  # Intel default (will be used if previous is absent)
        )
        self.engine = None
        self.is_initialized = False

    def initialize(self):
        try:
            self.engine = chess.engine.SimpleEngine.popen_uci(self.path)
            self.is_initialized = True
            print(f"Stockfish initialized at {self.path}.")
        except Exception as e:
            print(f"Failed to initialize {self.name}: {e}")
            self.is_initialized = False

    def quit(self):
        if self.engine:
            self.engine.quit()
            self.engine = None
            self.is_initialized = False


if __name__ == "__main__":
    engine = StockfishEngine()
    engine.initialize()
    if engine.is_initialized:
        print(f"Initialization successful at {engine.path}.")
        engine.quit()
