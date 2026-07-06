import inspect
import re
import discord

from discord import Embed, Permissions
from discord.ext.commands import Cog, Command, Context, Greedy, Group, HelpCommand

from typing import Union, get_args, get_origin

from virel.core.config import Configuration
from virel.core.functions.context.paginator import Paginator

FLAGS_RE = re.compile(r"\n(?:Optional )?Flags\n[-=]+\n", re.I)
EXAMPLE_RE = re.compile(r"\nExample:\s*\n", re.I)


def _unwrap(converter):
    """
    Unwraps a converter.
    """
    if isinstance(converter, Greedy):
        return _unwrap(converter.converter)
    
    if get_origin(converter) is Union:
        args = [arg for arg in get_args(converter) if arg is not type(None)]
        return _unwrap(args[0]) if len(args) == 1 else converter
    return converter


def _example_value(ctx: Context, param) -> str | None:
    """
    Prefills the value for a parameter.
    """
    name = (param.displayed_name or param.name).lower()
    if name == "flags":
        return None

    if name in {"channel"}:
        return ctx.channel.name
    if name in {"member", "user", "author"}:
        return ctx.author.display_name
    if name in {"guild", "server"}:
        return ctx.guild.name if ctx.guild else "guild"
    if name in {"reason", "message"}:
        return name
    if name in {"prefix"}:
        return ctx.clean_prefix

    converter = _unwrap(param.converter)
    if converter in {str, int, bool}:
        return {str: name, int: "1", bool: "true"}[converter]
    if not isinstance(converter, type):
        return name

    if issubclass(converter, discord.Member | discord.User):
        return ctx.author.display_name
    if issubclass(converter, discord.Role):
        if ctx.guild:
            roles = [role for role in ctx.guild.roles if not role.is_default() and not role.managed]
            return roles[-1].name if roles else "role"
        return "role"
    if issubclass(converter, discord.Guild):
        return ctx.guild.name if ctx.guild else "guild"
    if issubclass(converter, discord.abc.GuildChannel):
        return ctx.channel.name
    return name


def _example(ctx: Context, command: Command) -> str:
    """
    Formats the examples for a command.
    """
    prefix = ctx.clean_prefix
    parts = [f"{prefix}{command.qualified_name}"]
    parts.extend(
        value for param in command.clean_params.values()
        if (value := _example_value(ctx, param)) is not None
    )
    return " ".join(parts)


def _permissions(command: Command) -> list[str]:
    """
    Gets the permissions for a command.
    """
    perms = []
    for check in command.checks:
        predicate = getattr(check, "predicate", check)
        try:
            data = inspect.getclosurevars(predicate).nonlocals.get("perms")
        except TypeError:
            continue
        if not isinstance(data, dict):
            continue
        for perm, enabled in data.items():
            if not enabled or perm not in Permissions.VALID_FLAGS:
                continue
            label = perm.replace("_", " ").title()
            if label not in perms:
                perms.append(label)
    return perms


def _parse_flag(line: str) -> tuple[str, str] | None:
    """
    Parses a flag from a line of text.
    """
    line = line.strip()
    if not line:
        return None
    if ":" in line:
        flag, desc = line.split(":", 1)
        return flag.strip(), desc.strip()
    if " " in line:
        flag, desc = line.split(" ", 1)
        return flag, desc.strip(" :")
    return line, ""


def _parse_help(command: Command) -> dict:
    """
    Parses the help text for a command.
    """
    doc = inspect.cleandoc(command.help or inspect.getdoc(command.callback) or "")
    parsed = {
        "description": command.short_doc or "No description provided.",
        "flags": [],
        "example": None,
    }
    if not doc:
        return parsed

    if FLAGS_RE.search(doc):
        body, flags_text = FLAGS_RE.split(doc, maxsplit=1)
        parsed["description"] = body.strip() or parsed["description"]
        if EXAMPLE_RE.search(flags_text):
            flags_text, example = EXAMPLE_RE.split(flags_text, maxsplit=1)
            parsed["example"] = example.strip().splitlines()[0]
        parsed["flags"] = [flag for line in flags_text.splitlines() if (flag := _parse_flag(line))]
        return parsed

    if EXAMPLE_RE.search(doc):
        body, example = EXAMPLE_RE.split(doc, maxsplit=1)
        parsed["description"] = body.strip() or parsed["description"]
        parsed["example"] = example.strip().splitlines()[0]
    else:
        parsed["description"] = doc.split("\n\n", 1)[0].strip() or parsed["description"]
    return parsed


