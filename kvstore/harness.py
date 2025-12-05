from __future__ import annotations

import threading
import time
from typing import List

import httpx
import uvicorn

from .app import create_app
from .config import Settings


class InProcessNode:
    """Runs a FastAPI node inside the current process for testing/analysis."""

    def __init__(self, settings: Settings, log_level: str = "warning") -> None:
        self.settings = settings
        self.app = create_app(settings)
        self.config = uvicorn.Config(
            self.app,
            host=settings.host,
            port=settings.port,
            log_level=log_level,
            lifespan="on",
        )
        self.server = uvicorn.Server(self.config)
        self.thread = threading.Thread(target=self.server.run, daemon=True)
        self.base_url = f"http://{settings.host}:{settings.port}"

    def start(self, timeout: float = 10.0) -> None:
        self.thread.start()
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                response = httpx.get(f"{self.base_url}/health", timeout=0.5)
                if response.status_code == 200:
                    return
            except Exception:  # noqa: BLE001
                time.sleep(0.05)
        raise RuntimeError(f"Node {self.settings.node_id} failed to start")

    def stop(self) -> None:
        self.server.should_exit = True
        self.thread.join(timeout=5)


class InProcessCluster:
    """Starts a leader with five followers for tests or analysis."""

    def __init__(
        self,
        write_quorum: int,
        min_delay_ms: int = 0,
        max_delay_ms: int = 1000,
        base_port: int = 9100,
        follower_count: int = 5,
    ) -> None:
        if follower_count < 1:
            raise ValueError("Cluster requires at least one follower")
        if write_quorum < 1 or write_quorum > follower_count:
            raise ValueError("write_quorum must be between 1 and follower_count")
        self.write_quorum = write_quorum
        self.min_delay_ms = min_delay_ms
        self.max_delay_ms = max_delay_ms
        self.base_port = base_port
        self.follower_count = follower_count
        self.followers: List[InProcessNode] = []
        self.leader: InProcessNode | None = None
        self.leader_url: str | None = None
        self.follower_urls: List[str] = []

    def start(self) -> None:
        follower_urls: List[str] = []
        for idx in range(self.follower_count):
            port = self.base_port + idx + 1
            follower_settings = Settings(
                role="follower",
                node_id=f"follower-{idx+1}",
                host="127.0.0.1",
                port=port,
                min_delay_ms=self.min_delay_ms,
                max_delay_ms=self.max_delay_ms,
            )
            follower = InProcessNode(follower_settings)
            follower.start()
            follower_urls.append(f"http://127.0.0.1:{port}")
            self.followers.append(follower)

        leader_settings = Settings(
            role="leader",
            node_id="leader",
            host="127.0.0.1",
            port=self.base_port,
            follower_urls=follower_urls,
            write_quorum=self.write_quorum,
            min_delay_ms=self.min_delay_ms,
            max_delay_ms=self.max_delay_ms,
        )
        self.leader = InProcessNode(leader_settings)
        self.leader.start()
        self.leader_url = f"http://127.0.0.1:{self.base_port}"
        self.follower_urls = follower_urls

    def stop(self) -> None:
        if self.leader:
            self.leader.stop()
        for follower in self.followers:
            follower.stop()
        self.followers.clear()
        self.leader = None
        self.leader_url = None
        self.follower_urls = []

