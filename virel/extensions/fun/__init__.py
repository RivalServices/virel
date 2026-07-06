from .roleplay import NSFW, SFW
from virel.core import Virel

from discord.ext.commands import Cog


class Fun(NSFW, SFW, Cog):
    def __init__(self, bot: Virel):
        NSFW.__init__(self, bot)
        SFW.__init__(self, bot)
        self.bot = bot

async def setup(bot: Virel):
    await bot.add_cog(Fun(bot))