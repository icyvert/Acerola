import logging
import random
from typing import Any

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands


class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        self.parameters: str = "hatsune_miku favcount:>30"
        self.limit: int = 30
        self.sensitive: bool = False
        self.session: aiohttp.ClientSession | None = None

    async def cog_load(self) -> None:
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10),
            headers={"User-Agent": "Acerola/8.0"},
        )

    async def cog_unload(self) -> None:
        if self.session and not self.session.closed:
            await self.session.close()

    async def fetch_post(self) -> dict[str, Any] | None:
        if not self.session or self.session.closed:
            return None

        params = {
            "tags": f"{self.parameters}",
            "limit": f"{self.limit}",
            "random": "true",
        }
        async with self.session.get(
            "https://danbooru.donmai.us/posts.json", params=params
        ) as response:
            response.raise_for_status()
            posts: list[dict[str, Any]] = await response.json()

        file_ext = {"jpg", "jpeg", "png", "webp"}
        rating = {"g", "s"} if self.sensitive else {"g"}
        valid = [
            post
            for post in posts
            if post.get("id")
            and not post.get("is_deleted")
            and not post.get("is_banned")
            and post.get("file_ext") in file_ext
            and post.get("large_file_url")
            and post.get("rating") in rating
        ]
        return random.choice(valid) if valid else None

    @commands.hybrid_command(name="toggle", description="Toggle rating")
    @commands.is_owner()
    async def toggle(self, context: commands.Context[commands.Bot]) -> None:
        self.sensitive = not self.sensitive
        await context.send(f"Toggled rating: {self.sensitive}")

    @commands.hybrid_command(name="edit", description="Edit parameters")
    @commands.is_owner()
    async def edit(
        self, context: commands.Context[commands.Bot], parameters: str
    ) -> None:
        params = parameters.split(", ")
        try:
            self.parameters, self.limit = params[0], int(params[1])
        except (IndexError, ValueError):
            await context.send("Invalid parameters")
        await context.send(f"Parameters: {self.parameters}, Limit: {self.limit}")

    @commands.hybrid_command(name="miku", description="Post miku")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def miku(self, context: commands.Context[commands.Bot]) -> None:
        await context.defer()
        try:
            post = await self.fetch_post()
        except Exception:
            message = "Failed to fetch"
            self.logger.exception(message)
            await context.send(message)
            return
        if not post:
            await context.send("No illustrations found")
            return

        image_url = post.get("large_file_url")
        post_url = f"https://danbooru.donmai.us/posts/{post.get('id')}"
        artist = post.get("tag_string_artist") or "unknown"

        embed = discord.Embed(color=discord.Color.from_str("#0ad4de"))
        embed.set_author(name=artist, url=post_url)
        embed.set_image(url=image_url)
        await context.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Fun(bot))
