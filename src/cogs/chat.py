import os
import re
from collections import defaultdict, deque
from pathlib import Path
from typing import Any

import discord
from discord import app_commands
from discord.ext import commands
from groq import AsyncGroq, GroqError
from groq.types.chat import ChatCompletionMessageParam


class Chat(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.groq: AsyncGroq | None = None
        self.mention: re.Pattern[str] | None = None
        self.system_prompt = ""
        self.chats: deque[int] = deque(maxlen=32)
        self.disabled: set[int] = set()
        self.memory: defaultdict[tuple[int, int], deque[ChatCompletionMessageParam]] = (
            defaultdict(lambda: deque(maxlen=16))
        )
        self.cooldown: commands.CooldownMapping[discord.Message] = (
            commands.CooldownMapping[discord.Message].from_cooldown(
                10, 60, commands.BucketType.user
            )
        )

    async def cog_load(self) -> None:
        self.groq = AsyncGroq(api_key=os.environ["GROQ_KEY"])
        if self.bot.user:
            self.mention = re.compile(rf"\s*<@!?{self.bot.user.id}>\s*")
        prompt_path = Path(__file__).parent / "prompts" / "system_prompt.md"
        self.system_prompt = prompt_path.read_text(encoding="utf-8").strip()

    async def cog_unload(self) -> None:
        if self.groq:
            await self.groq.close()

    @commands.hybrid_command(name="toggle", description="Toggle AI chat")
    @commands.guild_only()
    @commands.is_owner()
    @app_commands.default_permissions(administrator=True)
    async def toggle(self, context: commands.Context[Any]) -> None:
        if not context.guild:
            return
        guild = context.guild.id
        if guild in self.disabled:
            self.disabled.remove(guild)
            await context.send("Enabled")
            return
        self.disabled.add(guild)
        await context.send("Disabled")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if not message.guild or message.guild.id in self.disabled:
            return
        if message.author.bot or self.groq is None:
            return

        if self.mention is None:
            if not self.bot.user:
                return
            self.mention = re.compile(rf"\s*<@!?{self.bot.user.id}>\s*")

        mention = self.mention.search(message.content)
        reply = message.reference and message.reference.message_id in self.chats
        if not (mention or reply):
            return

        try:
            bucket = self.cooldown.get_bucket(message)
            if bucket:
                retry_after = bucket.update_rate_limit()
                if retry_after:
                    await message.reply(f"Wait {retry_after:.1f}s", delete_after=3.0)
                    return

            user_prompt = self.mention.sub(" ", message.content).strip()
            if not user_prompt:
                await message.reply("what")
                return

            data = (message.channel.id, message.author.id)
            async with message.channel.typing():
                messages: list[ChatCompletionMessageParam] = [
                    {"role": "system", "content": self.system_prompt},
                    *self.memory[data],
                    {"role": "user", "content": user_prompt},
                ]
                output = await self.groq.chat.completions.create(
                    messages=messages,
                    model="openai/gpt-oss-120b",
                    max_completion_tokens=128,
                    temperature=0.8,
                )

                response = output.choices[0].message.content
                if not response:
                    return
                msg = await message.reply(response)

                self.memory[data].append({"role": "user", "content": user_prompt})
                self.memory[data].append({"role": "assistant", "content": response})
                self.chats.append(msg.id)
        except (GroqError, discord.DiscordException):
            try:
                await message.channel.send("Response failed.")
            except discord.DiscordException:
                pass


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Chat(bot))
