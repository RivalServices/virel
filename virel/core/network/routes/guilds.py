from __future__ import annotations

import orjson

from typing import TYPE_CHECKING
from litestar import Request, get

if TYPE_CHECKING:
    from virel.core import Virel

CACHE_KEY = "virel:guilds"
CACHE_TTL = 3


@get("/guilds")
async def guilds(request: Request) -> dict:
    """
    Returns the top 30 biggest guilds by member count.
    """
    bot: Virel = request.app.state.bot

    cached = await bot.redis.get(CACHE_KEY)
    if cached:
        return orjson.loads(cached)

    top_guilds = sorted(bot.guilds, key=lambda g: g.member_count or 0, reverse=True)[:30]

    response = {
        "guilds": [
            {
                "id": str(guild.id),
                "name": guild.name,
                "icon": str(guild.icon.url) if guild.icon else None,
                "members": guild.member_count or 0,
            }
            for guild in top_guilds
        ],
        "total": len(bot.guilds),
    }

    await bot.redis.set(CACHE_KEY, orjson.dumps(response).decode(), ex=CACHE_TTL)
    return response
