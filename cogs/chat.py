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
        regex = "|".join([re.escape(d) for d in self.domains.keys()])
        self.urls = re.compile(rf"https://(?:www\.)?({regex})/\S+")
        self.webhook_cache = {}

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return

        match = self.urls.search(message.content)
        if match:
            try:
                if message.channel.id in self.webhook_cache:
                    webhook = self.webhook_cache[message.channel.id]
                else:
                    webhooks = await message.channel.webhooks()
                    webhook = discord.utils.get(webhooks, name="Acerola")
                    if webhook is None:
                        webhook = await message.channel.create_webhook(name="Acerola")
                    self.webhook_cache[message.channel.id] = webhook
            except Exception:
                logger.exception("Webhook failed")
                return

            url = match.group(0)
            domain = match.group(1)
            new_url = url.replace(domain, self.domains[domain])

            try:
                await webhook.send(
                    content=new_url,
                    username=message.author.display_name,
                    avatar_url=message.author.display_avatar.url,
                )
                await message.delete()
            except discord.NotFound:
                self.webhook_cache.pop(message.channel.id, None)
            except Exception:
                logger.exception("Embed failed")
            return

        if self.bot.user in message.mentions:
            context: Context = await self.bot.get_context(message)
            if context.prefix and not context.valid:
                await message.reply("what")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Chat(bot))
