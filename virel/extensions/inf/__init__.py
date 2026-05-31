import sys
import discord

from discord import Embed, ButtonStyle
from discord.ui import Button, View
from discord.ext.commands import Cog, command

from virel.core import Virel, Context
from virel.core.config import Configuration


class Information(Cog):
    """
    Shows information regarding the bot, its members, channels, and commands and other details.
    """
    def __init__(self, bot: Virel):
        """
        Initializes the Information cog.
        """
        self.bot = bot

    @command(aliases=["info", "about", "bi"])
    async def botinfo(self, ctx: Context):
        """
        Shows information about the bot.
        """
        embed = Embed(
            description=(
                f"Premium multi-purpose Discord bot made by the [Rival Team](https://rival.rocks)\n"
                f"Used by **{len(self.bot.users):,}** members in **{len(self.bot.guilds):,}** guilds on **{len(self.bot.shards):,}** shards"
            ),
            color=Configuration.Colors.neutral,
        )
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.display_avatar.url)
        embed.add_field(
            name="Members",
            value=(
                f">>> **Total:** {len(self.bot.users):,}\n"
                f"**Human:** {len(self.bot.users) - sum(u.bot for u in self.bot.users):,}\n"
                f"**Bots:** {sum(u.bot for u in self.bot.users):,}"
            ),
            inline=True,
        )
        embed.add_field(
            name="Channels",
            value=(
                f">>> **Text:** {sum(len(g.text_channels) for g in self.bot.guilds):,}\n"
                f"**Voice:** {sum(len(g.voice_channels) for g in self.bot.guilds):,}\n"
                f"**Categories:** {sum(len(g.categories) for g in self.bot.guilds):,}"
            ),
            inline=True,
        )
        embed.add_field(
            name="System",
            value=(
                f">>> **Commands:** {len(set(self.bot.walk_commands())):,}\n"
                f"**Discord.py:** [{discord.__version__}](https://github.com/Rapptz/discord.py)\n"
                f"**Python:** [{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}](https://www.python.org/)"
            ),
            inline=True,
        )
        return await ctx.send(embed=embed)

    @command()
    async def credits(self, ctx: Context):
        """
        Shows the credits for the bot.
        """
        embed = Embed(title="Credits", color=Configuration.Colors.neutral)
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.display_avatar.url)
        embed.description = (
            f"[vael](https://discord.com/users/604463848526708757) - Developer"
        )
        return await ctx.send(embed=embed)

    @command(aliases=["inv"])
    async def invite(self, ctx: Context):
        """
        Shows the invite link for the bot.
        """
        view = View().add_item(
            Button(label=f"Invite {self.bot.user.name}", url=f"https://discord.com/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot", style=ButtonStyle.link)
        )
        return await ctx.send(view=view)


async def setup(bot: Virel):
    await bot.add_cog(Information(bot))
