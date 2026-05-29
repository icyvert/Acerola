import asyncio
from typing import Literal

import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context


class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.channel_id = None

    async def cog_load(self):
        self.console = self.bot.loop.create_task(self.console_chat())

    async def cog_unload(self):
        self.console.cancel()

    async def console_chat(self):
        while not self.bot.is_closed():
            user_input = await asyncio.to_thread(input, "")

            if not user_input.strip():
                continue

            if user_input.startswith("/c "):
                try:
                    self.channel_id = int(user_input.split()[1])
                except Exception:
                    print("Invalid")
                continue

            if self.channel_id:
                channel = self.bot.get_channel(self.channel_id)

                if isinstance(channel, discord.abc.Messageable):
                    await channel.send(user_input)
                    continue

                print("Invalid")

    @commands.command(name="sync")
    @commands.guild_only()
    @commands.is_owner()
    async def sync(
        self, context: Context, scope: Literal["global", "guild", "clear"] = "global"
    ) -> None:
        async with context.typing():
            assert context.guild is not None

            match scope:
                case "global":
                    await self.bot.tree.sync()
                    await context.send("Synchronized Globally")

                case "guild":
                    self.bot.tree.copy_global_to(guild=context.guild)
                    await self.bot.tree.sync(guild=context.guild)
                    await context.send("Synchronized Locally")

                case "clear":
                    self.bot.tree.clear_commands(guild=context.guild)
                    await self.bot.tree.sync(guild=context.guild)
                    await context.send("Cleared Local Commands")

    @commands.hybrid_command(name="source", description="Bot source")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def source(self, context: Context) -> None:
        await context.send("https://github.com/icyvert/Acerola")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Admin(bot))
