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
                try:
                    await self.load_extension(f'cogs.{file[:-3]}')
                    print(f"Loaded extension {file}")
                except Exception as e:
                    print(f"Failed to load extension {file}: {e}")

        try:
            await self.tree.sync()
            print(f"Synchronized commands")
        except Exception as e:
            print(f"Synchronization failed: {e}")

    async def on_command_error(self, context: Context, error: commands.CommandError) -> None:
        if isinstance(error, commands.CommandNotFound):
            return
        print(error)

keep_alive()

if __name__ == '__main__':
    client = DiscordBot()
    client.run(os.getenv('TOKEN'))