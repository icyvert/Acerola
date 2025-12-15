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

    async def ping(self, context: Context) -> None:
        await context.send("Pong!")

async def setup(bot) -> None:
    await bot.add_cog(Ping(bot))