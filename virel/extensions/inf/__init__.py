import sys
import discord
import time

from discord import (
    Embed, 
    ButtonStyle,   
    TextChannel, 
    CategoryChannel, 
    VoiceChannel, 
    Role,
    User
)
from discord.utils import format_dt
from discord.ui import Button, View
from discord.ext.commands import Cog, command, CurrentChannel

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

    @command(aliases=["info", "about", "bi", "bot"])
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

    @command(aliases=["ri"])
    async def roleinfo(self, ctx: Context, role: Role = None):
        """
        Shows information about a role.
        """
        role = role or ctx.author.top_role
        dangerous_perms = await ctx.dangerous_perms(role)

        embed = Embed(title=f"{role.name}", color=role.color)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
        embed.add_field(name="Role ID", value=f"``{role.id}``", inline=True)
        embed.add_field(name="Role color", value=str(role.color) if role.color else "No color", inline=True)
        embed.add_field(name="Created", value=format_dt(role.created_at, style="R") + f" ({format_dt(role.created_at, style='R')})", inline=False)
        embed.add_field(name="Members", value=', '.join([m.name for m in list(role.members)[:5]]) + (f" +{len(role.members) - 5}" if len(role.members) > 5 else ""), inline=False)
        embed.add_field(name="Permissions", value=", ".join(dangerous_perms).replace("_", " ").title() if dangerous_perms else "No dangerous permissions", inline=False)
        embed.set_thumbnail(url=role.icon.url if role.icon else None)

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

    @command()
    async def support(self, ctx: Context):
        """
        Shows the support server for the bot.
        """
        view = View().add_item(
            Button(label=f"Support {self.bot.user.name}", url=f"https://discord.gg/rivalbot", style=ButtonStyle.link)
        )
        return await ctx.send(view=view)

    @command(aliases=["code"])
    async def source(self, ctx: Context):
        """
        Shows the source code for the bot.
        """
        view = View().add_item(
            Button(label=f"Source Code", url=f"https://github.com/RivalServices/virel", style=ButtonStyle.link)
        )
        return await ctx.send(view=view)

    @command()
    async def ping(self, ctx: Context):
        """
        Check the bot's latency.
        """
        start = time.perf_counter()
        message = await ctx.send(f"... `{round(self.bot.latency * 1000)}ms`")
        rtt = (time.perf_counter() - start) * 1000
        await message.edit(content=f"... `{round(self.bot.latency * 1000)}ms` (rest: `{round(rtt)}ms`)")

    @command(aliases=["av"])
    async def avatar(self, ctx: Context, user: User = None):
        """
        Shows the avatar of a user.
        """
        user = user or ctx.author
        if not user.avatar:
            return await ctx.warning(f"{'You' if user == ctx.author else user.mention} does not have an avatar")
        
        embed = Embed(color=Configuration.Colors.neutral)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
        embed.set_image(url=user.display_avatar.url)
        return await ctx.send(embed=embed)

    @command(aliases=["ci"])
    async def channelinfo(self, ctx: Context, channel: TextChannel | CategoryChannel | VoiceChannel = CurrentChannel):
        """
        Shows information about the channel.
        """
        embed = Embed(title=channel.name, color=Configuration.Colors.neutral)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
        embed.add_field(name="Channel ID", value=f"`{channel.id}`", inline=True)
        embed.add_field(name="Type", value=channel.type.name, inline=True)

        if ctx.guild:
            embed.add_field(
                name="Guild",
                value=f"{ctx.guild.name} `({ctx.guild.id})`",
                inline=True,
            )
            category = getattr(channel, "category", None)
            embed.add_field(
                name="Category",
                value=f"{category.name} `({category.id})`" if category else "None",
                inline=False,
            )

        topic = getattr(channel, "topic", None)
        embed.add_field(name="Topic", value=topic or "None", inline=False)
        embed.add_field(
            name="Created At",
            value=f"{format_dt(channel.created_at, 'F')} ({format_dt(channel.created_at, 'R')})",
            inline=False,
        )
        return await ctx.send(embed=embed)

async def setup(bot: Virel):
    await bot.add_cog(Information(bot))
