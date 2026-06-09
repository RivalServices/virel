from __future__ import annotations

import orjson

from typing import TYPE_CHECKING
from litestar import Request, get

from discord.ext.commands import Group

if TYPE_CHECKING:
    from virel.core import Virel

CACHE_KEY = "virel:commands"
CACHE_TTL = 60


def get_permissions(command) -> list[str]:
    """
    Extracts permissions from a command's checks.
    
    Args:
        command: The command to extract permissions from.
        
    Returns:
        A list of permission names.
    """
    permissions = []
    for check in command.checks:
        closure = getattr(check, "__closure__", None) or []
        for cell in closure:
            try:
                val = cell.cell_contents
                if isinstance(val, dict) and all(isinstance(v, bool) for v in val.values()):
                    permissions.extend(k for k, v in val.items() if v)
            except ValueError:
                pass
    return permissions


def clean_signature(signature: str | None) -> str | None:
    """
    Strips <> and [] wrappers and hides default values from a command signature.
    """
    if not signature:
        return None

    cleaned = signature.replace("[", "").replace("]", "").replace("<", "").replace(">", "")
    parts = []
    in_default = False

    for token in cleaned.split():
        if "=" in token:
            name = token.split("=")[0]
            if name:
                parts.append(name)
            in_default = True
        
        elif not in_default:
            if token:
                parts.append(token)

    return " ".join(parts) or None


def serialize_command(command) -> dict:
    """
    Serializes a command into a dictionary.
    
    Args:
        command: The command to serialize.
        
    Returns:
        A dictionary containing the command's information.
    """
    return {
        "name": command.name,
        "description": command.help or command.brief or None,
        "aliases": command.aliases,
        "signature": clean_signature(command.signature),
        "hidden": command.hidden,
        "permissions": get_permissions(command),
        "subcommands": (
            [serialize_command(c) for c in sorted(command.commands, key=lambda c: c.name)]
            if isinstance(command, Group)
            else []
        ),
    }


@get("/commands")
async def commands(request: Request) -> dict:
    """
    Returns all bot commands grouped by cog.
    """
    bot: Virel = request.app.state.bot

    cached = await bot.redis.get(CACHE_KEY)
    if cached:
        return orjson.loads(cached)

    grouped: dict[str, list] = {}
    for command in sorted(bot.commands, key=lambda c: c.name):
        if command.hidden:
            continue
        cog = command.cog_name or "Uncategorized"
        grouped.setdefault(cog, []).append(serialize_command(command))

    response = {
        "categories": [
            {"name": cog, "commands": cmds}
            for cog, cmds in sorted(grouped.items())
        ],
        "total": sum(len(v) for v in grouped.values()),
    }

    await bot.redis.set(CACHE_KEY, orjson.dumps(response).decode(), ex=CACHE_TTL)
    return response
