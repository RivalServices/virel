from discord import Embed
from discord.ext.commands import Context as BaseContext

from virel.core.config import Configuration


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
            embed = Embed(description=message, color=color or Configuration.Colors.approved)
        
        return await self.reply(embed=embed)
    
    async def denied(
        self, 
        message: str,
        color: int = None,
        **kwargs
    ):
        """
        Sends a denial embed message in the context of the command invocation.
        """
        embed = kwargs.get("embed")
        if not embed:
            embed = Embed(description=message, color=color or Configuration.Colors.denied)
        
        return await self.reply(embed=embed)
    
    async def info(
        self, 
        message: str,
        color: int = None,
        **kwargs
    ):
        """
        Sends an informational embed message in the context of the command invocation.
        """
        embed = kwargs.get("embed")
        if not embed:
            embed = Embed(description=message, color=color or Configuration.Colors.info)
        
        return await self.reply(embed=embed)
    
    async def warning(
        self, 
        message: str,
        color: int = None,
        **kwargs
    ):
        """
        Sends a warning embed message in the context of the command invocation.
        """
        embed = kwargs.get("embed")
        if not embed:
            embed = Embed(description=message, color=color or Configuration.Colors.warning)
        
        return await self.reply(embed=embed)