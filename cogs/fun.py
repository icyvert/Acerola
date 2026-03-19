import time

import aiohttp
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context


class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.cache = {}
        self.session = None
        self.stats = {}
        self.sub = ""

    @commands.hybrid_command(name="subreddit", description="Set subreddit")
    @app_commands.describe(sub="Subreddit name")
    @commands.is_owner()
    async def subreddit(self, context: Context, sub: str) -> None:
        self.sub = sub.lower()
        self.stats[self.sub] = 0
        if self.session is None:
            self.session = aiohttp.ClientSession()
        await context.send("Subreddit set")

    @commands.hybrid_command(name="reddit", description="Reddit posts")
    @commands.guild_only()
    async def reddit(self, context: Context) -> None:
        subreddit = self.sub

        if subreddit == "":
            await context.send("Subreddit not set", ephemeral=True)
            return

        posts = []

        if subreddit in self.cache and (time.time() - self.cache[subreddit][0] < 600):
            posts = self.cache[subreddit][1]
        else:
            url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=32"
            headers = {"User-Agent": "Discord:PersonalBot:v1 (by /u/Dreamlinar)"}

            async with self.session.get(url, headers=headers) as response:  # type: ignore
                if response.status != 200:
                    await context.send("Failed to fetch posts", ephemeral=True)
                    return

                data = await response.json()
                children = data.get("data", {}).get("children", [])
                posts = [p["data"] for p in children if not p["data"].get("stickied")]

                if not posts:
                    await context.send("No posts found")
                    return

                self.cache[subreddit] = (time.time(), posts)

        current = self.stats[subreddit]

        if current >= len(posts):
            current = 0

        permalink = posts[current].get("permalink")
        full_link = f"https://www.vxreddit.com{permalink}"
        self.stats[subreddit] = current + 1

        await context.send(f"[r/{subreddit}]({full_link})")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Fun(bot))
