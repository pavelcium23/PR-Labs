from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List


@dataclass(slots=True)
class Settings:
    """Runtime configuration for a KV store node."""

    role: str = "leader"
    node_id: str = "node"
    host: str = "0.0.0.0"
    port: int = 8000
    follower_urls: List[str] = field(default_factory=list)
    write_quorum: int = 0
    min_delay_ms: int = 0
    max_delay_ms: int = 1000
    replicate_timeout_seconds: float = 5.0

    @classmethod
    def from_env(cls) -> "Settings":
        follower_urls_env = os.getenv("FOLLOWER_URLS", "").strip()
        follower_urls = [
            url.strip()
            for url in follower_urls_env.split(",")
            if url.strip()
        ]
        return cls(
            role=os.getenv("ROLE", "leader").lower(),
            node_id=os.getenv("NODE_ID", "node"),
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", "8000")),
            follower_urls=follower_urls,
            write_quorum=int(os.getenv("WRITE_QUORUM", str(len(follower_urls)) or "0")),
            min_delay_ms=int(os.getenv("MIN_DELAY_MS", "0")),
            max_delay_ms=int(os.getenv("MAX_DELAY_MS", "1000")),
            replicate_timeout_seconds=float(os.getenv("REPLICATE_TIMEOUT_SECONDS", "5.0")),
        )

    def validate(self) -> None:
        if self.role not in {"leader", "follower"}:
            raise ValueError(f"Unsupported ROLE '{self.role}'")
        if self.min_delay_ms < 0 or self.max_delay_ms < 0:
            raise ValueError("Delays must be non-negative")
        if self.max_delay_ms < self.min_delay_ms:
            raise ValueError("MAX_DELAY_MS must be >= MIN_DELAY_MS")
        if self.replicate_timeout_seconds <= 0:
            raise ValueError("Replication timeout must be positive")
        if self.role == "leader":
            if not self.follower_urls:
                raise ValueError("Leader requires at least one follower URL")
            if self.write_quorum <= 0:
                raise ValueError("Leader WRITE_QUORUM must be >= 1")
            if self.write_quorum > len(self.follower_urls):
                raise ValueError(
                    f"WRITE_QUORUM ({self.write_quorum}) "
                    f"cannot exceed follower count ({len(self.follower_urls)})"
                )
        else:
            # Followers ignore write quorum and follower URLs.
            self.write_quorum = 0
            self.follower_urls = []

