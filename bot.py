import logging
import os
from pathlib import Path

import discord
from discord.ext import commands
from dotenv import load_dotenv

from keep_alive import keep_alive

load_dotenv()


class DiscordBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(
            command_prefix="&",
            intents=intents,
            help_command=None,
        )
        self.logger = logging.getLogger("bot")

    async def setup_hook(self) -> None:
        cogs_dir = Path(__file__).resolve().parent / "cogs"
        for file in cogs_dir.glob("*.py"):
            if file.name == "__init__.py":
                continue

            extension = f"cogs.{file.stem}"

            try:
                await self.load_extension(extension)
                self.logger.info(f"Loaded extension {extension}")
            except Exception:
                self.logger.exception(f"Failed to load extension {extension}")

    async def on_command_error(self, _, error: commands.CommandError) -> None:
        if isinstance(error, commands.CommandNotFound):
            return
        self.logger.error(error)


if __name__ == "__main__":
    keep_alive()
    discord.utils.setup_logging()
    client = DiscordBot()
    client.run(os.getenv("BOT_TOKEN"))
