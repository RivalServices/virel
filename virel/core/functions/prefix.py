from discord import Message

from 

async def get_prefix(bot, message: Message):
    """
    Returns the command prefix for the bot dynamically.
    """
    return bot.command_prefix