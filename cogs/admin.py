from discord.ext import commands
from discord.ext.commands import Context
from typing import Literal

class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(
        name="sync"
    )
    @commands.guild_only()
    @commands.is_owner()
    async def sync(self, context: Context, scope: Literal['global', 'guild', 'clear'] = 'guild') -> None:
        match scope:
            case 'global':
                await self.bot.tree.sync()
                await context.send("Synchronized Globally")
            case 'guild':
                self.bot.tree.copy_global_to(guild=context.guild)
                await self.bot.tree.sync(guild=context.guild)
                await context.send("Synchronized Locally")
            case 'clear':   
                self.bot.tree.clear_commands(guild=context.guild)
                await self.bot.tree.sync(guild=context.guild)
                await context.send("Cleared Local Commands")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Admin(bot))