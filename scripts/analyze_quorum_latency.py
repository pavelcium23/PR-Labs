from __future__ import annotations

import asyncio
import json
from pathlib import Path
from statistics import mean
from time import perf_counter
from typing import List

import httpx
import matplotlib.pyplot as plt

from kvstore.harness import InProcessCluster

TOTAL_WRITES = 100
KEY_SPACE = 10
CONCURRENCY = 10
SETTLE_DELAY_SECONDS = 1.5
RESULTS_PATH = Path("analysis/quorum_latency_results.json")
PLOT_PATH = Path("imgs/quorum_vs_latency.png")


async def _issue_write(client: httpx.AsyncClient, url: str, key: str, value: str, sem: asyncio.Semaphore) -> float:
    async with sem:
        start = perf_counter()
        resp = await client.post(f"{url}/kv/{key}", json={"value": value})
        resp.raise_for_status()
        return (perf_counter() - start) * 1000  # milliseconds


async def _run_load(leader_url: str) -> List[float]:
    sem = asyncio.Semaphore(CONCURRENCY)
    async with httpx.AsyncClient(timeout=10.0) as client:
        tasks = [
            asyncio.create_task(
                _issue_write(
                    client,
                    leader_url,
                    key=f"key-{idx % KEY_SPACE}",
                    value=f"value-{idx}",
                    sem=sem,
                )
            )
            for idx in range(TOTAL_WRITES)
        ]
        return await asyncio.gather(*tasks)


async def _verify_consistency(cluster: InProcessCluster) -> bool:
    async with httpx.AsyncClient(timeout=5.0) as client:
        leader_store = (await client.get(f"{cluster.leader_url}/dump")).json()["store"]
        leader_projection = {k: (v["value"], v["version"]) for k, v in leader_store.items()}
        for follower_url in cluster.follower_urls:
            follower_store = (await client.get(f"{follower_url}/dump")).json()["store"]
            follower_projection = {k: (v["value"], v["version"]) for k, v in follower_store.items()}
            if follower_projection != leader_projection:
                return False
        return True


async def run_analysis() -> list[dict[str, float]]:
    results: list[dict[str, float]] = []
    for quorum in range(1, 6):
        cluster = InProcessCluster(
            write_quorum=quorum,
            min_delay_ms=0,
            max_delay_ms=1000,
            base_port=9700 + quorum * 20,
        )
        cluster.start()
        try:
            latencies = await _run_load(cluster.leader_url)
            await asyncio.sleep(SETTLE_DELAY_SECONDS)
            avg_latency = mean(latencies)
            consistent = await _verify_consistency(cluster)
            results.append(
                {
                    "write_quorum": quorum,
                    "average_latency_ms": avg_latency,
                    "max_latency_ms": max(latencies),
                    "min_latency_ms": min(latencies),
                    "consistent": consistent,
                }
            )
        finally:
            cluster.stop()
    return results


def _persist_results(results: list[dict[str, float]]) -> None:
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text(json.dumps(results, indent=2))


def _plot(results: list[dict[str, float]]) -> None:
    quorums = [item["write_quorum"] for item in results]
    averages = [item["average_latency_ms"] for item in results]
    plt.figure(figsize=(8, 4))
    plt.plot(quorums, averages, marker="o")
    plt.xticks(quorums)
    plt.xlabel("Write quorum (followers)")
    plt.ylabel("Average latency (ms)")
    plt.title("Impact of write quorum on observed write latency")
    plt.grid(True, linestyle="--", alpha=0.4)
    PLOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(PLOT_PATH, dpi=200)
    plt.close()


def main() -> None:
    results = asyncio.run(run_analysis())
    _persist_results(results)
    _plot(results)
    print("Analysis complete. Results:")
    for row in results:
        print(row)


if __name__ == "__main__":
    main()
