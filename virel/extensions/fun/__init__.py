from .nsfw import NSFW
from virel.core import Virel

from discord.ext.commands import Cog


class Fun(NSFW, Cog):
    def __init__(self, bot: Virel):
        super().__init__(bot)
        self.bot = bot

async def setup(bot: Virel):
    await bot.add_cog(Fun(bot))