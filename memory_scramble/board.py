from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Awaitable, Callable, Dict, List, Optional, Tuple

CardTransform = Callable[[str], Awaitable[str]]
Position = Tuple[int, int]

# Delay constants used when revealing cards to players. Keeping them short makes
# automated tests fast while still giving players time to observe the board.
MISMATCH_HIDE_DELAY_SECONDS = 0.6
MATCH_CLEAR_DELAY_SECONDS = 0.4


@dataclass(slots=True)
class _Card:
    """Internal mutable state for a single board location."""

    label: Optional[str]
    face_up: bool = False
    controller: Optional[str] = None

    @property
    def present(self) -> bool:
        return self.label is not None


class Board:
    """Concurrency-safe mutable board used by the Memory Scramble game.

    Abstraction function:
        AF(self) is a height x width grid of cards, where each card either has a
        label (a unicode string) or has been removed from the board. Each card
        may be face down, face up under the control of some player, or removed.

    Representation invariant:
        * len(self._grid) == self._height and each row has self._width entries
        * If a card's label is None, then face_up is False and controller is None
        * Every controller listed in _controlled maps to the exact cards that
          have controller == player_id and are face up.
        * Each player controls at most two cards at a time.

    Safety from rep exposure:
        * The _Card instances are private to this module.
        * All methods that return state return freshly-built strings.
    """

    def __init__(self, cards: List[List[str]]):
        if not cards or not cards[0]:
            raise ValueError("board must contain at least one card")
        widths = {len(row) for row in cards}
        if len(widths) != 1:
            raise ValueError("board rows must have equal length")

        self._height = len(cards)
        self._width = len(cards[0])
        self._grid: List[List[_Card]] = [
            [_Card(label=value) for value in row]
            for row in cards
        ]
        self._controlled: Dict[str, List[Position]] = {}
        self._version = 0
        self._lock = asyncio.Lock()
        self._condition = asyncio.Condition(self._lock)
        self._pending_resolutions: set[asyncio.Task[None]] = set()
        self.check_rep()

    @property
    def height(self) -> int:
        return self._height

    @property
    def width(self) -> int:
        return self._width

    @classmethod
    async def parse_from_file(cls, filename: str) -> "Board":
        """Parse a board description from *filename*.

        The file format matches the original TypeScript starter:
        the first nonempty line is HEIGHTxWIDTH, followed by HEIGHT*WIDTH lines
        of card labels in row-major order.
        """

        path = Path(filename)
        if not path.exists():
            raise FileNotFoundError(f"board file not found: {filename}")

        contents = await asyncio.to_thread(path.read_text, encoding="utf-8")
        lines = [line.strip() for line in contents.splitlines() if line.strip()]
        if not lines:
            raise ValueError("board file is empty")

        match = re.fullmatch(r"(\d+)x(\d+)", lines[0])
        if not match:
            raise ValueError("first line of board must be HEIGHTxWIDTH")
        height = int(match.group(1))
        width = int(match.group(2))
        if height <= 0 or width <= 0:
            raise ValueError("board dimensions must be positive")

        expected_cards = height * width
        cards_only = lines[1:]
        if len(cards_only) != expected_cards:
            raise ValueError(
                f"expected {expected_cards} cards but found {len(cards_only)}"
            )

        matrix = [
            cards_only[row * width:(row + 1) * width]
            for row in range(height)
        ]
        return cls(matrix)

    async def look(self, player_id: str) -> str:
        """Observe the board from *player_id*'s perspective."""

        async with self._condition:
            state = self._render_locked(player_id)
            return state

    async def flip(self, player_id: str, row: int, column: int) -> str:
        """Flip the card at (row, column) for *player_id*."""

        self._validate_position(row, column)
        position = (row, column)

        async with self._condition:
            await self._wait_for_player_slot(player_id)

            while True:
                card = self._grid[row][column]
                if not card.present:
                    raise ValueError("card has already been removed")
                if card.face_up:
                    if card.controller == player_id:
                        raise ValueError("player already controls this card")
                    await self._condition.wait()
                    continue
                card.face_up = True
                card.controller = player_id
                self._controlled.setdefault(player_id, []).append(position)
                self._bump_version_locked()
                break

            snapshot = self._render_locked(player_id)
            if len(self._controlled[player_id]) == 2:
                first, second = self._controlled[player_id]
                if first == second:
                    raise ValueError("must flip two distinct cards")
                match = self._cards_match(first, second)
                delay = MATCH_CLEAR_DELAY_SECONDS if match else MISMATCH_HIDE_DELAY_SECONDS
                task = asyncio.create_task(
                    self._resolve_pair(player_id, first, second, match, delay)
                )
                self._pending_resolutions.add(task)
                task.add_done_callback(self._pending_resolutions.discard)

            self.check_rep()
            return snapshot

    async def map(self, player_id: str, transform: CardTransform) -> str:
        """Replace every card label with transform(label)."""

        async with self._condition:
            snapshot = [
                ((row, col), card.label)
                for row, grid_row in enumerate(self._grid)
                for col, card in enumerate(grid_row)
                if card.present and card.label is not None
            ]

        replacements: Dict[Position, str] = {}
        for position, label in snapshot:
            assert label is not None
            new_label = await transform(label)
            if not isinstance(new_label, str) or not new_label:
                raise ValueError("map() transform must return a nonempty string")
            replacements[position] = new_label

        changed = False
        async with self._condition:
            for (row, col), new_label in replacements.items():
                card = self._grid[row][col]
                if not card.present:
                    continue
                if card.label != new_label:
                    card.label = new_label
                    changed = True
            if changed:
                self._bump_version_locked()
            snapshot = self._render_locked(player_id)
            self.check_rep()
            return snapshot

    async def watch(self, player_id: str) -> str:
        """Wait until the board changes, then return the new state."""

        async with self._condition:
            baseline = self._version
            await self._condition.wait_for(lambda: self._version != baseline)
            state = self._render_locked(player_id)
            return state

    async def _wait_for_player_slot(self, player_id: str) -> None:
        """Wait until the player controls at most one card."""

        while True:
            current = self._controlled.get(player_id, [])
            if len(current) < 2:
                return
            await self._condition.wait()

    def _cards_match(self, first: Position, second: Position) -> bool:
        first_card = self._grid[first[0]][first[1]]
        second_card = self._grid[second[0]][second[1]]
        return first_card.present and second_card.present and first_card.label == second_card.label

    async def _resolve_pair(
        self,
        player_id: str,
        first: Position,
        second: Position,
        matched: bool,
        delay: float,
    ) -> None:
        await asyncio.sleep(delay)
        async with self._condition:
            cards = [self._grid[first[0]][first[1]], self._grid[second[0]][second[1]]]
            if any(card.controller != player_id for card in cards):
                return
            if matched:
                for card in cards:
                    card.label = None
                    card.face_up = False
            else:
                for card in cards:
                    card.face_up = False
            for card in cards:
                card.controller = None
            self._controlled[player_id] = []
            if not self._controlled[player_id]:
                del self._controlled[player_id]
            self._bump_version_locked()
            self.check_rep()

    def _render_locked(self, player_id: str) -> str:
        lines = [f"{self._height}x{self._width}"]
        for row in range(self._height):
            for col in range(self._width):
                card = self._grid[row][col]
                lines.append(self._describe_card(player_id, card))
        return "\n".join(lines)

    def _describe_card(self, player_id: str, card: _Card) -> str:
        if not card.present:
            return "none _"
        if not card.face_up:
            return "down _"
        status = "my" if card.controller == player_id else "up"
        assert card.label is not None
        return f"{status} {card.label}"

    def _validate_position(self, row: int, column: int) -> None:
        if not (0 <= row < self._height and 0 <= column < self._width):
            raise ValueError("card position out of range")

    def _bump_version_locked(self) -> None:
        self._version += 1
        self._condition.notify_all()

    def check_rep(self) -> None:
        assert len(self._grid) == self._height
        for row in self._grid:
            assert len(row) == self._width
        for row in self._grid:
            for card in row:
                if card.label is None:
                    assert not card.face_up
                    assert card.controller is None
        for player, positions in self._controlled.items():
            assert len(positions) <= 2
            for (r, c) in positions:
                card = self._grid[r][c]
                assert card.face_up
                assert card.controller == player
        # _controlled should not keep empty lists
        for player, positions in list(self._controlled.items()):
            if not positions:
                del self._controlled[player]