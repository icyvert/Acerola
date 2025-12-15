import discord
from discord.ext import commands
from discord.ext.commands import Context

class Chat(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.bot_id_str = str(bot.user.id)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return
        context: Context = await self.bot.get_context(message)
        if context.prefix is not None and self.bot_id_str in context.prefix and not context.valid:
            await message.reply("what")
            return

async def setup(bot) -> None:
    await bot.add_cog(Chat(bot))