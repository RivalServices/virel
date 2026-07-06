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

    @command(aliases=["rl"])
    async def reload(self, ctx: Context, extension: str):
        """
        Reloads a cog.
        """
        ext = f"virel.extensions.{extension}"
        try:
            if ext in self.bot.extensions:
                await self.bot.reload_extension(ext)
                await ctx.approved(f"Reloaded {extension}")
            else:
                await self.bot.load_extension(ext)
                await ctx.approved(f"Loaded {extension}")
        
        except Exception as e:
            await ctx.denied(f"Failed to reload {extension}: ```yaml\n{e}```")

    @command(aliases=["ul"])
    async def unload(self, ctx: Context, extension: str):
        """
        Unloads a cog.
        """
        forbidden = ["dev", "jishaku"]
        if extension in forbidden:
            return await ctx.denied(f"Extension {extension} is forbidden to unload")
        
        ext = f"virel.extensions.{extension}"
        try:
            if ext in self.bot.extensions:
                await self.bot.unload_extension(ext)
                await ctx.approved(f"Unloaded {extension}")
            else:
                await ctx.denied(f"Extension {extension} is not loaded")
        
        except Exception as e:
            await ctx.denied(f"Failed to unload {extension}: ```yaml\n{e}```")

async def setup(bot: Virel):
    await bot.add_cog(Developer(bot))