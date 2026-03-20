import os
import re
from collections import deque
from pathlib import Path
from typing import List

import discord
from discord.ext import commands
from discord.ext.commands import Context
from groq import AsyncGroq
from groq.types.chat import ChatCompletionMessageParam


class Chat(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.cooldown = commands.CooldownMapping.from_cooldown(
            10, 60, commands.BucketType.user
        )
        self.disabled = set()
        self.groq = AsyncGroq(api_key=os.getenv("GROQ_KEY"))
        self.memory = {}

    async def cog_load(self) -> None:
        self.mention = re.compile(rf"\s*<@!?{self.bot.user.id}>\s*")  # type: ignore
        prompt_path = Path(__file__).resolve().parent.parent / "system_prompt.md"
        self.system_prompt = prompt_path.read_text(encoding="utf-8").strip()

    @commands.hybrid_command(name="toggle", description="Toggle AI chat")
    @commands.guild_only()
    @commands.is_owner()
    async def toggle(self, context: Context) -> None:
        guild = context.guild.id  # type: ignore

        if guild in self.disabled:
            self.disabled.remove(guild)
            await context.send("AI chat enabled")
            return
        self.disabled.add(guild)
        await context.send("AI chat disabled")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if not message.guild:
            return

        if message.guild.id in self.disabled:
            return

        if message.author.bot:
            return

        if self.bot.user in message.mentions:
            bucket = self.cooldown.get_bucket(message)
            retry_after = bucket.update_rate_limit()  # type: ignore

            if retry_after:
                await message.reply(f"Wait {retry_after:.1f}s")
                return

            user_prompt = self.mention.sub("", message.clean_content).strip()

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
                        model="llama-3.3-70b-versatile",
                        max_completion_tokens=128,
                        temperature=0.8,
                    )
                    response = output.choices[0].message.content

                    if not response:
                        return

                    self.memory[data].append({"role": "user", "content": user_prompt})
                    self.memory[data].append({"role": "assistant", "content": response})
                    await message.reply(response)
                except Exception:
                    await message.channel.send("Response Failed")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Chat(bot))
