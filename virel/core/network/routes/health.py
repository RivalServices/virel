from __future__ import annotations

import orjson

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from litestar import Request, get

if TYPE_CHECKING:
    from virel.core import Virel

CACHE_KEY = "virel:health"
CACHE_TTL = 3


@get("/health")
async def health(request: Request) -> dict:
    """
    Returns health information about the bot.
    """
    bot: Virel = request.app.state.bot

    cached = await bot.redis.get(CACHE_KEY)
    if cached:
        return orjson.loads(cached)

    latencies = dict(bot.latencies)
    now = datetime.now(timezone.utc)

    shard_data: dict[int, dict] = {}
    for guild in bot.guilds:
        sid = guild.shard_id
        if sid not in shard_data:
            shard_data[sid] = {"guilds": 0, "members": 0}
        shard_data[sid]["guilds"] += 1
        shard_data[sid]["members"] += guild.member_count or 0

    shard_latencies = list(latencies.values())
    avg_latency = round(sum(shard_latencies) / len(shard_latencies) * 1000, 2) if shard_latencies else None

    def shard_uptime(sid: int) -> float | None:
        """
        Returns the uptime of a shard in seconds.
        
        Args:
            sid: The shard ID.
            
        Returns:
            The uptime of the shard in seconds, or None if the shard is not ready.
        """
        ready_at = bot.shard_ready_times.get(sid)
        if not ready_at:
            return None
        return round((now - ready_at.replace(tzinfo=timezone.utc)).total_seconds())

    response = {
        "shards": [
            {
                "id": sid,
                "guilds": data["guilds"],
                "members": data["members"],
                "latency": round(latencies[sid] * 1000, 2) if sid in latencies else None,
                "uptime": shard_uptime(sid),
            }
            for sid, data in sorted(shard_data.items())
        ],
        "shard_count": bot.shard_count,
        "guilds": len(bot.guilds),
        "users": len(bot.users),
        "avg_latency": avg_latency,
    }

    await bot.redis.set(CACHE_KEY, orjson.dumps(response).decode(), ex=CACHE_TTL)
    return response
