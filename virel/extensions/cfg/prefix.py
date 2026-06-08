from discord import Embed
from discord.ext.commands import Cog, group, has_permissions

from virel.core import Virel
from virel.core.config import Configuration
from virel.core.functions.context import Context

class Prefix(Cog):
    """
    Set and manage the server's command prefix.
    """
    def __init__(self, bot: Virel):
        self.bot = bot

    @group(name="prefix", invoke_without_command=True)
    async def prefix(self, ctx: Context):
        """
        Modifiy server prefix.
        """
        embed = Embed(color=Configuration.Colors.neutral)
        embed.set_author(name=f"{ctx.author.display_name}", icon_url=ctx.author.display_avatar)

        prefix = await self.bot.db.fetchval(
            """
            SELECT prefix 
            FROM settings.prefix
            WHERE guild_id = $1
            """,
            ctx.guild.id
        )
        if prefix:
            embed.add_field(name="Prefix", value=f">>> {prefix} - Server Prefix\n{self.bot.user.mention} - Bot Mention")
        else:
            default_prefix = Configuration.Bot.prefix
            embed.add_field(name="Prefix", value=f">>> {default_prefix} - Default Prefix\n{self.bot.user.mention} - Bot Mention")
        
        return await ctx.send(embed=embed)
    
    @prefix.command(name="set")
    @has_permissions(manage_guild=True)
    async def prefix_set(self, ctx: Context, prefix: str):
        """
        Set the server's prefix.
        """
        current_prefix = await self.bot.db.fetchval(
            """
            SELECT prefix 
            FROM settings.prefix 
            WHERE guild_id = $1
            """,
            ctx.guild.id
        )
        if current_prefix == prefix:
            return await ctx.warning(f"The prefix `{prefix}` is already set as this server's prefix")
        
        record = await self.bot.db.execute(
            """
            INSERT INTO settings.prefix (guild_id, prefix)
            VALUES ($1, $2)
            ON CONFLICT (guild_id) DO UPDATE SET prefix = $2
            """,
            ctx.guild.id,
            prefix
        )
        if record:
            await ctx.approved(f"Prefix set to `{prefix}`")

    @prefix.command(name="reset")
    @has_permissions(manage_guild=True)
    async def prefix_reset(self, ctx: Context):
        """
        Reset the server's prefix to the default.
        """
        record = await self.bot.db.execute(
            """
            DELETE FROM settings.prefix 
            WHERE guild_id = $1
            """,
            ctx.guild.id
        )
        if record:
            await ctx.approved("Prefix reset to default")
        