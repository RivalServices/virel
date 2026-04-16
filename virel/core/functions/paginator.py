from discord import ButtonStyle, Embed, Interaction, Message
from discord.ext.commands import Context
from discord.ui import View, Button, button


class Paginator(View):
    """
    A paginator view that allows a user to navigate through multiple pages of embeds
    using buttons. Only the user who invoked the paginator can interact with it.
    """
    def __init__(self, ctx: Context, entries: list[str], *, embed: Embed = None, per_page: int = 10, timeout: float = 30.0):
        """
        Initializes the paginator with the context, list of entries, and an optional timeout.
        Args:
            ctx (Context): The context of the command invocation.
            entries (list[str]): A list of string entries to paginate.
            embed (Embed, optional): A base embed to use for styling (title, color). Defaults to None.
            per_page (int, optional): Number of entries per page. Defaults to 10.
            timeout (float, optional): How long the paginator should wait for interactions before timing out. Defaults to 30.0 seconds.
        """
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.entries = entries
        self.per_page = per_page
        self.base_embed = embed or Embed()
        self.current = 0
        self.message: Message | None = None
        self.pages = self._build_pages()

    def _build_pages(self) -> list[Embed]:
        """
        Splits entries into chunks and builds indexed embed pages.
        """
        pages = []
        for i in range(0, len(self.entries), self.per_page):
            chunk = self.entries[i:i + self.per_page]
            description = "\n".join(
                f"`{i + j + 1}.` {entry}" for j, entry in enumerate(chunk)
            )
            embed = Embed(
                title=self.base_embed.title,
                description=description,
                color=self.base_embed.color,
            )
            embed.set_footer(text=f"Page {len(pages) + 1}/{-(-len(self.entries) // self.per_page)}")
            pages.append(embed)
        return pages

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

        if len(self.pages) <= 1:
            self.message = await self.ctx.send(embed=self.pages[0] if self.pages else self.base_embed)
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