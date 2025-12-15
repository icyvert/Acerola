import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context

class Ping(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(
        name="ping",
        description="Is it alive?"
    )
    @commands.is_owner()
    async def ping(self, context: Context) -> None:
        latency = round(self.bot.latency * 1000)
        await context.send(f"{latency}ms")

async def setup(bot) -> None:
    await bot.add_cog(Ping(bot))