
import logging

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from virel.core import Virel

logger = logging.getLogger("virel.core")


async def load_extensions(bot: "Virel"):
    """
    Loads all extensions found in the `extensions` directory by iterating over
    each subdirectory that contains an `__init__.py` file and attempting to
    load it as a bot extension.
    """
    extensions_dir = Path(__file__).resolve().parent.parent.parent.parent / "extensions"
    await bot.load_extension("jishaku")
    logger.info("Loaded extension: jishaku")

    for child in sorted(extensions_dir.iterdir()):
        if child.is_dir() and (child / "__init__.py").exists():
            module = f"virel.extensions.{child.name}"
            try:
                await bot.load_extension(module)
                logger.info(f"Loaded extension: {module}")
            
            except Exception as e:
                logger.error(f"Failed to load extension {module}: {e}")