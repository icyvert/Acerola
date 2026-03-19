import re

import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context


class Utils(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.domains = {
            "reddit.com": "vxreddit.com",
            "instagram.com": "vxinstagram.com",
            "x.com": "fixupx.com",
            "twitter.com": "fixupx.com",
        }
        self.altdomains = {
            "reddit.com": "rxddit.com",
            "instagram.com": "instafix.ldez.top",
            "x.com": "fxtwitter.com",
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

    def embed(self, match: re.Match, embed: str) -> str:
        protocol = match.group(1)
        domain = match.group(2)
        path = match.group(3) or ""

        if embed.lower() == "alternate":
            fixed_url = f"{protocol}{self.altdomains[domain]}{path}"
        else:
            fixed_url = f"{protocol}{self.domains[domain]}{path}"

        response = f"[{self.sites[domain]}]({fixed_url})"
        return response

    @commands.hybrid_command(name="fix", description="Social embeds")
    @app_commands.describe(url="Instagram, Reddit or X link", embed="Embed provider")
    @app_commands.choices(
        embed=[
            app_commands.Choice(name="Default", value="default"),
            app_commands.Choice(name="Alternate", value="alternate"),
        ]
    )
    async def fix(self, context: Context, url: str, embed: str = "default") -> None:
        match = self.urls.search(url)

        if not match:
            await context.send("Invalid link", ephemeral=True)
            return

        response = self.embed(match, embed)
        await context.send(response)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return

        match = self.urls.search(message.content)

        if not match:
            return

        try:
            await message.edit(suppress=True)
        except Exception:
            pass

        response = self.embed(match, "default")
        await message.reply(response, mention_author=False)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Utils(bot))
