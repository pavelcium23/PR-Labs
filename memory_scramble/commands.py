"""String-based commands for the Memory Scramble server."""

from __future__ import annotations

import re
from typing import Awaitable, Callable

from board import Board

CardTransform = Callable[[str], Awaitable[str]]
_PLAYER_ID_PATTERN = re.compile(r"^[A-Za-z0-9_]+$")


def _validate_player(player_id: str) -> None:
    if not _PLAYER_ID_PATTERN.fullmatch(player_id):
        raise ValueError("playerId must be alphanumeric or underscore")


def _validate_coordinate(value: int, name: str) -> None:
    if not isinstance(value, int):
        raise ValueError(f"{name} must be an integer")


async def look(board: Board, player_id: str) -> str:
    """Return the board state for *player_id*."""

    _validate_player(player_id)
    return await board.look(player_id)


async def flip(board: Board, player_id: str, row: int, column: int) -> str:
    """Flip a single card for *player_id*."""

    _validate_player(player_id)
    _validate_coordinate(row, "row")
    _validate_coordinate(column, "column")
    return await board.flip(player_id, row, column)


async def map(board: Board, player_id: str, transform: CardTransform) -> str:
    """Replace every card with transform(card)."""

    _validate_player(player_id)
    if not callable(transform):
        raise ValueError("transform must be callable")
    return await board.map(player_id, transform)


async def watch(board: Board, player_id: str) -> str:
    """Return the next state change for *player_id*."""

    _validate_player(player_id)
    return await board.watch(player_id)
