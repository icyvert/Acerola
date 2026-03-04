import re

from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context


class Utils(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.domains = {
            "reddit.com": "vxreddit.com",
            "instagram.com": "instafix.ldez.top",
            "x.com": "fixupx.com",
            "twitter.com": "fxtwitter.com",
        }
        self.urls = re.compile(
            rf"(https?://)(?:www\.)?({'|'.join(re.escape(d) for d in self.domains)})(/[\w\-./?=&%+]*)?"
        )

    @commands.hybrid_command(name="fix", description="Social embeds")
    @app_commands.describe(url="Reddit, Instagram or X link")
    async def fix(self, context: Context, url: str) -> None:
        match = self.urls.search(url)

        if not match:
            await context.send("Invalid link", ephemeral=True)
            return

        protocol = match.group(1)
        domain = match.group(2)
        path = match.group(3) or ""
        fixed_url = f"{protocol}{self.domains[domain]}{path}"

        await context.send(fixed_url)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Utils(bot))
