# Frontend Chessboard Demo

A lightweight React + Vite setup using [`react-chessboard`](https://react-chessboard.vercel.app) and [`chess.js`] for move legality.

## Features
- Interactive chessboard with drag & drop piece movement
- Automatic legal move validation (illegal moves snap back)
- FEN display updates after each move
- Move list (in SAN) for the current session
- Reset button returns to initial position

## Tech Stack
- React 18
- Vite 5
- TypeScript 5
- `react-chessboard` for rendering
- `chess.js` for move logic

## Getting Started

Install deps and start the dev server:
```bash
npm install
npm run dev
```
The server prints a local URL (default `http://localhost:5173/` or next available port).

## Build & Preview
```bash
npm run build
npm run preview
```

## Code Overview
- `src/App.tsx` – Main component (board, move list, FEN, reset)
- `src/main.tsx` – React root bootstrap
- `vite.config.ts` – Vite config with React plugin

## How It Works
1. A single `Chess` instance from `chess.js` tracks position.
2. `onPieceDrop(sourceSquare, targetSquare)` attempts the move. If legal, board updates; else returns `false` to snap the piece back.
3. The resulting FEN and SAN move list are rendered below the board.

## Customization Ideas
- Add orientation toggle (flip board)
- Highlight last move squares
- Add PGN import/export functionality
- Add autoplay for a loaded PGN sequence
- Integrate with backend engine for evaluation overlays

## License
This demo code is MIT licensed. See repository root for overall project license.
