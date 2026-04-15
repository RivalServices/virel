from discord import Embed
from discord.ext.commands import Context as BaseContext


class Context(BaseContext):
    """
    Custom context class for Virel commands, extending the default discord.py Context
    to provide additional helper methods for sending embeds and approval messages.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def approved(
        self, 
        message: str,
        color: int = None,
        **kwargs
    ):
        """
        Sends an approval embed message in the context of the command invocation.
        """
        embed = kwargs.get("embed")
        if not embed:
            embed = Embed(description=message, color=color)
        
        return await self.reply(embed=embed)