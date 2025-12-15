import discord
import os
from discord.ext import commands
from discord.ext.commands import Context
from dotenv import load_dotenv
from keep_alive import keep_alive

load_dotenv()

class DiscordBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        
        super().__init__(
            command_prefix=commands.when_mentioned_or('&'),
            intents=intents,
            help_command=None
        )

    async def setup_hook(self) -> None:
        for file in os.listdir('./cogs'):
            if file.endswith('.py'):
                await self.load_extension(f'cogs.{file[:-3]}')

    async def on_message(self, message: discord.Message) -> None:
        if message.author == self.user or message.author.bot:
            return
        await self.process_commands(message)

    async def on_command_error(self, context: Context, error: commands.CommandError) -> None:
        if isinstance(error, commands.CommandNotFound):
            return
        await super().on_command_error(context, error)

keep_alive()
bot = DiscordBot()
bot.run(os.getenv('TOKEN'))