from discord import ButtonStyle, Embed, Interaction, Message
from discord.ext.commands import Context
from discord.ui import View, Button, button


class Paginator(View):
    """
    A paginator view that allows a user to navigate through multiple pages of embeds
    using buttons. Only the user who invoked the paginator can interact with it.
    """
    def __init__(self, ctx: Context, pages: list[Embed], *, timeout: float = 30.0):
        """
        Initializes the paginator with the context, list of embed pages, and an optional timeout.
        Args:
            ctx (Context): The context of the command invocation.
            pages (list[Embed]): A list of embed pages to paginate through.
            timeout (float, optional): How long the paginator should wait for interactions before timing out. Defaults to 30.0 seconds.
        """
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.pages = pages
        self.current = 0
        self.message: Message | None = None
        self._index_pages()

    def _index_pages(self):
        """
        Adds a footer to each embed page indicating its position in the paginator.
        """
        for i, page in enumerate(self.pages):
            page.set_footer(text=f"Page {i + 1}/{len(self.pages)}")

    async def interaction_check(self, interaction: Interaction) -> bool:
        """
        Checks if the user interacting with the paginator is the same as the user
        who invoked the command. If not, sends an ephemeral message indicating
        they cannot use the paginator.
        """
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message(
                "You can't use this paginator", ephemeral=True
            )
            return False
        return True

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        if self.message:
            await self.message.edit(view=self)

    async def start(self):
        """
        Starts the paginator by sending the first embed page to the context.
        If there is only one page, it sends it without the view. Otherwise,
        it sends the first page with the paginator view attached.
        """

        if len(self.pages) == 1:
            self.message = await self.ctx.send(embed=self.pages[0])
            return

        self.message = await self.ctx.send(embed=self.pages[0], view=self)

    @button(emoji="⏮", style=ButtonStyle.grey)
    async def first(self, interaction: Interaction, btn: Button):
        """
        Navigates to the first page of the paginator and updates the message
        with the corresponding embed.
        """

        self.current = 0
        await interaction.response.edit_message(embed=self.pages[self.current])

    @button(emoji="◀", style=ButtonStyle.grey)
    async def previous(self, interaction: Interaction, btn: Button):
        """
        Navigates to the previous page of the paginator and updates the message
        with the corresponding embed.
        """

        self.current = max(0, self.current - 1)
        await interaction.response.edit_message(embed=self.pages[self.current])

    @button(emoji="▶", style=ButtonStyle.grey)
    async def next(self, interaction: Interaction, btn: Button):
        """
        Navigates to the next page of the paginator and updates the message
        with the corresponding embed.
        """

        self.current = min(len(self.pages) - 1, self.current + 1)
        await interaction.response.edit_message(embed=self.pages[self.current])

    @button(emoji="⏭", style=ButtonStyle.grey)
    async def last(self, interaction: Interaction, btn: Button):
        """
        Navigates to the last page of the paginator and updates the message
        with the corresponding embed.
        """

        self.current = len(self.pages) - 1
        await interaction.response.edit_message(embed=self.pages[self.current])

    @button(emoji="⏹", style=ButtonStyle.red)
    async def stop_paginator(self, interaction: Interaction, btn: Button):
        """
        Stops the paginator by disabling all buttons and editing the message
        to remove the interactive view.
        """

        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(view=self)
        self.stop()