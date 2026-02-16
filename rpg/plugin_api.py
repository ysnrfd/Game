from __future__ import annotations

from typing import Protocol


class GamePlugin(Protocol):
    """Plugin interface.

    A plugin module should expose a `register(game)` function.
    """

    def register(self, game: "Game") -> None:
        ...
