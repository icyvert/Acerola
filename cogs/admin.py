import discord
from discord.ext import commands
from discord.ext.commands import Context
from typing import Literal

class Admin(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command(
        name="sync",
        description="Sync slash commands"
    )
    @commands.guild_only()
    @commands.is_owner()
    async def sync(self, context: Context, scope: Literal["global", "guild", "clear"]) -> None:
        if scope == "global":
            await context.bot.tree.sync()
            await context.send("Synchronized Globally")
            return  
        elif scope == "guild":
            context.bot.tree.copy_global_to(guild=context.guild)
            await context.bot.tree.sync(guild=context.guild)
            await context.send("Synchronized Locally")
            return
        elif scope == "clear":    
            context.bot.tree.clear_commands(guild=context.guild)
            await context.bot.tree.sync(guild=context.guild)
            await context.send("Cleared Local Commands")

async def setup(bot) -> None:
    await bot.add_cog(Admin(bot))