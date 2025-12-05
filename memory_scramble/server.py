from __future__ import annotations

import argparse
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from fastapi.responses import FileResponse
import uvicorn
from pathlib import Path
from typing import Iterable

from board import Board
import commands


def iter_public_dirs() -> Iterable[Path]:
    """Yield possible locations for the bundled web UI."""
    server_dir = Path(__file__).resolve().parent
    yield server_dir.parent / "public"  # repository root/public
    yield server_dir / "public"  # repo copied without top-level public
    yield Path.cwd() / "public"  # running from arbitrary working dir


def find_index_file() -> Path | None:
    for directory in iter_public_dirs():
        candidate = directory / "index.html"
        if candidate.exists():
            return candidate
    return None

def create_app(board: Board) -> FastAPI:
    """Create a FastAPI application that exposes the Memory Scramble API."""

    app = FastAPI(title="Memory Scramble Server")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/look/{player_id}", response_class=PlainTextResponse)
    async def look_endpoint(player_id: str) -> str:
        try:
            return await commands.look(board, player_id)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/flip/{player_id}/{location}", response_class=PlainTextResponse)
    async def flip_endpoint(player_id: str, location: str) -> str:
        try:
            row_string, col_string = location.split(",", maxsplit=1)
            row = int(row_string)
            col = int(col_string)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="invalid row,column") from exc
        try:
            return await commands.flip(board, player_id, row, col)
        except ValueError as exc:
            raise HTTPException(
                status_code=409,
                detail=f"cannot flip this card: {exc}",
            ) from exc

    @app.get("/replace/{player_id}/{from_card}/{to_card}", response_class=PlainTextResponse)
    async def replace_endpoint(player_id: str, from_card: str, to_card: str) -> str:
        async def transform(card: str) -> str:
            return to_card if card == from_card else card

        try:
            return await commands.map(board, player_id, transform)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/watch/{player_id}", response_class=PlainTextResponse)
    async def watch_endpoint(player_id: str) -> str:
        try:
            return await commands.watch(board, player_id)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
    
    @app.get("/")
    async def root():
        index_path = find_index_file()
        if not index_path:
            searched = ", ".join(str(path / "index.html") for path in iter_public_dirs())
            raise HTTPException(
                status_code=404,
                detail=f"index.html not found; looked in: {searched}",
            )
        return FileResponse(index_path, media_type="text/html")

    @app.get("/favicon.ico", response_class=PlainTextResponse)
    async def favicon() -> PlainTextResponse:
        return PlainTextResponse(status_code=204, content="")

    return app


async def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Memory Scramble server")
    parser.add_argument("port", type=int, help="listening port (0 chooses a random port)")
    parser.add_argument("filename", help="path to a board file")
    args = parser.parse_args()

    if args.port < 0:
        raise ValueError("port must be non-negative")

    board = await Board.parse_from_file(args.filename)
    app = create_app(board)
    config = uvicorn.Config(app, host="0.0.0.0", port=args.port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
