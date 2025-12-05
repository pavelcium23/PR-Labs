from __future__ import annotations

import asyncio
import logging
import random
from typing import Any, Iterable

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .config import Settings
from .store import KVStore

logger = logging.getLogger("kvstore")


class WriteRequest(BaseModel):
    value: Any


class ReplicateRequest(BaseModel):
    key: str
    value: Any
    version: int


class ReplicationError(Exception):
    """Raised when the leader cannot gather enough acknowledgements."""


def _entry_response(entry) -> dict[str, Any]:
    return {
        "key": entry.key,
        "value": entry.value,
        "version": entry.version,
        "updated_at": entry.updated_at,
    }


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings.from_env()
    settings.validate()

    app = FastAPI(title="Distributed KV Store", version="1.0.0")
    store = KVStore()
    app.state.settings = settings
    app.state.store = store
    app.state.http_client: httpx.AsyncClient | None = None

    async def _replicate_to_followers(entry) -> int:
        follower_urls = settings.follower_urls
        if settings.role != "leader" or settings.write_quorum == 0 or not follower_urls:
            return 0

        required = settings.write_quorum
        client = app.state.http_client
        if client is None:
            raise RuntimeError("HTTP client not initialized")

        payload = {"key": entry.key, "value": entry.value, "version": entry.version}
        tasks = [
            asyncio.create_task(_replicate_single(client, url, payload, settings))
            for url in follower_urls
        ]

        successes = 0
        pending = set(tasks)

        if not pending:
            return 0

        while pending and successes < required:
            done, pending = await asyncio.wait(
                pending,
                return_when=asyncio.FIRST_COMPLETED,
                timeout=settings.replicate_timeout_seconds,
            )
            if not done:
                break
            for task in done:
                exc = task.exception()
                if exc:
                    logger.warning("Follower replication failed: %s", exc)
                    continue
                successes += 1

        if successes < required:
            # Drain remaining tasks to avoid warnings.
            if pending:
                asyncio.create_task(_drain_pending(pending))
            raise ReplicationError(
                f"Write quorum {required} not met "
                f"(acks={successes}, followers={len(follower_urls)})"
            )

        # Drain the remaining followers in the background.
        if pending:
            asyncio.create_task(_drain_pending(pending))

        return successes

    async def _drain_pending(pending: Iterable[asyncio.Task]) -> None:
        for task in pending:
            try:
                await task
            except Exception as exc:  # noqa: BLE001
                logger.debug("Background replication task failed: %s", exc)

    async def _replicate_single(
        client: httpx.AsyncClient,
        follower_url: str,
        payload: dict[str, Any],
        cfg: Settings,
    ) -> None:
        delay_ms = random.uniform(cfg.min_delay_ms, cfg.max_delay_ms)
        if delay_ms > 0:
            await asyncio.sleep(delay_ms / 1000.0)
        response = await client.post(f"{follower_url}/replicate", json=payload)
        response.raise_for_status()

    @app.on_event("startup")
    async def startup_event() -> None:
        app.state.http_client = httpx.AsyncClient(
            timeout=settings.replicate_timeout_seconds
        )
        logger.info(
            "Node %s (%s) listening on %s:%s",
            settings.node_id,
            settings.role,
            settings.host,
            settings.port,
        )

    @app.on_event("shutdown")
    async def shutdown_event() -> None:
        client = app.state.http_client
        if client:
            await client.aclose()

    @app.get("/health")
    async def health() -> dict[str, Any]:
        return {"status": "ok", "node_id": settings.node_id, "role": settings.role}

    @app.get("/kv/{key}")
    async def read_key(key: str):
        entry = await store.get(key)
        if not entry:
            raise HTTPException(status_code=404, detail="Key not found")
        return _entry_response(entry)

    @app.post("/kv/{key}")
    async def write_key(key: str, request: WriteRequest):
        if settings.role != "leader":
            raise HTTPException(status_code=403, detail="Followers are read-only")
        entry = await store.set_local(key, request.value)
        try:
            acknowledgements = await _replicate_to_followers(entry)
        except ReplicationError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        response = _entry_response(entry)
        response["acks"] = acknowledgements
        response["required_acks"] = settings.write_quorum
        return JSONResponse(response)

    @app.post("/replicate")
    async def replicate(request: ReplicateRequest):
        if settings.role != "follower":
            raise HTTPException(status_code=405, detail="Leader cannot accept replicas")
        entry, applied = await store.apply_replica(request.key, request.value, request.version)
        response = _entry_response(entry)
        response["applied"] = applied
        return response

    @app.get("/dump")
    async def dump():
        data = await store.snapshot()
        current_version = await store.version()
        return {
            "node_id": settings.node_id,
            "role": settings.role,
            "version": current_version,
            "store": data,
        }

    return app


# When used with ``uvicorn kvstore.app:app --factory`` this callable will be invoked.
app = create_app

