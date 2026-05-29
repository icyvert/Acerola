from discord.ext import commands
from discord.ext.commands import Context


class Extension(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="unload", description="Unload extensions")
    @commands.is_owner()
    async def unload(self, context: Context, cog: str) -> None:
        extension = f"cogs.{cog}"

        try:
            await self.bot.unload_extension(extension)
            await context.send(f"Unloaded {extension}")
        except Exception:
            await context.send("Unload failed")

    @commands.hybrid_command(name="load", description="Load extensions")
    @commands.is_owner()
    async def load(self, context: Context, cog: str) -> None:
        extension = f"cogs.{cog}"

        try:
            await self.bot.load_extension(extension)
            await context.send(f"Loaded {extension}")
        except Exception:
            await context.send("Load failed")

    @commands.hybrid_command(name="reload", description="Reload extensions")
    @commands.is_owner()
    async def reload(self, context: Context, cog: str) -> None:
        extension = f"cogs.{cog}"

        try:
            await self.bot.reload_extension(extension)
            await context.send(f"Reloaded {extension}")
        except Exception:
            await context.send("Reload failed")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Extension(bot))
