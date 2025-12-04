import asyncio

import pytest

from memory_scramble.board import (
    Board,
    MATCH_CLEAR_DELAY_SECONDS,
    MISMATCH_HIDE_DELAY_SECONDS,
)


@pytest.mark.asyncio
async def test_parse_from_file_and_look() -> None:
    board = await Board.parse_from_file("boards/ab.txt")
    state = await board.look("tester")
    lines = state.splitlines()
    assert lines[0] == "5x5"
    assert len(lines) == 1 + 25
    assert all(line == "down _" for line in lines[1:])


@pytest.mark.asyncio
async def test_flip_matching_pair_removes_cards() -> None:
    board = Board([["A", "A"]])
    await board.flip("alice", 0, 0)
    state = await board.flip("alice", 0, 1)
    assert state.splitlines()[1:3] == ["my A", "my A"]
    await asyncio.sleep(MATCH_CLEAR_DELAY_SECONDS + 0.1)
    cleared = await board.look("alice")
    assert cleared.splitlines()[1:3] == ["none _", "none _"]


@pytest.mark.asyncio
async def test_flip_mismatch_turns_cards_face_down() -> None:
    board = Board([["A", "B"]])
    await board.flip("bob", 0, 0)
    await board.flip("bob", 0, 1)
    await asyncio.sleep(MISMATCH_HIDE_DELAY_SECONDS + 0.1)
    after = await board.look("bob")
    assert after.splitlines()[1:3] == ["down _", "down _"]


@pytest.mark.asyncio
async def test_map_transforms_labels() -> None:
    board = Board([["A", "B"], ["B", "A"]])

    async def to_lower(label: str) -> str:
        return label.lower()

    await board.map("mapper", to_lower)
    await board.flip("mapper", 0, 0)
    state = await board.look("mapper")
    assert "my a" in state


@pytest.mark.asyncio
async def test_watch_reports_changes() -> None:
    board = Board([["A", "A"]])

    async def watcher() -> str:
        return await board.watch("carol")

    task = asyncio.create_task(watcher())
    await asyncio.sleep(0.05)
    await board.flip("carol", 0, 0)
    updated = await asyncio.wait_for(task, timeout=1.0)
    assert "my A" in updated
