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
	
	async def paginate(
       self, 
       entries: list[str], 
       *, 
       embed: Embed = None, 
       color: int = Configuration.Colors.neutral, 
       per_page: int = 10, 
       timeout: float = 10
   ):
		"""
		Sends a paginated embed message in the context of the command invocation.
		Args:
			entries (list[str]): A list of string entries to paginate.
			embed (Embed, optional): A base embed template copied for each page. Defaults to None.
			color (int, optional): The color of the embed. Defaults to Configuration.Colors.neutral.
			per_page (int, optional): Number of entries per page. Defaults to 10.
			timeout (float, optional): How long the paginator should wait for interactions before timing out. Defaults to 10 seconds.
		"""
		paginator = Paginator(
			self, 
			entries, 
			embed=embed, 
			color=color, 
			per_page=per_page, 
			timeout=timeout
		)
		await paginator.start()