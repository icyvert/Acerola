import discord
import re
import logging

from discord.ext import commands
from discord.ext.commands import Context

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

    def embed(self, match: re.Match) -> str:
        url = match.group(0)
        domain = match.group(1).lower()
        return url.replace(domain, self.domains[domain])

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return

        if self.bot.user in message.mentions:
            context: Context = await self.bot.get_context(message)
            if context.prefix and not context.valid:
                await message.reply("what")
            return

        if isinstance(message.channel, discord.TextChannel):
            if self.urls.search(message.content):
                try:
                    if len(self.webhook_cache) > 16:
                        old_keys = list(self.webhook_cache.keys())[:4]
                        for key in old_keys:
                            self.webhook_cache.pop(key, None)
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
                except discord.NotFound:
                    self.webhook_cache.pop(message.channel.id, None)
                except Exception:
                    logger.exception("Embed failed")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Chat(bot))
