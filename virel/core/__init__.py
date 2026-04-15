from discord import Intents, AllowedMentions
from discord.ext.commands import AutoShardedBot, MinimalHelpCommand

from .config import Configuration


class Virel(AutoShardedBot):
    """
    Main bot class for Virel.

    Args:
        AutoShardedBot (_type_): The base class for a Discord bot that automatically shards itself across multiple guilds.
    """
    def __init__(self):
        super().__init__(
            command_prefix=Configuration.Bot.prefix, 
            intents=Intents.all(),
            help_command=MinimalHelpCommand(),
            allowed_mentions=(
                AllowedMentions(
                    everyone=False,
                    users=True,
                    replied_user=False,
                    roles=False
                )
            )
        )

    async def setup_hook(self):
        """
        Called when the bot is setting up. This is where you can load
        extensions, cogs, or perform other asynchronous setup tasks.
        """
        pass

    async def run(self):
        """
        Starts the bot using the token from the configuration.
        """
        await super().start(Configuration.Bot.token)