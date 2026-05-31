from discord import Embed
from discord.ext.commands import Cog, command

from virel.core import Virel, Context

class Developer(Cog):
    """
    A cog for developer-only commands and utilities.
    """
    def __init__(self, bot: Virel):
        """
        Initializes the Developer cog.
        """
        self.bot = bot

    async def cog_check(self, ctx: Context):
        """
        Checks if the user is a developer.
        """
        return super().cog_check(ctx) and ctx.author.id in self.bot.owner_ids
    
    @command()
    async def guilds(self, ctx: Context):
        """
        Lists all guilds the bot is currently in.
        """
        entries = [
            f"{guild.name} ({guild.id}) - {guild.member_count or 0}"
            for guild in sorted(self.bot.guilds, key=lambda g: g.member_count or 0, reverse=True)
        ]
        return await ctx.paginate(entries)

async def setup(bot: Virel):
    await bot.add_cog(Developer(bot))