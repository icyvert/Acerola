import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context

class Chat(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
    
    @app_commands.context_menu(name="the what")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def the_what(self, interaction: discord.Interaction, message: discord.Message) -> None:
        await interaction.response.send_message("the what")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if self.bot.user in message.mentions:
            context: Context = await self.bot.get_context(message)
            if not context.valid and context.prefix:
                await message.reply("what")

async def setup(bot) -> None:
    await bot.add_cog(Chat(bot))