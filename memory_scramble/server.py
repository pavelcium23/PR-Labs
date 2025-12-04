from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, PlainTextResponse
import uvicorn

PUBLIC_DIR = Path(__file__).resolve().parent.parent / "public"


try:  # Allow running both as package module and standalone script
    from .board import Board
    from . import commands
except ImportError:  # pragma: no cover - fallback for direct execution
    from board import Board
    import commands


def create_app(board: Board) -> FastAPI:
    """Create a FastAPI application that exposes the Memory Scramble API."""

    app = FastAPI(title="Memory Scramble Server")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/", response_class=FileResponse)
    async def root() -> FileResponse:
        index_path = PUBLIC_DIR / "index.html"
        if not index_path.exists():
            raise HTTPException(status_code=404, detail="index.html not found")
        return FileResponse(index_path, media_type="text/html")

    @app.get("/favicon.ico", response_class=PlainTextResponse)
    async def favicon() -> PlainTextResponse:
        return PlainTextResponse(status_code=204, content="")

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
