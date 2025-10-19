import { useState, useCallback, useRef } from 'react';
import { Chessboard } from 'react-chessboard';
import { Chess, Move, Square } from 'chess.js';

function App() {
  // Persist game across renders
  const gameRef = useRef(new Chess());
  const game = gameRef.current;

  // Position & move tracking
  const [fen, setFen] = useState(game.fen());
  const [moves, setMoves] = useState<Move[]>([]);

  // Click-to-move tracking
  const [moveFrom, setMoveFrom] = useState<string>('');
  const [optionSquares, setOptionSquares] = useState<Record<string, React.CSSProperties>>({});

  // Produce a random legal reply move (simple demo CPU)
  const makeRandomReply = useCallback(() => {
    if (game.isGameOver()) return;
    const possible = game.moves();
    if (!possible.length) return;
    const randomMove = possible[Math.floor(Math.random() * possible.length)];
    const result = game.move(randomMove);
    if (result) {
      setMoves((m) => [...m, result as Move]);
      setFen(game.fen());
    }
  }, [game]);

  // Highlight legal destinations from a square
  const getMoveOptions = useCallback((square: Square) => {
    const legal = game.moves({ square, verbose: true });
    if (legal.length === 0) {
      setOptionSquares({});
      return false;
    }
    const styles: Record<string, React.CSSProperties> = {};
    for (const mv of legal) {
      const isCapture = !!game.get(mv.to) && game.get(mv.to)?.color !== game.get(square)?.color;
      styles[mv.to] = {
        background: isCapture
          ? 'radial-gradient(circle, rgba(0,0,0,.15) 85%, transparent 85%)'
          : 'radial-gradient(circle, rgba(0,0,0,.15) 28%, transparent 28%)',
        borderRadius: '50%'
      };
    }
    styles[square] = { background: 'rgba(255,255,0,0.4)' };
    setOptionSquares(styles);
    return true;
  }, [game]);

  // Handle square click logic (click from square, then destination)
  const onSquareClick = useCallback((square: string, piece?: string) => {
    // First click selects piece
    if (!moveFrom && piece) {
      const hasOptions = getMoveOptions(square as Square);
      if (hasOptions) setMoveFrom(square);
      return;
    }

    // Attempt move
    if (moveFrom) {
      const legal = game.moves({ square: moveFrom as Square, verbose: true });
      const found = legal.find(m => m.from === moveFrom && m.to === square);
      if (!found) {
        // Maybe switching selection
        const hasOptions = getMoveOptions(square as Square);
        setMoveFrom(hasOptions ? square : '');
        return;
      }
      try {
  const result = game.move({ from: moveFrom as Square, to: square as Square, promotion: 'q' });
        if (result) {
          setMoves((m) => [...m, result as Move]);
          setFen(game.fen());
          setMoveFrom('');
          setOptionSquares({});
          setTimeout(makeRandomReply, 400);
        }
      } catch {
        const hasOptions = getMoveOptions(square as Square);
        setMoveFrom(hasOptions ? square : '');
      }
    }
  }, [moveFrom, game, getMoveOptions, makeRandomReply]);

  // Handle drag/drop logic
  const onPieceDrop = useCallback((sourceSquare: string, targetSquare: string) => {
    try {
  const result = game.move({ from: sourceSquare as Square, to: targetSquare as Square, promotion: 'q' });
      if (result) {
        setMoves((m) => [...m, result as Move]);
        setFen(game.fen());
        setMoveFrom('');
        setOptionSquares({});
        setTimeout(makeRandomReply, 500);
        return true;
      }
      return false;
    } catch {
      return false;
    }
  }, [game, makeRandomReply]);

  const reset = () => {
    game.reset();
    setFen(game.fen());
    setMoves([]);
    setMoveFrom('');
    setOptionSquares({});
  };

  return (
    <div style={layoutStyle}>
      <div style={{ maxWidth: 520 }}>
        <h1 style={{ ...titleStyle, textAlign: 'center' }}>This is made with react!</h1>
        <div style={boardWrapperStyle}>
          <Chessboard
            id="click-or-drag-board"
            position={fen}
            onPieceDrop={onPieceDrop}
            onSquareClick={onSquareClick}
            boardWidth={460}
            customSquareStyles={optionSquares}
            animationDuration={180}
          />
        </div>
        <div style={{ marginTop: '1rem', display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          <button onClick={reset} style={buttonStyle}>Reset</button>
        </div>
        <div style={fenBoxStyle}>
          <strong>FEN:</strong> {fen}
        </div>
        <div style={movesBoxStyle}>
          <strong>Moves (Your + CPU):</strong>
          <ol style={{ paddingLeft: '1.1rem', margin: '0.4rem 0 0' }}>
            {moves.map((m, i) => (
              <li key={i} style={{ fontSize: '0.72rem', lineHeight: '1rem' }}>{m.san}</li>
            ))}
            {moves.length === 0 && <li style={{ listStyle: 'none', opacity: 0.6 }}>No moves yet.</li>}
          </ol>
        </div>
      </div>
    </div>
  );
}

const layoutStyle: React.CSSProperties = {
  minHeight: '100vh',
  display: 'flex',
  alignItems: 'flex-start',
  justifyContent: 'center',
  padding: '2rem 1.25rem',
  background: '#20232a',
  color: '#fff',
  fontFamily: 'system-ui, sans-serif'
};

const titleStyle: React.CSSProperties = { margin: '0 0 1rem', fontSize: '1.4rem' };

const boardWrapperStyle: React.CSSProperties = {
  boxShadow: '0 4px 16px rgba(0,0,0,0.45)',
  borderRadius: 8,
  overflow: 'hidden',
  background: '#2f3542',
  padding: '0.75rem'
};

const buttonStyle: React.CSSProperties = {
  padding: '0.5rem 0.9rem',
  background: '#444',
  border: '1px solid #666',
  color: '#fff',
  cursor: 'pointer',
  borderRadius: 4,
  fontSize: '0.75rem'
};

const fenBoxStyle: React.CSSProperties = {
  marginTop: '1rem',
  fontSize: '0.7rem',
  background: '#1e1f24',
  padding: '0.5rem 0.75rem',
  borderRadius: 4,
  wordBreak: 'break-all'
};

const movesBoxStyle: React.CSSProperties = {
  marginTop: '1rem',
  fontSize: '0.7rem',
  background: '#1e1f24',
  padding: '0.5rem 0.75rem',
  borderRadius: 4,
  maxHeight: 220,
  overflowY: 'auto'
};

export default App;