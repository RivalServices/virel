from __future__ import annotations

from typing import TYPE_CHECKING, Any
from contextlib import suppress

from discord import Forbidden, Guild, HTTPException, Invite, NotFound
from discord.utils import format_dt
from discord.ext.commands import (
    BadFlagArgument,
    BadInviteArgument,
    BadLiteralArgument,
    BadUnionArgument,
    ChannelNotFound,
    CheckFailure,
    CommandError,
    CommandInvokeError,
    CommandNotFound,
    CommandOnCooldown,
    DisabledCommand,
    FlagError,
    MaxConcurrencyReached,
    MemberNotFound,
    MessageNotFound,
    MissingFlagArgument,
    MissingPermissions,
    MissingRequiredArgument,
    MissingRequiredAttachment,
    MissingRequiredFlag,
    NSFWChannelRequired,
    NotOwner,
    Range,
    RangeError,
    RoleNotFound,
    TooManyFlags,
    UserNotFound,
)

from .context import Context

if TYPE_CHECKING:
    from discord import Member, User
    from virel.core import Virel


def human_join(seq: list[str], *, delimiter: str = ", ", final: str = "or") -> str:
    """
    Joins a list of strings with a delimiter and a final separator.
    """
    if not seq:
        return ""
    elif len(seq) == 1:
        return seq[0]
    elif len(seq) == 2:
        return f"{seq[0]} {final} {seq[1]}"
    else:
        return f"{delimiter.join(seq[:-1])}{delimiter}{final} {seq[-1]}"


