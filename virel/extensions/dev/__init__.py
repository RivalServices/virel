from discord import Embed
from discord.ext.commands import Cog, command

from virel.core import Virel, Context

class Developer(Cog):
    """
    A cog for developer-only commands and utilities.
    """
    def __init__(self, bot: Virel):
        self.bot = bot

    async def cog_check(self, ctx: Context):
        return super().cog_check(ctx) and ctx.author.id in self.bot.owner_ids
    
    @command()
    async def guilds(self, ctx: Context):
        """
        Lists all guilds the bot is currently in.
        """
        entries = [f"{guild.name} ({guild.id})" for guild in self.bot.guilds]
        return await ctx.paginate(entries)