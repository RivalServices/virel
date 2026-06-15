from discord import ButtonStyle, Embed, Interaction
from discord.ext.commands import Context
from discord.ui import View, Button, Modal, TextInput, button

from virel.core.config import Configuration


class PageModal(Modal, title="Go to page"):
    """
    A modal for navigating to a specific page in the paginator.
    """
    page = TextInput(label="Page number", placeholder="Enter a page number...", max_length=5)

    def __init__(self, paginator: "Paginator"):
        """
        Initializes the page modal.
 
        Args:
            paginator (Paginator): The paginator to navigate.
        """
        super().__init__()
        self.paginator = paginator

    async def on_submit(self, interaction: Interaction):
        """
        Called when the page modal is submitted.
        """
        try:
            value = int(self.page.value)
        except ValueError:
            return await interaction.response.send_message("That's not a valid number", ephemeral=True)

        if value < 1 or value > len(self.paginator.pages):
            return await interaction.response.send_message(
                f"Page must be between **1** and **{len(self.paginator.pages)}**.", ephemeral=True
            )

        await self.paginator._show(interaction, value - 1)


class Paginator(View):
    """
    A paginator for displaying a list of entries in an embed.
    """
    def __init__(
        self,
        ctx: Context,
        entries: list[str],
        *,
        embed: Embed = None,
        color: int = Configuration.Colors.neutral,
        per_page: int = 10,
        timeout: float = 10.0,
    ):
        """
        Initializes the paginator with the context, list of entries, and an optional timeout.
        Args:
            ctx (Context): The context of the command invocation.
            entries (list[str]): A list of string entries to paginate.
            embed (Embed, optional): A base embed template copied for each page. Defaults to None.
            per_page (int, optional): Number of entries per page. Defaults to 10.
            timeout (float, optional): How long the paginator should wait for interactions before timing out. Defaults to 30.0 seconds.
        """
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.current = 0
        self.message = None
        
        base = embed or Embed(color=color or Configuration.Colors.neutral)
        total = max(1, (len(entries) + per_page - 1) // per_page)
        self.pages = []
        for i in range(0, len(entries), per_page):
            chunk = entries[i:i + per_page]
            page = base.copy()
            page.description = "\n".join(f"{i + j + 1}. {e}" for j, e in enumerate(chunk))
            page.set_footer(text=f"Page {len(self.pages) + 1}/{total}")
            self.pages.append(page)

    async def interaction_check(self, interaction: Interaction) -> bool:
        """
        Checks if the user is the same as the context author.
        """
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("You can't use this paginator", ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        """
        Called when the paginator times out.
        """
        if self.message:
            await self.message.edit(view=None)

    async def start(self):
        """
        Starts the paginator by sending the first embed page to the context.
        """
        embed = self.pages[0] if self.pages else Embed(color=Configuration.Colors.neutral)
        self.message = await self.ctx.send(embed=embed, view=self if len(self.pages) > 1 else None)

    async def _show(self, interaction: Interaction, index: int):
        """
        Shows the embed at the given index.
        """
        self.current = index
        await interaction.response.edit_message(embed=self.pages[self.current])

    @button(emoji=f"{Configuration.Emojis.left}", style=ButtonStyle.grey)
    async def previous(self, interaction: Interaction, _btn: Button):
        """
        Shows the previous embed page.
        """
        await self._show(interaction, max(0, self.current - 1))

    @button(emoji=f"{Configuration.Emojis.right}", style=ButtonStyle.grey)
    async def next(self, interaction: Interaction, _btn: Button):
        """
        Shows the next embed page.
        """
        await self._show(interaction, min(len(self.pages) - 1, self.current + 1))

    @button(emoji=f"{Configuration.Emojis.navigate}", style=ButtonStyle.grey)
    async def navigate(self, interaction: Interaction, _btn: Button):
        """
        Shows the page modal.
        """
        await interaction.response.send_modal(PageModal(self))

    @button(emoji=f"{Configuration.Emojis.cancel}", style=ButtonStyle.red)
    async def stop_paginator(self, interaction: Interaction, _btn: Button):
        """
        Stops the paginator by editing the message to remove the view.
        """
        await interaction.response.edit_message(view=None)
        self.stop()