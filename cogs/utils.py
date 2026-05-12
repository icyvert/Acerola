import re
from typing import Literal

import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context


class Utils(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.domains = {
            "reddit.com": ("Reddit", "redditez.com", "rxddit.com"),
            "instagram.com": ("Instagram", "instafix.ldez.top", "kkinstagram.com"),
            "x.com": ("X", "fixupx.com", "fxtwitter.com"),
            "twitter.com": ("X", "fixupx.com", "fxtwitter.com"),
        }
        self.urls = re.compile(
            rf"(https?://)(?:[\w-]+\.)?({'|'.join(re.escape(d) for d in self.domains)})(/[\w\-./?=&%+]*)?"
        )

    def embed(self, match: re.Match, provider: str) -> str:
        protocol = match.group(1)
        domain = match.group(2)
        path = match.group(3) or ""
        index = 2 if provider.lower() == "alternate" else 1
        fixed_url = f"{protocol}{self.domains[domain][index]}{path}"
        response = f"[{self.domains[domain][0]}]({fixed_url})"
        return response

    @commands.hybrid_command(name="fix", description="Social embeds")
    @app_commands.describe(url="Instagram, Reddit or X link", provider="Embed provider")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def fix(
        self,
        context: Context,
        url: str,
        provider: Literal["default", "alternate"] = "default",
    ) -> None:
        match = self.urls.search(url)

        if not match:
            await context.send("Invalid link", ephemeral=True)
            return

        response = self.embed(match, provider)
        await context.send(response)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return

        if message.content.startswith("&"):
            return

        match = self.urls.search(message.content)

        if not match:
            return

        try:
            await message.edit(suppress=True)
        except Exception:
            pass

        response = self.embed(match, "default")
        await message.channel.send(response, mention_author=False)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Utils(bot))
