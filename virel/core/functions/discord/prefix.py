from discord import Message
from discord.ext.commands import when_mentioned_or

from ...config import Configuration


async def get_prefix(bot, message: Message):
    """
    Returns the command prefix for the bot dynamically based on the guild settings
    stored in the database. If the guild has a custom prefix set in the `settings`
    table, that prefix will be returned. Otherwise, the default prefix from the
    configuration will be used.
    """
    if not message.guild:
        return Configuration.Bot.prefix

    try:
        row = await bot.pool.fetchrow(
            """
            SELECT prefix 
            FROM settings.prefix
            WHERE guild_id = $1
            """,
            message.guild.id,
        )
        if row and row["prefix"]:
            return when_mentioned_or(row["prefix"])(bot, message)
    
    except Exception:
        pass

    return when_mentioned_or(Configuration.Bot.prefix)(bot, message)