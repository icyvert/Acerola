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
        cogs_dir = Path(__file__).parent / "cogs"

        for cog in cogs_dir.glob("*.py"):
            if cog.name == "__init__.py":
                continue

            extension = f"cogs.{cog.stem}"

            try:
                await self.load_extension(extension)
                self.logger.info("Loaded extension %s", extension)
            except Exception:
                self.logger.exception("Failed to load extension %s", extension)

    async def on_command_error(
        self, context: commands.Context, error: commands.CommandError
    ) -> None:
        if isinstance(error, commands.CommandNotFound):
            return

        self.logger.error(
            "Exception in command '%s': %s", context.command, error, exc_info=error
        )


if __name__ == "__main__":
    load_dotenv()
    DiscordBot().run(os.environ["BOT_TOKEN"])
