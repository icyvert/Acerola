import logging
import os
import re
from collections import deque
from pathlib import Path
from typing import List

import discord
from discord.ext import commands
from groq import AsyncGroq
from groq.types.chat import ChatCompletionMessageParam

logger = logging.getLogger("bot.chat")


class Chat(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.domains = {
            "reddit.com": "vxreddit.com",
            "instagram.com": "instafix.ldez.top",
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
            rf"https?://(?:www\.)?({'|'.join(re.escape(d) for d in self.domains)})(?:/[\w\-./?=&%+]*)?"
        )
        self.cooldown = commands.CooldownMapping.from_cooldown(
            10, 60, commands.BucketType.user
        )
        self.groq = AsyncGroq(api_key=os.getenv("GROQ_KEY"))
        self.memory = {}
        self.mention = None
        prompt_path = Path(__file__).resolve().parent.parent / "system_prompt.md"
        self.system_prompt = prompt_path.read_text(encoding="utf-8").strip()

    def embed(self, match: re.Match) -> tuple[str, str]:
        url = match.group(0)
        domain = match.group(1)
        fixed_url = url.replace(domain, self.domains[domain], 1)
        if domain == "instagram.com":
            fixed_url = fixed_url.replace("www.", "", 1)
        return fixed_url, domain

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot or not message.guild:
            return

        match = self.urls.search(message.content)

        if match:
            fixed_url, domain = self.embed(match)
            await message.reply(
                f"[{self.sites[domain]}]({fixed_url})", mention_author=False
            )
            try:
                await message.edit(suppress=True)
            except Exception:
                pass
            return

        if self.bot.user in message.mentions:
            bucket = self.cooldown.get_bucket(message)
            retry_after = bucket.update_rate_limit()  # type: ignore

            if retry_after:
                await message.reply(f"Wait {retry_after:.1f}s")
                return

            if self.mention is None:
                self.mention = re.compile(rf"\s*<@!?{self.bot.user.id}>\s*")  # type: ignore

            user_prompt = self.mention.sub("", message.content).strip()

            if not user_prompt:
                await message.reply("what")
                return

            data = (message.channel.id, message.author.id)

            if data not in self.memory:
                self.memory[data] = deque(maxlen=16)

            async with message.channel.typing():
                try:
                    messages: List[ChatCompletionMessageParam] = [
                        {"role": "system", "content": self.system_prompt}
                    ]
                    messages.extend(self.memory[data])
                    messages.append({"role": "user", "content": user_prompt})

                    output = await self.groq.chat.completions.create(
                        messages=messages,
                        model="llama-3.1-8b-instant",
                        max_completion_tokens=128,
                        temperature=0.8,
                    )
                    response = output.choices[0].message.content

                    if not response:
                        await message.reply("no comment")
                        return

                    await message.reply(response)
                    self.memory[data].append({"role": "user", "content": user_prompt})
                    self.memory[data].append({"role": "assistant", "content": response})
                except Exception:
                    logger.exception("Response Failed")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Chat(bot))
