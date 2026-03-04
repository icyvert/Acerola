import re

import discord
from discord import app_commands
from discord.ext import commands


class Utils(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.domains = {
            "reddit.com": "vxreddit.com",
            "instagram.com": "instafix.ldez.top",
            "x.com": "fixupx.com",
            "twitter.com": "fxtwitter.com",
        }
        self.altdomains = {
            "reddit.com": "rxddit.com",
            "instagram.com": "vxinstagram.com",
            "x.com": "fixupx.com",
            "twitter.com": "fxtwitter.com",
        }
        self.sites = {
            "reddit.com": "Reddit",
            "instagram.com": "Instagram",
            "x.com": "X",
            "twitter.com": "X",
        }
        self.urls = re.compile(
            rf"(https?://)(?:www\.)?({'|'.join(re.escape(d) for d in self.domains)})(/[\w\-./?=&%+]*)?"
        )

    @app_commands.command(name="fix", description="Social embeds")
    @app_commands.describe(url="Reddit, Instagram or X link")
    async def fix(
        self, interaction: discord.Interaction, url: str, embed: str = "Default"
    ) -> None:
        match = self.urls.search(url)

        if not match:
            await interaction.response.send_message("Invalid link", ephemeral=True)
            return

        protocol = match.group(1)
        domain = match.group(2)
        path = match.group(3) or ""

        match embed:
            case "Default":
                fixed_url = f"{protocol}{self.domains[domain]}{path}"
            case "Alternate":
                fixed_url = f"{protocol}{self.altdomains[domain]}{path}"

        await interaction.response.send_message(f"[{self.sites[domain]}]({fixed_url})")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Utils(bot))
