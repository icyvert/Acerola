import os
import discord
import re
import logging

from discord.ext import commands
from pathlib import Path
from collections import deque
from groq import AsyncGroq

logger = logging.getLogger("bot.chat")


class Chat(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.domains = {
            "reddit.com": "vxreddit.com",
            "instagram.com": "vxinstagram.com",
            "x.com": "fixupx.com",
            "twitter.com": "fxtwitter.com",
        }
        self.urls = re.compile(
            rf"https?://(?:www\.)?({'|'.join(re.escape(d) for d in self.domains)})(?:/[\w\-./?=&%+]*)?",
            re.IGNORECASE,
        )
        self.webhook_cache = {}
        self.groq = AsyncGroq(api_key=os.getenv("GROQ_KEY"))
        prompt_path = Path(__file__).resolve().parent.parent / "system_prompt.md"
        self.system_prompt = prompt_path.read_text(encoding="utf-8").strip()
        self.mention = None
        self.memory = {}

    def embed(self, match: re.Match) -> str:
        url = match.group(0)
        domain = match.group(1).lower()
        return url.replace(domain, self.domains[domain])

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return

        if isinstance(message.channel, discord.TextChannel):
            if self.urls.search(message.content):
                try:
                    if message.channel.id in self.webhook_cache:
                        webhook = self.webhook_cache[message.channel.id]
                    else:
                        webhooks = await message.channel.webhooks()
                        webhook = discord.utils.get(webhooks, name="Acerola")
                        if webhook is None:
                            webhook = await message.channel.create_webhook(
                                name="Acerola"
                            )
                        self.webhook_cache[message.channel.id] = webhook
                    if len(self.webhook_cache) > 16:
                        del self.webhook_cache[next(iter(self.webhook_cache))]
                except Exception:
                    logger.exception("Webhook failed")
                    return

                content = self.urls.sub(self.embed, message.content)

                try:
                    await webhook.send(
                        content=content,
                        username=message.author.display_name,
                        avatar_url=message.author.display_avatar.url,
                        allowed_mentions=discord.AllowedMentions(
                            users=True, roles=False, everyone=False
                        ),
                    )
                    await message.delete()
                    return
                except discord.NotFound:
                    self.webhook_cache.pop(message.channel.id, None)
                except Exception:
                    logger.exception("Embed failed")

        if self.bot.user in message.mentions:
            if self.mention is None:
                self.mention = re.compile(rf"\s*<@!?{self.bot.user.id}>\s*")

            user_prompt = self.mention.sub("", message.content).strip()

            if not user_prompt:
                await message.reply("what")
                return

            if message.channel.id not in self.memory:
                self.memory[message.channel.id] = deque(maxlen=12)

            async with message.channel.typing():
                try:
                    messages = [{"role": "system", "content": self.system_prompt}]
                    messages.extend(self.memory[message.channel.id])
                    messages.append({"role": "user", "content": user_prompt})
                    output = await self.groq.chat.completions.create(
                        messages=messages,
                        model="llama-3.1-8b-instant",
                        max_completion_tokens=64,
                        temperature=0.8,
                    )
                    response = output.choices[0].message.content
                    await message.reply(response)
                    self.memory[message.channel.id].append(
                        {"role": "user", "content": user_prompt}
                    )
                    self.memory[message.channel.id].append(
                        {"role": "assistant", "content": response}
                    )
                except Exception:
                    logger.exception("Response Failed")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Chat(bot))
