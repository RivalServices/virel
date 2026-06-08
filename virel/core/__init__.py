import discord_ios

import logging
import os

from discord import Intents, AllowedMentions, Activity, ActivityType
from discord.ext.commands import AutoShardedBot

from datetime import datetime

from .config import Configuration
from .functions.context import Context
from .functions.discord import load_extensions, Help, get_prefix
from .services.postgres import PostgresClient
from .services.redis import RedisClient

logger = logging.getLogger("virel.core")
logging.getLogger("virel.core").setLevel(logging.INFO)
logging.getLogger("discord").setLevel(logging.INFO)
logging.getLogger("discord.gateway").setLevel(logging.INFO)


os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"
os.environ["JISHAKU_HIDE"] = "True"
os.environ["JISHAKU_FORCE_PAGINATOR"] = "True"
os.environ["JISHAKU_RETAIN"] = "True"


class Virel(AutoShardedBot):
    """
    Main bot class for Virel.

    Args:
        AutoShardedBot (_type_): The base class for a Discord bot that automatically shards itself across multiple guilds.
    """
    def __init__(self):
        super().__init__(
            command_prefix=get_prefix, 
            intents=Intents.all(),
            help_command=Help(),
            owner_ids=Configuration.Bot.owner_ids,
            activity=Activity(
                type=ActivityType.custom, 
                name="discord.gg/virel"
            ),
            allowed_mentions=(
                AllowedMentions(
                    everyone=False,
                    users=True,
                    replied_user=False,
                    roles=False
                )
            )
        )
        self.startup_time = datetime.now()

    async def on_command(self, ctx: Context):
        """
        Event called whenever a command is successfully invoked.
        """
        if ctx.valid:
            logging.info(f"Command {ctx.command.qualified_name} invoked by {ctx.author} ({ctx.author.id}) in {ctx.guild} ({ctx.guild.id})")

    async def get_context(self, origin, /, *, cls = Context):
        """
        Overrides the default get_context method to use the custom Context class
        defined in virel.core.functions.Context instead of the default discord.py
        Context class.
        """
        return await super().get_context(origin, cls=cls)

    async def setup_hook(self):
        """
        Called when the bot is setting up. This is where you can load
        extensions, cogs, or perform other asynchronous setup tasks.
        """
        self.db = PostgresClient()
        await self.db.connect()
        self.pool = self.db.pool

        self.redis = RedisClient()
        await self.redis.connect()

        await load_extensions(self)

    async def run(self):
        """
        Starts the bot using the token from the configuration.
        """
        await super().start(Configuration.Bot.token)

    async def close(self):
        """
        Closes the database and Redis connections when the bot is shutting down.
        """
        if hasattr(self, "db") and self.db:
            await self.db.close()
        if hasattr(self, "redis") and self.redis:
            await self.redis.close()
        
        await super().close()