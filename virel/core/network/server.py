from __future__ import annotations

import logging
import uvicorn

from typing import TYPE_CHECKING

from litestar import Litestar
from litestar.config.cors import CORSConfig

from .routes import commands, guilds, health

if TYPE_CHECKING:
    from virel.core import Virel

logger = logging.getLogger("virel.core.network")

def make_app(bot: "Virel") -> Litestar:
    """
    Create a Litestar app for the bot.
    
    Args:
        bot: The bot instance.
        
    Returns:
        The Litestar app.
    """
    async def on_startup(app: Litestar) -> None:
        app.state.bot = bot

    return Litestar(
        route_handlers=[health, guilds, commands],
        cors_config=CORSConfig(allow_origins=["*"]),
        on_startup=[on_startup],
        logging_config=None,
    )


class NetworkServer:
    """
    Network server for the bot.
    """
    def __init__(self, bot: "Virel", host: str = "0.0.0.0", port: int = 8080):
        """
        Initialize the network server.
        
        Args:
            bot: The bot instance.
            host: The host to bind to.
            port: The port to bind to.
        """
        self.bot = bot
        self.host = host
        self.port = port
        self._server: uvicorn.Server | None = None

    async def start(self):
        """
        Start the network server.
        """
        app = make_app(self.bot)
        config = uvicorn.Config(
            app,
            host=self.host,
            port=self.port,
            log_level="info",
            log_config=None,
        )
        self._server = uvicorn.Server(config)
        logger.info(f"Network API starting on {self.host}:{self.port}")
        await self._server.serve()

    async def stop(self):
        """
        Stop the network server.
        """
        if self._server:
            self._server.should_exit = True
