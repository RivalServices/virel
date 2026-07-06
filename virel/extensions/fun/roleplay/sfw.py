from ..methods.roleplay import Otaku
from virel.core import Virel
from virel.core.functions.context import Context

from discord import Member
from discord.ext.commands import Cog, command, Author

class SFW(Cog):
    """
    Do NSFW actions on other members.
    """
    def __init__(self, bot: Virel):
        self.bot = bot
        self.otaku = Otaku(bot)

    @command()
    async def hug(self, ctx: Context, member: Member = Author):
        """
        Hug a member.
        """
        await self.otaku.send(ctx, member, "hug")

    @command()
    async def kiss(self, ctx: Context, member: Member = Author):
        """
        Kiss a member.
        """
        await self.otaku.send(ctx, member, "kiss")

    @command()
    async def cuddle(self, ctx: Context, member: Member = Author):
        """
        Cuddle a member.
        """
        await self.otaku.send(ctx, member, "cuddle")

    @command()
    async def slap(self, ctx: Context, member: Member = Author):
        """
        Slap a member.
        """
        await self.otaku.send(ctx, member, "slap")

    @command()
    async def tickle(self, ctx: Context, member: Member = Author):
        """
        Tickle a member.
        """
        await self.otaku.send(ctx, member, "tickle")