class CommandErrorHandler:
    def __init__(self, bot: "Virel"):
        """
        Initializes the CommandErrorHandler.
        """
        self.bot = bot

    async def on_command_error(self, ctx: Context, exc: CommandError) -> Any:
        """
        Handles a command error.
        """ 
        try:
            return await self._handle_command_error(ctx, exc)
        except Exception as e:
            return await ctx.denied(f"An error occurred while processing the command: ```yaml\n{e}```")

    async def _handle_command_error(self, ctx: Context, exc: CommandError) -> Any:
        """
        Handles a command error.
        """
        if not (
            ctx.channel
            and (
                ctx.guild is None
                or all(
                    [
                        ctx.channel.permissions_for(ctx.guild.me).send_messages,
                        ctx.channel.permissions_for(ctx.guild.me).embed_links,
                    ]
                )
            )
        ):
            return

        if isinstance(exc, CommandNotFound | NotOwner):
            return

        elif isinstance(
            exc,
            MissingRequiredArgument | MissingRequiredAttachment | BadLiteralArgument,
        ):
            return await ctx.send_help(ctx.command)

        elif isinstance(exc, FlagError):
            if isinstance(exc, TooManyFlags):
                return await ctx.denied(
                    f"The **{exc.flag.name}** flag was specified multiple times",
                )
            elif isinstance(exc, MissingFlagArgument):
                return await ctx.denied(
                    f"You must specify a value for the **{exc.flag.name}** flag",
                )
            elif isinstance(exc, MissingRequiredFlag):
                return await ctx.denied(
                    f"You forgot to specify the **{exc.flag.name}** flag",
                )
            elif isinstance(exc, BadFlagArgument):
                annotation = exc.flag.annotation
                if isinstance(annotation, Range):
                    if annotation.min is not None and annotation.max is not None:
                        detail = f"between **{annotation.min}** and **{annotation.max}**"
                    elif annotation.min is not None:
                        detail = f"at least **{annotation.min}**"
                    elif annotation.max is not None:
                        detail = f"at most **{annotation.max}**"
                    else:
                        detail = None

                    if detail:
                        return await ctx.denied(
                            f"The **{exc.flag.name}** flag must be {detail}",
                        )
                return await ctx.denied(
                    f"Invalid value provided for the **{exc.flag.name}** flag",
                )

        if isinstance(exc, CommandInvokeError):
            return await ctx.denied(str(exc.original))

        elif isinstance(exc, MaxConcurrencyReached):
            return await ctx.denied(
                f"Maximum concurrency reached for **{ctx.command.qualified_name}**, please try again later"
            )

        elif isinstance(exc, CommandOnCooldown):
            if exc.retry_after > 30:
                return await ctx.denied(
                    f"You're on cooldown\n> Try again **{format_dt(exc.retry_after, 'R')}**"
                )
            return await ctx.message.add_reaction("\u23f0")

        elif isinstance(exc, BadUnionArgument):
            if set(exc.converters) == {Member, User}:
                return await ctx.denied(
                    f"Couldn't find any **{exc.param.name}** matching **{ctx.current_argument}**\n"
                    "> If the user isn't in this server, try using their **ID** instead"
                )
            elif exc.converters == (Guild, Invite):
                return await ctx.denied(
                    f"No server was found matching **{ctx.current_argument}**",
                )
            else:
                return await ctx.denied(
                    f"Casting **{exc.param.name}** to {human_join([f'`{c.__name__}`' for c in exc.converters])} failed",
                )

        elif isinstance(exc, MemberNotFound):
            return await ctx.denied(
                f"No **member** was found matching **{exc.argument}**",
            )

        elif isinstance(exc, UserNotFound):
            return await ctx.denied(
                f"No **user** was found matching **{exc.argument}**",
            )

        elif isinstance(exc, RoleNotFound):
            return await ctx.denied(
                f"No **role** was found matching **{exc.argument}**",
            )

        elif isinstance(exc, ChannelNotFound):
            return await ctx.denied(
                f"No **channel** was found matching **{exc.argument}**",
            )

        elif isinstance(exc, MessageNotFound):
            return await ctx.denied(
                "Couldn't find the specified **message**\n"
                "> Consider using the **Message URL** instead",
            )

        elif isinstance(exc, BadInviteArgument):
            return await ctx.denied("Invalid **invite code** provided")

        elif isinstance(exc, DisabledCommand):
            return await ctx.denied("This command is currently disabled")

        elif isinstance(exc, RangeError):
            label = ""
            if exc.minimum is None and exc.maximum is not None:
                label = f"no more than **{exc.maximum}**"
            elif exc.minimum is not None and exc.maximum is None:
                label = f"no less than **{exc.minimum}**"
            elif exc.maximum is not None and exc.minimum is not None:
                label = f"between **{exc.minimum}** and **{exc.maximum}**"

            if label and isinstance(exc.value, str):
                label += " characters"

            return await ctx.denied(f"The input must be {label}")

        elif isinstance(exc, MissingPermissions):
            permissions = human_join(
                [f"`{permission}`" for permission in exc.missing_permissions],
                final="and",
            )
            _plural = "s" if len(exc.missing_permissions) > 1 else ""

            return await ctx.denied(
                f"You're missing the {permissions} permission{_plural}",
            )

        elif isinstance(exc, NSFWChannelRequired):
            return await ctx.denied("This command can only be used in **NSFW** channels")

        elif isinstance(exc, CommandError):
            if isinstance(exc, (HTTPException, NotFound)) and not isinstance(
                exc, (CheckFailure, Forbidden)
            ):
                if "Unknown Channel" in exc.text or "Unknown Interaction" in exc.text:
                    return
                return await ctx.denied(exc.text.capitalize())

            if isinstance(exc, (Forbidden, CommandInvokeError)):
                error = exc.original if isinstance(exc, CommandInvokeError) else exc

                if isinstance(error, Forbidden):
                    perms = ctx.guild.me.guild_permissions
                    missing_perms = []

                    if not perms.manage_channels:
                        missing_perms.append("`manage_channels`")
                    if not perms.manage_roles:
                        missing_perms.append("`manage_roles`")

                    if missing_perms:
                        error_msg = f"I'm missing the following permissions: {', '.join(missing_perms)}"
                    else:
                        error_msg = (
                            "I'm missing required permissions\n"
                            "> Please check my role's permissions and position"
                        )

                    return await ctx.denied(error_msg + f"\nError: {str(error)}")

                return await ctx.denied(str(error))

            origin = getattr(exc, "original", exc)

            with suppress(TypeError):
                if any(
                    forbidden in origin.args[-1]
                    for forbidden in (
                        "global check",
                        "check functions",
                        "Unknown Channel",
                    )
                ):
                    return

            return await ctx.denied(str(origin))

        else:
            return await ctx.send_help(ctx.command)
