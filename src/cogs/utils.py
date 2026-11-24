import re
from typing import Literal

import discord
from discord import app_commands
from discord.ext import commands


class Utils(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.domains: dict[str, tuple[str, str, str]] = {
            "instagram.com": ("Instagram", "oginstagram.com", "axinstagram.com"),
            "reddit.com": ("Reddit", "redditez.com", "rxddit.com"),
            "twitter.com": ("Twitter", "fxtwitter.com", "fixupx.com"),
            "x.com": ("X", "fixupx.com", "fxtwitter.com"),
        }
        self.urls = re.compile(
            rf"(https?://)(?:[\w-]+\.)?({'|'.join(re.escape(domain) for domain in self.domains)})(?=/|\s|$)(/[\w\-./?=&%+]*)?"
        )

    def embed(self, match: re.Match[str], provider: str) -> str:
        protocol, domain, path = match.groups()
        path = path or ""
        domains = self.domains[domain]
        index = 2 if provider.lower() == "alternate" else 1
        fixed_url = f"{protocol}{domains[index]}{path}"
        return f"[{domains[0]}]({fixed_url})"

    @commands.hybrid_command(name="fix", description="Social embeds")
    @app_commands.describe(url="Instagram, Reddit or X link", provider="Embed provider")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def fix(
        self,
        context: commands.Context[commands.Bot],
        url: str,
        provider: Literal["default", "alternate"] = "default",
    ) -> None:
        match = self.urls.search(url)
        if not match:
            await context.send("Invalid link", ephemeral=True)
            return
        await context.send(self.embed(match, provider))

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return
        match = self.urls.search(message.content)
        if not match:
            return
        context = await self.bot.get_context(message)
        if context.valid:
            return

        try:
            await message.channel.send(self.embed(match, "default"))
            await message.edit(suppress=True)
        except discord.HTTPException:
            pass


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Utils(bot))
