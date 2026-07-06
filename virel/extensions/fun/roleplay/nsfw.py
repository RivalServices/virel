from ..methods.roleplay import PurrBot
from virel.core import Virel
from virel.core.functions.context import Context

from discord import Member
from discord.ext.commands import Cog, command, is_nsfw, Author

class NSFW(Cog):
    """
    Do NSFW actions on other members.
    """
    def __init__(self, bot: Virel):
        self.bot = bot
        self.purrbot = PurrBot(bot)

    @is_nsfw()
    @command()
    async def anal(self, ctx: Context, member: Member = Author):
        """
        Give anal sex to a member.
        """
        await self.purrbot.send(ctx, member, "anal")

    @is_nsfw()
    @command(aliases=["bj"])
    async def blowjob(self, ctx: Context, member: Member = Author):
        """
        Give a blowjob to a member.
        """
        await self.purrbot.send(ctx, member, "blowjob")

    @is_nsfw()
    @command()
    async def cum(self, ctx: Context, member: Member = Author):
        """
        Cum on a member.
        """
        await self.purrbot.send(ctx, member, "cum")

    @is_nsfw()
    @command()
    async def fuck(self, ctx: Context, member: Member = Author):
        """
        Have sex with a member.
        """
        await self.purrbot.send(ctx, member, "fuck")

    @is_nsfw()
    @command()
    async def pussylick(self, ctx: Context, member: Member = Author):
        """
        Lick a member's pussy.
        """
        await self.purrbot.send(ctx, member, "pussylick")

    @is_nsfw()
    @command()
    async def solo(self, ctx: Context):
        """
        Have sex with yourself.
        """
        await self.purrbot.send(ctx, None, "solo")