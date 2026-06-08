from discord.ext.commands import Cog

from virel.core import Virel

from .prefix import Prefix

class Configuration(Prefix, Cog):
    """
    Modify server and user related configuration settings for the bot.
    Base configuration class that all other configuration classes should inherit from.
    """
    def __init__(self, bot: Virel):
        self.bot = bot

async def setup(bot: Virel):
    await bot.add_cog(Configuration(bot))