import logging
import os
from pathlib import Path

import discord
from discord.ext import commands
from dotenv import load_dotenv


class DiscordBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        self.logger = logging.getLogger("bot")

        super().__init__(command_prefix="&", intents=intents, help_command=None)

    async def setup_hook(self) -> None:
        cogs_dir = Path(__file__).resolve().parent / "cogs"
        extensions = (
            f"cogs.{cog.stem}"
            for cog in cogs_dir.glob("*.py")
            if cog.name != "__init__.py"
        )

        for extension in extensions:
            try:
                await self.load_extension(extension)
                self.logger.info(f"Loaded extension {extension}")
            except Exception:
                self.logger.exception(f"Failed to load extension {extension}")

    async def on_command_error(
        self, context: commands.Context, error: commands.CommandError
    ) -> None:
        if isinstance(error, commands.CommandNotFound):
            return

        self.logger.error(f"Exception in command '{context.command}': {error}")


if __name__ == "__main__":
    load_dotenv()
    DiscordBot().run(os.environ["BOT_TOKEN"])
