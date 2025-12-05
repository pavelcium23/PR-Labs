import asyncio

import httpx
import pytest

from kvstore.harness import InProcessCluster


@pytest.fixture
def cluster():
    ctl = InProcessCluster(write_quorum=3, min_delay_ms=0, max_delay_ms=5, base_port=9400)
    ctl.start()
    try:
        yield ctl
    finally:
        ctl.stop()


@pytest.mark.asyncio
async def test_writes_replicate_to_all_followers(cluster):
    async with httpx.AsyncClient(timeout=5.0) as client:
        for idx in range(5):
            resp = await client.post(
                f"{cluster.leader_url}/kv/key-{idx}",
                json={"value": f"value-{idx}"},
            )
            assert resp.status_code == 200
            payload = resp.json()
            assert payload["acks"] >= cluster.write_quorum
        # wait for background replication to finish
        await asyncio.sleep(0.5)
        leader_dump = (await client.get(f"{cluster.leader_url}/dump")).json()["store"]
        for follower_url in cluster.follower_urls:
            follower_dump = (await client.get(f"{follower_url}/dump")).json()["store"]
            assert _normalize_store(follower_dump) == _normalize_store(leader_dump)


def _normalize_store(store: dict[str, dict]) -> dict[str, tuple[str, int]]:
    return {key: (entry["value"], entry["version"]) for key, entry in store.items()}


@pytest.mark.asyncio
async def test_write_fails_when_quorum_not_met():
    cluster = InProcessCluster(write_quorum=5, min_delay_ms=0, max_delay_ms=0, base_port=9500)
    cluster.start()
    # stop one follower to make quorum unreachable
    cluster.followers[0].stop()
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(
                f"{cluster.leader_url}/kv/critical",
                json={"value": "payload"},
            )
            assert resp.status_code == 503
    finally:
        cluster.stop()
