from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context


class Ping(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="ping", description="「こんにちは世界」")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def ping(self, context: Context) -> None:
        latency = round(self.bot.latency * 1000)
        await context.send(f"{latency}ms")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Ping(bot))
