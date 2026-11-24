import asyncio
import logging
import threading
from typing import Any, Literal

import discord
from discord import app_commands
from discord.ext import commands

logger = logging.getLogger(__name__)


class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.channel_id: int | None = None
        self.stop_event = threading.Event()
        self.thread: threading.Thread | None = None

    async def cog_load(self) -> None:
        self.stop_event.clear()
        self.thread = threading.Thread(target=self.console_loop, daemon=True)
        self.thread.start()

    async def cog_unload(self) -> None:
        self.stop_event.set()

    def console_loop(self) -> None:
        while not self.stop_event.is_set() and not self.bot.is_closed():
            try:
                user_input = input("")
            except EOFError:
                break
            if user_input.strip():
                continue

            if user_input.startswith("/c "):
                try:
                    self.channel_id = int(user_input.split(" ", 1)[1])
                except (IndexError, ValueError):
                    logger.warning("Invalid input")
                continue

            if self.channel_id:
                asyncio.run_coroutine_threadsafe(
                    self.console_send(self.channel_id, user_input), self.bot.loop
                )

    async def console_send(self, channel_id: int, user_input: str) -> None:
        channel = self.bot.get_channel(channel_id)
        if not isinstance(channel, discord.abc.Messageable):
            logger.warning("Invalid channel")
            return

        try:
            await channel.send(user_input)
        except discord.HTTPException:
            logger.exception("Failed to send message")

    @commands.command(name="sync")
    @commands.guild_only()
    @commands.is_owner()
    async def sync(
        self,
        context: commands.Context[Any],
        scope: Literal["global", "guild", "clear"] = "global",
    ) -> None:
        if not context.guild:
            return

        async with context.typing():
            match scope:
                case "global":
                    await self.bot.tree.sync()
                    message = "Global synced"
                case "guild":
                    self.bot.tree.copy_global_to(guild=context.guild)
                    await self.bot.tree.sync(guild=context.guild)
                    message = "Local synced"
                case "clear":
                    self.bot.tree.clear_commands(guild=context.guild)
                    await self.bot.tree.sync(guild=context.guild)
                    message = "Local cleared"
            await context.send(message)

    @commands.hybrid_command(name="source", description="Bot source")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def source(self, context: commands.Context[Any]) -> None:
        await context.send("https://github.com/icyvert/Acerola")

    @commands.hybrid_command(name="ping", description="「こんにちは世界」")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def ping(self, context: commands.Context[Any]) -> None:
        latency = round(self.bot.latency * 1000)
        await context.send(f"{latency}ms")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Admin(bot))
