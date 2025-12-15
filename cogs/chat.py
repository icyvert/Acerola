import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context

class Chat(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if self.bot.user in message.mentions:
            context: Context = await self.bot.get_context(message)
            if not context.valid and context.prefix:
                await message.reply("what")
                return
            return

async def setup(bot) -> None:
    await bot.add_cog(Chat(bot))