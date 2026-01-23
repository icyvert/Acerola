import discord

from discord.ext import commands
from discord.ext.commands import Context


class Chat(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return
        if self.bot.user in message.mentions:
            context: Context = await self.bot.get_context(message)
            if context.prefix and not context.valid:
                await message.reply("what")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Chat(bot))
