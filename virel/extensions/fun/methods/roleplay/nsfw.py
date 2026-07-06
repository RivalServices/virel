from discord import Embed, Member

from yarl import URL

from virel.core import Virel
from virel.core.config import Configuration
from virel.core.functions.context import Context
from virel.core.config import Configuration

from .actions import ACTIONS


def api_url(category: str) -> URL:
    """
    Generate a URL for the PurrBot API.
    """
    return URL.build(
        scheme="https",
        host="api.purrbot.site",
        path=f"/v2/img/nsfw/{category}/gif",
    ).with_query(proxy=Configuration.Bot.proxy_url)


def format_action(category: str, member: Member) -> str:
    """
    Format the action for the embed.
    """
    action = ACTIONS[category]
    if action.startswith("gave a ") and action.endswith(" to"):
        return f"gave **{member.display_name}** a {category}"
    return f"{action} **{member.display_name}**"


class PurrBot:
    def __init__(self, bot: Virel):
        """
        Initialize the PurrBot class.
        """
        self.bot = bot

    async def send(self, ctx: Context, member: Member | None, category: str):
        """
        Send an NSFW roleplay embed.
        """
        async with self.bot.session.get(api_url(category)) as response:
            data = await response.json()

        embed = Embed(color=Configuration.Colors.neutral)
        if member is not None:
            embed.description = (
                f"*Oh fuck!* **{ctx.author.display_name}** "
                f"{format_action(category, member)}"
            )
        embed.set_image(url=data["link"])
        return await ctx.send(embed=embed)
