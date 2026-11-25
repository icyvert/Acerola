import asyncio
import logging
import threading

import discord
from discord import app_commands
from discord.ext import commands


class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        self.channel_id: int | None = None
        self.stop_event = threading.Event()
        self.thread: threading.Thread | None = None

    async def cog_load(self) -> None:
        self.loop = asyncio.get_running_loop()
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
            if self.stop_event.is_set() or self.bot.is_closed():
                break
            if not user_input.strip():
                continue

            if user_input.startswith("/c "):
                try:
                    self.channel_id = int(user_input.split(" ", 1)[1])
                except (IndexError, ValueError):
                    self.logger.warning("Invalid input")
                continue
            if self.channel_id is None:
                self.logger.warning("No channel")
                continue

            if self.loop.is_running():
                asyncio.run_coroutine_threadsafe(
                    self.console_send(self.channel_id, user_input), self.loop
                )

    async def console_send(self, channel_id: int, user_input: str) -> None:
        channel = self.bot.get_channel(channel_id)
        if not isinstance(channel, discord.abc.Messageable):
            self.logger.warning("Invalid channel")
            return

        try:
            await channel.send(user_input)
        except discord.HTTPException:
            self.logger.exception("Failed to send message")

    @commands.command(name="sync")
    @commands.is_owner()
    async def sync(self, context: commands.Context[commands.Bot]) -> None:
        if not context.guild:
            return
        try:
            async with context.typing():
                await self.bot.tree.sync()
                await context.send("Synced")
        except discord.HTTPException:
            self.logger.exception("Failed to sync")

    @commands.hybrid_command(name="source", description="Bot source")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def source(self, context: commands.Context[commands.Bot]) -> None:
        await context.send("https://github.com/icyvert/Acerola")

    @commands.hybrid_command(name="ping", description="「こんにちは世界」")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def ping(self, context: commands.Context[commands.Bot]) -> None:
        latency = round(self.bot.latency * 1000)
        await context.send(f"{latency}ms")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Admin(bot))
