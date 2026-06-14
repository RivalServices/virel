import discord
from typing import Union, Optional
from discord import Embed
from discord.ext.commands import Context as BaseContext

from .paginator import Paginator
from virel.core.config import Configuration


class Context(BaseContext):
	"""
	Custom context class for Virel commands, extending the default discord.py Context
	to provide additional helper methods for sending embeds and approval messages.
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	async def dangerous_perms(self, role):
		"""
		Checks if a role has dangerous permissions.
		"""
		dangerous_perms = [
			perm for perm, value in role.permissions if value and perm in [
				"administrator", 
				"manage_guild", 
				"manage_channels", 
				"ban_members", 
				"kick_members",
				"manage_roles",
				"manage_permissions",
				"manage_webhooks",
				"manage_expressions",
				"manage_emojis",
				"manage_nicknames",
				"manage_messages",
				"manage_threads",
			]
		]
		return dangerous_perms

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
		emoji = Configuration.Emojis.approved
		message = f"{emoji} {self.author.mention}: {message}"
		

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
		emoji = Configuration.Emojis.denied
		message = f"{emoji} {self.author.mention}: {message}"
	   
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
		emoji = Configuration.Emojis.info
		message = f"{emoji} {self.author.mention}: {message}"

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
		emoji = Configuration.Emojis.warning
		message = f"{emoji} {self.author.mention}: {message}"

		if not embed:
			embed = Embed(description=message, color=color or Configuration.Colors.warning)
		
		return await self.reply(embed=embed)
	
#    async def paginate(
#        self, 
#        entries: list[str], 
#        *, 
#        embed: Embed = None, 
#        color: int = Configuration.Colors.neutral, 
#        per_page: int = 10, 
#        timeout: float = 10
#    ):
#        """
#        Sends a paginated embed message in the context of the command invocation.
#        Args:
#            entries (list[str]): A list of string entries to paginate.
#            embed (Embed, optional): A base embed template copied for each page. Defaults to None.
#            color (int, optional): The color of the embed. Defaults to Configuration.Colors.neutral.
#            per_page (int, optional): Number of entries per page. Defaults to 10.
#            timeout (float, optional): How long the paginator should wait for interactions before timing out. Defaults to 10 seconds.
#        """
#        paginator = Paginator(
#            self, 
#            entries, 
#            embed=embed, 
#            color=color, 
#            per_page=per_page, 
#            timeout=timeout
#        )
#        await paginator.start()


	async def alternative_paginate(self, embeds: list):
		from .paginator import Paginator
	
		paginator = Paginator(self.bot, embeds, self, invoker=self.author.id)
	
		if len(embeds) > 1:
			paginator.add_button("prev", emoji="<:left:1430582416355098665>", style=discord.ButtonStyle.grey)
			paginator.add_button("goto", emoji="<:navigate:1430580893201858580>", style=discord.ButtonStyle.grey)
			paginator.add_button("next", emoji="<:right:1430582394150326362>", style=discord.ButtonStyle.grey)
			paginator.add_button("delete", emoji="<:cancel:1430581170831101992>", style=discord.ButtonStyle.grey)
		elif len(embeds) == 1:
			pass
		
		return await paginator.start()

	async def paginate(
		self,
		embed: Union[discord.Embed, list],
		rows: Optional[list] = None,
		numbered: Optional[bool] = False,
		per_page: int = 10,
		type: str = "entry",
		plural_type: str = "entries",
	):
		def chunk_list(lst, n):
			return [lst[i:i + n] for i in range(0, len(lst), n)]
	
		class plural:
			def __init__(self, value):
				self.value = value
			def do_plural(self, text):
				bits = text.split("|")
				singular, pluralform = bits[0], bits[1] if len(bits) > 1 else bits[0] + "s"
				count = len(self.value) if isinstance(self.value, list) else self.value
				return f"{count} {singular if count == 1 else pluralform}"
	
		embeds = []
		if isinstance(embed, list):
			return await self.alternative_paginate(embed)
		if rows:
			if isinstance(rows[0], discord.Embed):
				embeds.extend(rows)
				return await self.alternative_paginate(embeds)
			else:
				if numbered and not rows[0].startswith("`1`"):
					rows = [f"`{i}` {row}" for i, row in enumerate(rows, start=1)]
				if len(rows) > int(per_page):
					chunks = chunk_list(rows, per_page)
					for i, chunk in enumerate(chunks, start=1):
						chunk_rows = [f"{c}\n" for c in chunk]
						page = embed.copy()
						page.description = "".join(chunk_rows)
						page.set_footer(
							text=f"Page {i}/{len(chunks)} ({plural(chunk_rows).do_plural(f'{type.title()}|{plural_type}') if not type.endswith('d') else type})"
						)
						embeds.append(page)
					return await self.alternative_paginate(embeds)
				else:
					embed.description = "".join(f"{r}\n" for r in rows)
					embed.set_footer(text=f"Page 1/1 ({plural(rows).do_plural(f'{type.title()}|{plural_type}') if not type.endswith('d') else type})")
					return await self.send(embed=embed)