import discord
import re

from discord.ext import commands
from discord.ext.commands import Context


class Chat(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.domains = {"reddit.com": "rxddit.com"}
        regex = "|".join([re.escape(d) for d in self.domains.keys()])
        self.urls = re.compile(rf"https://(?:www\.)?({regex})/[^\s]+")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return

        if self.bot.user in message.mentions:
            context: Context = await self.bot.get_context(message)
            if context.prefix and not context.valid:
                await message.reply("what")

        match = self.urls.search(message.content)
        if match:
            url = match.group(0)
            domain = match.group(1)

            for domain in self.domains:
                new_domain = self.domains[domain]
                new_url = url.replace(domain, new_domain)
                await message.edit(suppress=True)
                await message.channel.send(new_url)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Chat(bot))
