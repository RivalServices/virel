from socket import gaierror
import sys
import discord
import time

from datetime import datetime, timezone

from discord import (
    Embed, 
    ButtonStyle,   
    TextChannel, 
    CategoryChannel, 
    VoiceChannel, 
    Role,
    User,
    Member,
    Guild,
    Invite,
)

from discord.utils import format_dt
from discord.ui import Button, View
from discord.ext.commands import Cog, command, CurrentChannel, Author, CommandError, CurrentGuild

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

    @command(name = "uptime", aliases = ["boot", "up", "startup"])
    async def uptime(self, ctx: Context):
        """
        Shows the uptime of the bot.
        """
        return await ctx.reply(f"ngl.. i been peepin since <t:{int(self.bot.startup_time.timestamp())}:R>")
    
    @command(name="roles")
    async def roles(self, ctx: Context):
        """
        Shows a list of all roles in the guild.
        """
        if not (roles := list(reversed(ctx.guild.roles[1:]))):
            raise CommandError(f"No roles have been found in {ctx.guild.name}!")

        rows = [f"{role.mention} - {len(role.members)} member{'s' if len(role.members) != 1 else ''}" for i, role in enumerate(roles)]

        embed = Embed(title=f"Roles in {ctx.guild.name}", color=Configuration.Colors.neutral)
        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon.url if ctx.guild.icon else None)

        return await ctx.paginate(rows, embed=embed)

    @command(aliases=["si", "guild", "guildinfo"])
    async def serverinfo(self, ctx: Context, *, guild: Guild | Invite = CurrentGuild):
        """
        Shows information about the server.
        """
        if isinstance(guild, Invite):
            invite = guild
            guild = invite.guild

            embed = Embed(color=Configuration.Colors.neutral)
            embed.title = f"Invite code: {invite.code}"
            embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
            embed.add_field(
                name="Invite",
                value=(
                    f">>> **Channel:** {invite.channel.name} ({invite.channel.type})\n"
                    f"**ID:** `{invite.channel.id}`\n"
                    f"**Expires:** {'no' if invite.max_age == 0 else f'<t:{int(invite.expires_at.timestamp())}:R>' if invite.expires_at else 'no'}\n"
                    f"**Uses:** {invite.uses if invite.uses is not None else 'unknown'}"
                ) if invite.channel else ">>> Unknown",
                inline=True,
            )
            embed.add_field(
                name="Server",
                value=(
                    f">>> **Name:** {guild.name}\n"
                    f"**ID:** `{guild.id}`\n"
                    f"**Members:** {invite.approximate_member_count or 'N/A'}\n"
                    f"**Created:** {f'<t:{int(guild.created_at.timestamp())}:D>' if guild.created_at else 'N/A'}"
                ),
                inline=True,
            )

            view = View()
            if guild.icon:
                view.add_item(Button(label="Icon", url=guild.icon.url, style=ButtonStyle.link))
            view.add_item(Button(label="Invite", url=invite.url, style=ButtonStyle.link))

            return await ctx.send(embed=embed, view=view)

        embed = Embed(color=Configuration.Colors.neutral)
        if guild.owner:
            embed.set_author(
                name=f"{guild.owner} ({guild.owner.id})",
                icon_url=guild.owner.display_avatar.url,
            )
        else:
            embed.set_author(name="Unknown Owner")
        
        embed.title = guild.name
        embed.description = f"Created on <t:{int(guild.created_at.timestamp())}:D>  <t:{int(guild.created_at.timestamp())}:R>"
        if guild.me and guild.me.joined_at:
            embed.description += (
                f"\nJoined on <t:{int(guild.me.joined_at.timestamp())}:D>  <t:{int(guild.me.joined_at.timestamp())}:R>"
            )
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        embed.add_field(
            name="Counts",
            value=(
                f">>> **Roles:** {len(guild.roles) - 1}\n"
                f"**Emojis:** {len(guild.emojis)}\n"
                f"**Stickers:** {len(guild.stickers)}"
            ),
            inline=True,
        )
        embed.add_field(
            name="Members",
            value=(
                f">>> **Users:** {sum(1 for m in guild.members if not m.bot):,}\n"
                f"**Bots:** {sum(1 for m in guild.members if m.bot):,}\n"
                f"**Total:** {guild.member_count:,}"
            ),
            inline=True,
        )
        embed.add_field(
            name="Channels",
            value=(
                f">>> **Text:** {len(guild.text_channels)}\n"
                f"**Voice:** {len(guild.voice_channels)}\n"
                f"**Categories:** {len(guild.categories)}"
            ),
            inline=True,
        )
        embed.add_field(
            name="Info",
            value=(
                f">>> **Vanity:** {guild.vanity_url_code or 'N/A'}\n"
                f"**Popularity:** {sorted(self.bot.guilds, key=lambda g: g.member_count or 0, reverse=True).index(guild) + 1}/{len(self.bot.guilds)}\n"
                f"**Owner:** {guild.owner.mention if guild.owner else 'Unknown'}"
            ),
            inline=True,
        )
        embed.add_field(
            name="Boost",
            value=(
                f">>> **Boosts:** {guild.premium_subscription_count}\n"
                f"**Level:** {guild.premium_tier}\n"
                f"**Boosters:** {len(guild.premium_subscribers)}"
            ),
            inline=True,
        )
        embed.set_footer(text=f"Guild ID: {guild.id} \u2022 Shard: {guild.shard_id or 0}/{self.bot.shard_count or 1}")

        return await ctx.send(embed=embed)

    @command(aliases=["ui", "whois", "who"])
    async def userinfo(self, ctx, member: Member = Author):
        """
        Shows information about a user.
        """
        now = datetime.now(timezone.utc)

        roles = [r.mention for r in member.roles[1:]]
        join_pos = sorted(ctx.guild.members, key=lambda m: m.joined_at or now).index(member) + 1
        mutual = sum(1 for g in self.bot.guilds if member in g.members)

        embed = Embed(color=Configuration.Colors.neutral)
        embed.set_author(name=f"{member.name} ({member.id})", icon_url=member.display_avatar.url)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Created", value=f"<t:{int(member.created_at.timestamp())}:D>\n<t:{int(member.created_at.timestamp())}:R>", inline=True)
        embed.add_field(name="Joined", value=f"<t:{int(member.joined_at.timestamp())}:D>\n<t:{int(member.joined_at.timestamp())}:R>", inline=True)

        if member.premium_since:
            embed.add_field(name="Boosting", value=f"<t:{int(member.premium_since.timestamp())}:D>\n<t:{int(member.premium_since.timestamp())}:R>", inline=True)

        if roles:
            embed.add_field(name=f"Roles [{len(roles)}]", value=" ".join(roles), inline=False)

        embed.set_footer(text=f"Join position: {join_pos} • {mutual} server(s)")

        await ctx.send(embed=embed)

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
        embed.add_field(name=f"Members ({len(role.members)})", value=', '.join([m.name for m in list(role.members)[:5]]) + (f" +{len(role.members) - 5}" if len(role.members) > 5 else ""), inline=False)
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
        return await ctx.send("<https://discord.gg/rivalbot>")#iew=view)

    @command(aliases=["code"])
    async def source(self, ctx: Context):
        """
        Shows the source code for the bot.
        """
        view = View().add_item(
            Button(label=f"Source Code", url=f"https://github.com/RivalServices/virel", style=ButtonStyle.link)
        )
        await ctx.message.add_reaction("😂")
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
