import { useState, useCallback, useRef, useEffect } from 'react';
import Chessboard from 'chessboardjsx';
import { Chess, Move } from 'chess.js';

interface DropArgs {
  sourceSquare: string;
  targetSquare: string;
  piece?: string;
}

function App() {
  const [game] = useState(() => new Chess());
  const [fen, setFen] = useState(game.fen());
  const [moves, setMoves] = useState<Move[]>([]);
  const [lastSquares, setLastSquares] = useState<{ from: string; to: string } | null>(null);
  const [pgnInput, setPgnInput] = useState('');
  const [loadedGameMoves, setLoadedGameMoves] = useState<Move[]>([]); // full move objects from parsed PGN
  const [moveIndex, setMoveIndex] = useState<number>(0); // pointer into loadedGameMoves (position after moveIndex moves)
  const [isAutoplay, setIsAutoplay] = useState(false);
  const autoplayRef = useRef<number | null>(null);

  const handleDrop = useCallback((move: DropArgs) => {
    // Disable manual dragging when a PGN is loaded (optional). Here we allow if no PGN loaded.
    if (loadedGameMoves.length > 0) return; // prevent altering loaded sequence
    const result = game.move({
      from: move.sourceSquare,
      to: move.targetSquare,
      promotion: 'q',
    });
    if (result) {
      setFen(game.fen());
      setMoves((m) => [...m, result]);
      setLastSquares({ from: result.from, to: result.to });
    } else {
      setFen(game.fen());
    }
  }, [game, loadedGameMoves.length]);

  const reset = () => {
    game.reset();
    setFen(game.fen());
    setMoves([]);
    setLastSquares(null);
    setLoadedGameMoves([]);
    setMoveIndex(0);
    setIsAutoplay(false);
    if (autoplayRef.current) {
      window.clearInterval(autoplayRef.current);
      autoplayRef.current = null;
    }
  };

  // Load PGN, parse moves, precompute sequence
  const loadPgn = () => {
    try {
      const tmp = new Chess();
      // Some versions of chess.js return boolean, others void; rely on exception or resulting history length.
      tmp.loadPgn(pgnInput);
      const historySans = tmp.history({ verbose: true });
      if (historySans.length === 0) throw new Error('No moves parsed from PGN');
      setLoadedGameMoves(historySans as Move[]);
      setMoveIndex(0);
      game.reset();
      setFen(game.fen());
      setLastSquares(null);
      setMoves([]);
    } catch (e: any) {
      alert(e.message || 'Failed to parse PGN');
    }
  };

  // Compute FEN for current moveIndex
  useEffect(() => {
    if (loadedGameMoves.length === 0) return;
    const replay = new Chess();
    let last: Move | null = null;
    for (let i = 0; i < moveIndex; i++) {
      const m = loadedGameMoves[i];
      const applied = replay.move({ from: m.from, to: m.to, promotion: m.promotion || 'q' });
      if (applied) last = applied as Move;
    }
    setFen(replay.fen());
    setLastSquares(last ? { from: last.from, to: last.to } : null);
  }, [loadedGameMoves, moveIndex]);

  // Autoplay effect
  useEffect(() => {
    if (isAutoplay && loadedGameMoves.length > 0) {
      autoplayRef.current = window.setInterval(() => {
        setMoveIndex((i) => {
          if (i < loadedGameMoves.length) return i + 1; // advance one ply
          return i; // stop at end
        });
      }, 1000);
    } else {
      if (autoplayRef.current) {
        window.clearInterval(autoplayRef.current);
        autoplayRef.current = null;
      }
    }
    return () => {
      if (autoplayRef.current) {
        window.clearInterval(autoplayRef.current);
        autoplayRef.current = null;
      }
    };
  }, [isAutoplay, loadedGameMoves.length]);

  const gotoStart = () => setMoveIndex(0);
  const gotoPrev = () => setMoveIndex((i) => Math.max(0, i - 1));
  const gotoNext = () => setMoveIndex((i) => Math.min(loadedGameMoves.length, i + 1));
  const gotoEnd = () => setMoveIndex(loadedGameMoves.length);
  const toggleAutoplay = () => setIsAutoplay((a) => !a);

  // Highlight last move squares by customizing square styles
  const squareStyles: Record<string, React.CSSProperties> = {};
  if (lastSquares) {
    squareStyles[lastSquares.from] = { background: 'rgba(255,215,0,0.6)' };
    squareStyles[lastSquares.to] = { background: 'rgba(173,216,230,0.65)' };
  }

  const playbackActive = loadedGameMoves.length > 0;
  const displayedMoves = playbackActive ? loadedGameMoves.slice(0, moveIndex) : moves;

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'flex-start',
      padding: '2rem 1rem',
      fontFamily: 'system-ui, sans-serif',
      background: 'linear-gradient(135deg, #20232a 0%, #2f3542 100%)',
      color: '#fff'
    }}>
      <h1 style={{ margin: '0 0 1rem', fontSize: '1.5rem' }}>Chess Demo / PGN Player</h1>
      <div style={{ display: 'flex', gap: '2rem', flexWrap: 'wrap', alignItems: 'flex-start', width: '100%', maxWidth: 1100 }}>
        <div style={{ boxShadow: '0 4px 16px rgba(0,0,0,0.4)', borderRadius: 8, overflow: 'hidden' }}>
          <Chessboard
            position={fen}
            onDrop={handleDrop}
            width={440}
            boardStyle={{ borderRadius: 8 }}
            squareStyles={squareStyles}
            transitionDuration={200}
          />
        </div>
        <div style={{ flex: 1, minWidth: 280, display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            <button onClick={reset} style={buttonStyle}>Reset</button>
            {playbackActive && (
              <>
                <button onClick={gotoStart} style={buttonStyle} disabled={moveIndex===0}>|◀</button>
                <button onClick={gotoPrev} style={buttonStyle} disabled={moveIndex===0}>◀</button>
                <button onClick={gotoNext} style={buttonStyle} disabled={moveIndex===loadedGameMoves.length}>▶</button>
                <button onClick={gotoEnd} style={buttonStyle} disabled={moveIndex===loadedGameMoves.length}>▶|</button>
                <button onClick={toggleAutoplay} style={buttonStyle} disabled={moveIndex===loadedGameMoves.length}>{isAutoplay ? 'Pause' : 'Autoplay'}</button>
              </>
            )}
          </div>
          <div style={{ fontSize: '0.75rem', wordBreak: 'break-all', background: '#1e1f24', padding: '0.5rem 0.75rem', borderRadius: 4 }}>
            <strong>FEN:</strong> {fen}
          </div>
          <div style={{ background: '#1e1f24', padding: '0.75rem', borderRadius: 4 }}>
            <strong style={{ fontSize: '0.8rem' }}>Paste PGN:</strong>
            <textarea
              value={pgnInput}
              onChange={(e) => setPgnInput(e.target.value)}
              placeholder={'[Event "?"]\n1. e4 e5 2. Nf3 Nc6 3. Bb5 a6'}
              style={{ width: '100%', minHeight: 120, marginTop: 4, resize: 'vertical', background: '#262830', color: '#fff', border: '1px solid #444', borderRadius: 4, fontSize: '0.75rem', padding: '0.5rem' }}
            />
            <div style={{ marginTop: 6 }}>
              <button onClick={loadPgn} style={buttonStyle} disabled={!pgnInput.trim()}>Load PGN</button>
            </div>
            {playbackActive && (
              <div style={{ marginTop: 8, fontSize: '0.7rem', opacity: 0.8 }}>Loaded {loadedGameMoves.length} half-moves. Viewing ply {moveIndex}.</div>
            )}
          </div>
          <div style={{ marginTop: '0.5rem', maxHeight: 260, overflowY: 'auto', background: '#1e1f24', padding: '0.5rem 0.75rem', borderRadius: 4 }}>
            <strong>Moves:</strong>
            <ol style={{ paddingLeft: '1.1rem', margin: '0.5rem 0 0' }}>
              {displayedMoves.map((m, i) => (
                <li key={i} style={{ fontSize: '0.8rem', lineHeight: '1.2rem', background: playbackActive && i === moveIndex - 1 ? 'rgba(255,215,0,0.25)' : 'transparent' }}>{m.san}</li>
              ))}
              {displayedMoves.length === 0 && <li style={{ listStyle: 'none', opacity: 0.6 }}>No moves yet.</li>}
            </ol>
          </div>
        </div>
      </div>
    </div>
  );
}

const buttonStyle: React.CSSProperties = {
  padding: '0.5rem 0.9rem',
  background: '#444',
  border: '1px solid #666',
  color: '#fff',
  cursor: 'pointer',
  borderRadius: 4,
  fontSize: '0.75rem',
  letterSpacing: 0.5,
  display: 'inline-flex',
  alignItems: 'center',
  gap: '0.25rem'
};

export default App;