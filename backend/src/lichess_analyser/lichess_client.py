"""Simple Lichess API client for fetching a single game's PGN.

This module purposefully uses only the standard library so it doesn't add new
dependencies to the project. It supports passing a personal access token via
constructor or via the `LICHESS_TOKEN` environment variable.

Usage:
    client = LichessClient(token=os.getenv('LICHESS_TOKEN'))
    pgn_text = client.get_single_game('qBi86tUA')

The endpoint used is documented at https://lichess.org/api#tag/Games/operation/gamePgn
which accepts the Accept header to choose the response format. By default this
client requests PGN (text) and returns the raw PGN string.
"""

from __future__ import annotations

import os
import urllib.error
import urllib.request
from typing import Dict, Optional
from urllib.parse import urlencode


class LichessApiError(RuntimeError):
    """Raised for non-2xx responses from the Lichess API."""


class LichessClient:
    """Tiny client for a subset of the Lichess API.

    Parameters
    - token: personal access token (optional). If not provided the client will
      look for the `LICHESS_TOKEN` environment variable.
    - base_url: base Lichess url (default: https://lichess.org)
    """

    def __init__(
        self, token: Optional[str] = None, *, base_url: str = "https://lichess.org"
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.token = token or os.getenv("LICHESS_TOKEN")

    def _build_headers(self, accept: str = "application/x-chess-pgn") -> Dict[str, str]:
        headers = {"Accept": accept, "User-Agent": "lichess-analyser/0.1"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def get_single_game(
        self,
        game_id: str,
        *,
        accept: str = "application/json",
        params: Optional[Dict[str, str]] = None,
        timeout: int = 10,
    ) -> str:
        """Fetch one game from Lichess and return the response body as text.

        - game_id: the Lichess game id (usually 8 chars).
        - accept: media type to request. Default is PGN text.
        - params: optional query parameters (e.g., {'moves': 'true', 'tags': 'true'}).
        - timeout: network timeout in seconds.

        Returns the decoded response text. Raises LichessApiError on HTTP errors.
        """
        if not game_id:
            raise ValueError("game_id must be provided")

        path = f"/game/export/{game_id}"
        qs = f"?{urlencode(params)}" if params else ""
        url = f"{self.base_url}{path}{qs}"

        headers = self._build_headers(accept=accept)
        req = urllib.request.Request(url, headers=headers, method="GET")

        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                # resp may be bytes (for pgn) or text encoded utf-8
                raw = resp.read()
                try:
                    return raw.decode("utf-8")
                except Exception:
                    # fallback: return repr of bytes
                    return raw.decode("latin-1")
        except urllib.error.HTTPError as e:
            # Create a helpful message including status and body (if any)
            body = b""
            try:
                body = e.read()
            except Exception:
                pass
            msg = f"Lichess API error: {e.code} {e.reason} for url {url}. Response body: {body[:200]!r}"
            raise LichessApiError(msg) from e
        except urllib.error.URLError as e:
            raise LichessApiError(f"Network error when contacting {url}: {e}") from e
