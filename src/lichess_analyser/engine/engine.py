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
                # Some builds expose version separately
                self.version = ident.get("version", "Unknown")
            self.is_initialized = True
            print(f"{self.name} ({self.version}) initialized at {self.path}.")
        except Exception as e:  # Broad catch acceptable for initialization boundary; printed with context.
            print(f"Failed to initialize engine at {self.path}: {e}")
            self.is_initialized = False

    def quit(self: "StockfishEngine") -> None:
        if self.engine:
            self.engine.quit()
            self.engine = None
            self.is_initialized = False


if __name__ == "__main__":
    engine = StockfishEngine()
    engine.initialize()
    if engine.is_initialized:
        print(
            f"Initialization successful for {engine.name} ({engine.version}) at {engine.path}."
        )
        engine.quit()
