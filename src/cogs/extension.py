from typing import Any, Literal

from discord import app_commands
from discord.ext import commands


class Extension(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="extension", description="Manage extensions")
    @commands.guild_only()
    @commands.is_owner()
    @app_commands.default_permissions(administrator=True)
    async def extension(
        self,
        context: commands.Context[Any],
        action: Literal["load", "unload", "reload"],
        cog: str,
    ) -> None:
        await context.defer(ephemeral=True)
        extension = f"cogs.{cog}"
        try:
            method = getattr(self.bot, f"{action}_extension")
            await method(extension)
            await context.send(f"{action}ed {extension}")
        except commands.ExtensionError as error:
            await context.send(f"{action} failed: {error}")

    @commands.hybrid_command(name="ping", description="「こんにちは世界」")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def ping(self, context: commands.Context[Any]) -> None:
        latency = round(self.bot.latency * 1000)
        await context.send(f"{latency}ms")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Extension(bot))
