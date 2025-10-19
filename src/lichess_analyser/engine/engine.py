import shutil
from typing import Optional

import chess.engine


class StockfishEngine:
    """Wrapper for a local Stockfish binary.

    Auto-detects a Homebrew installation via ``shutil.which``; falls back to
    common default paths. After initialization, captures the engine's reported
    name and version from the UCI identification dictionary.
    """

    def __init__(self: "StockfishEngine") -> None:
        self.path: str = (
            shutil.which("stockfish")
            or "/opt/homebrew/bin/stockfish"  # Apple Silicon default
            or "/usr/local/bin/stockfish"  # Intel default
        )
        self.engine: Optional[chess.engine.SimpleEngine] = None
        self.is_initialized: bool = False
        self.name: str = "Unknown"
        self.version: str = "Unknown"

    def initialize(self: "StockfishEngine") -> None:
        try:
            self.engine = chess.engine.SimpleEngine.popen_uci(self.path)
            ident = getattr(self.engine, "id", {}) or {}
            raw_name: str = ident.get("name", "Unknown")
            parts = raw_name.split()
            if len(parts) > 1 and any(ch.isdigit() for ch in parts[-1]):
                self.name = " ".join(parts[:-1])
                self.version = parts[-1]
            else:
                self.name = raw_name
                self.version = ident.get("version", "Unknown")
            self.is_initialized = True
            print(f"{self.name} ({self.version}) initialized at {self.path}.")
        except Exception as e:
            print(f"Failed to initialize engine at {self.path}: {e}")
            self.is_initialized = False

    def quit(self: "StockfishEngine") -> None:
        if self.engine:
            self.engine.quit()
            self.engine = None
            self.is_initialized = False

    def get_game_phase(self: "StockfishEngine", board: "chess.Board") -> str:
        """
        Heuristically classify the position as Opening, MiddleGame, or EndGame.

        Approach:
        - Use total remaining non-pawn material (NPM) for both sides plus queen presence.
        - Initial NPM (excluding pawns) is 40 (QQ=18, RR=10, BBNN=12).
        - High NPM (>=32) or both queens present -> Opening unless large trades.
        - Transition with some trades and at least one queen -> MiddleGame.
        - Low NPM (<=14) or no queens with clearly reduced material -> EndGame.

        This avoids engine-specific, non-standard UCI debug commands (e.g. Stockfish's 'eval').
        """
        # Count pieces
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
            if piece_type != chess.QUEEN or count > 0:
                npm_total += count * value

        # Simple rule set
        if npm_total >= 32 and queens_present:
            return "Opening"
        if not queens_present and npm_total <= 14:
            return "EndGame"
        if npm_total <= 12:  # Extreme reduction even if a lone queen remains
            return "EndGame"
        if queens_present and npm_total < 24:
            return "MiddleGame"
        # Fallback
        if npm_total <= 18:
            return "EndGame"
        return "MiddleGame"


if __name__ == "__main__":
    engine = StockfishEngine()
    engine.initialize()
    if engine.is_initialized:
        print(
            f"Initialization successful for {engine.name} ({engine.version}) at {engine.path}."
        )
        engine.quit()
