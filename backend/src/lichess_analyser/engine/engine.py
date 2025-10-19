import shutil
from typing import Optional

import chess.engine
from tqdm import tqdm


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

    # Note: game-phase detection has been moved to `lichess_analyser.phase.get_game_phase`

    def evaluate_board_cp(
        self: "StockfishEngine", board: "chess.Board", depth: int = 12
    ) -> int:
        """
        Return a centipawn evaluation for `board` from White's perspective.

        Uses the initialized engine to analyse the position at the requested depth.
        If the engine is not initialized it will attempt to initialize it.

        Mate scores are converted to large cp integers (mate -> +/- 100000 cp).
        """
        import chess.engine

        if not self.is_initialized:
            self.initialize()
        if not self.is_initialized or self.engine is None:
            raise RuntimeError(
                "Stockfish engine is not available to evaluate positions"
            )

        try:
            info = self.engine.analyse(board, chess.engine.Limit(depth=depth))
            score = info.get("score")
            if score is None:
                raise RuntimeError("Engine returned no score")
            # Convert to White-perspective centipawns; handle mate by using a large value
            pov = score.white()
            cp = pov.score(mate_score=100000)
            if cp is None:
                # Defensive fallback
                return 0
            return int(cp)
        except Exception:
            raise

    def analyze_game_evals(
        self: "StockfishEngine",
        game: "chess.pgn.Game",
        depth: int = 12,
        verbose: bool = False,
    ) -> list[int]:
        """
        Produce a list of centipawn evaluations after each ply (half-move) for the game's mainline.

        The returned list will have length equal to the number of plies in the game's mainline.
        Each entry is an integer centipawn evaluation from White's perspective.
        """
        board = game.board()
        evals: list[int] = []
        moves = list(game.mainline_moves())

        if verbose:
            moves = tqdm(moves, desc="Analyzing positions")

        for move in moves:
            board.push(move)
            cp = self.evaluate_board_cp(board, depth=depth)
            evals.append(cp)
        return evals
        """
        Produce a list of centipawn evaluations after each ply (half-move) for the game's mainline.

        The returned list will have length equal to the number of plies in the game's mainline.
        Each entry is an integer centipawn evaluation from White's perspective.
        """
        board = game.board()
        evals: list[int] = []
        for move in game.mainline_moves():
            board.push(move)
            cp = self.evaluate_board_cp(board, depth=depth)
            evals.append(cp)
        return evals


if __name__ == "__main__":
    engine = StockfishEngine()
    engine.initialize()
    if engine.is_initialized:
        print(
            f"Initialization successful for {engine.name} ({engine.version}) at {engine.path}."
        )
        engine.quit()
