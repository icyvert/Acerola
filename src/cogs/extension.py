from typing import Literal

from discord.ext import commands


class Extension(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="extension", description="Manage extensions")
    @commands.is_owner()
    async def extension(
        self,
        context: commands.Context[commands.Bot],
        action: Literal["load", "unload", "reload"],
        cog: str,
    ) -> None:
        await context.defer(ephemeral=True)
        extension = f"cogs.{cog}"
        try:
            method = getattr(self.bot, f"{action}_extension")
            await method(extension)
            await context.send(f"{action}ed {extension}")
        except commands.ExtensionError as error:
            await context.send(f"{action} failed: {error}")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Extension(bot))
