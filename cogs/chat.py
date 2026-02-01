import os
import discord
import re
import logging

from discord.ext import commands
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
            rf"https?://(?:www\.)?({'|'.join(re.escape(d) for d in self.domains)})"
            r"(?:/[^\s<>]*)?",
            re.IGNORECASE,
        )
        self.webhook_cache = {}
        self.groq = AsyncGroq(api_key=os.getenv("GROQ_KEY"))
        self.system_prompt = (
            "You are a discord chatbot called Acerola. "
            "Keep responses ideally under 128 characters."
        )
        self.mention = None

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
                    if len(self.webhook_cache) > 16:
                        del self.webhook_cache[next(iter(self.webhook_cache))]
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

            async with message.channel.typing():
                try:
                    response = await self.groq.chat.completions.create(
                        messages=[
                            {"role": "system", "content": self.system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        model="llama-3.1-8b-instant",
                        max_tokens=64,
                    )
                    await message.reply(response.choices[0].message.content)
                except Exception:
                    logger.exception("Response Failed")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Chat(bot))
