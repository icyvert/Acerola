import logging
import os
from pathlib import Path
from typing import Any

import discord
from discord.ext import commands
from dotenv import load_dotenv


class DiscordBot(commands.Bot):
    def __init__(self) -> None:
        self.logger = logging.getLogger("bot")
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="&", intents=intents, help_command=None)

    async def setup_hook(self) -> None:
        cogs_dir = Path(__file__).parent / "cogs"
        for cog in cogs_dir.glob("*.py"):
            if cog.name.startswith("_"):
                continue

            extension = f"cogs.{cog.stem}"
            try:
                await self.load_extension(extension)
                self.logger.info("Loaded %s", extension)
            except Exception:
                self.logger.exception("Failed to load %s", extension)

    async def on_command_error(
        self, context: commands.Context[Any], error: commands.CommandError
    ) -> None:
        if isinstance(error, commands.CommandNotFound):
            return

        self.logger.error("Exception in command %s", context.command, exc_info=error)
        if context.interaction and not context.interaction.is_expired():
            try:
                await context.send("Command failed", ephemeral=True)
            except discord.HTTPException:
                pass


if __name__ == "__main__":
    load_dotenv()
    DiscordBot().run(os.environ["BOT_TOKEN"], root_logger=True)