class Help(HelpCommand):
    """
    Custom help command for Virel.
    """
    def __init__(self):
        """
        Initializes the Help command.
        """
        super().__init__(command_attrs={"aliases": ["h", "commands"]})

    def _syntax(self, command: Command) -> str:
        """
        Formats the syntax for a command.
        """
        ctx = self.context
        params = " ".join(f"[{p.displayed_name or p.name}]" for p in command.clean_params.values())
        return f"{ctx.clean_prefix}{command.qualified_name} {params}".strip()

    def _usage(self, command: Command, example: str | None) -> str:
        """
        Formats the usage for a command.
        """
        return (
            f"```yaml\n"
            f"Syntax: {self._syntax(command)}\n"
            f"Example: {example or _example(self.context, command)}\n"
            f"```"
        )

    def _embed(self, command: Command, *, page: int, total: int) -> Embed:
        """
        Builds the command embed.
        """
        ctx = self.context
        parsed = _parse_help(command)
        params = command.clean_params
        perms = _permissions(command)

        embed = Embed(
            title=f"Command: {command.qualified_name}",
            description=parsed["description"],
            color=Configuration.Colors.neutral,
        )
        embed.set_author(name=ctx.bot.user.name, icon_url=ctx.bot.user.display_avatar.url)
        embed.add_field(name="Aliases", value=", ".join(command.aliases) or "N/A", inline=True)
        embed.add_field(
            name="Parameters",
            value=", ".join(p.displayed_name or p.name for p in params.values()) or "N/A",
            inline=True,
        )
        embed.add_field(
            name="Information",
            value=f"{Configuration.Emojis.warning} {', '.join(perms)}" if perms else "N/A",
            inline=True,
        )

        body = ""
        if parsed["flags"]:
            body = "**Optional Flags**\n" + "\n".join(
                f"`{flag}` : {desc}" if desc else f"`{flag}`" for flag, desc in parsed["flags"]
            ) + "\n\n"
        body += f"**Usage**\n{self._usage(command, parsed['example'])}"
        embed.add_field(name="\u200b", value=body, inline=False)

        module = command.cog.qualified_name if command.cog else "Unknown"
        embed.set_footer(text=f"Page: {page}/{total} • Module: {module}")
        return embed

    async def _send_pages(self, embeds: list[Embed]):
        """
        Sends the embed pages.
        """
        if not embeds:
            return
        ctx = self.context
        if len(embeds) == 1:
            await ctx.send(embed=embeds[0])
            return
        
        paginator = Paginator(
            ctx,
            [""] * len(embeds),
            embed=Embed(color=Configuration.Colors.neutral),
            per_page=1,
            timeout=60,
        )
        paginator.pages = embeds
        await paginator.start()

    async def send_command_help(self, command: Command):
        """
        Sends the command help.
        """
        await self.context.send(embed=self._embed(command, page=1, total=1))

    async def send_group_help(self, group: Group):
        """
        Sends the group help.
        """
        commands = [group, *await self.filter_commands(group.commands, sort=True)]
        await self._send_pages([self._embed(cmd, page=i, total=len(commands)) for i, cmd in enumerate(commands, 1)])

    async def send_cog_help(self, cog: Cog):
        """
        Sends the cog help.
        """
        filtered = await self.filter_commands(cog.get_commands(), sort=True)
        if not filtered:
            ctx = self.context
            embed = Embed(
                title=f"Module: {cog.qualified_name}",
                description=cog.description or "No commands available",
                color=Configuration.Colors.neutral,
            )
            embed.set_author(name=ctx.bot.user.name, icon_url=ctx.bot.user.display_avatar.url)
            embed.set_footer(text="Page: 1/1")
            await ctx.send(embed=embed)
            return
        await self._send_pages([self._embed(cmd, page=i, total=len(filtered)) for i, cmd in enumerate(filtered, 1)])

    async def send_bot_help(self, mapping):
        """
        Sends the bot help.
        """
        ctx = self.context
        await ctx.send(
            f"{ctx.author.mention}: <https://rival.rocks/commands>, "
            f"join the discord server at <https://rival.rocks/discord>"
        )
