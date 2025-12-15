import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context

class Chat(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.context_menu = app_commands.ContextMenu(
            name="the what",
            callback=self.the_what,
            allowed_contexts=app_commands.AppCommandContext(guild=True, dm_channel=True, private_channel=True),
            allowed_installs=app_commands.AppInstallationType(guild=True, user=True)
        )
        self.bot.tree.add_command(self.context_menu)

    async def the_what(self, interaction: discord.Interaction, message: discord.Message) -> None:
        await interaction.response.defer(ephemeral=True)
        await message.reply("the what")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if self.bot.user in message.mentions:
            context: Context = await self.bot.get_context(message)
            if not context.valid and context.prefix:
                await message.reply("what")
        return

async def setup(bot) -> None:
    await bot.add_cog(Chat(bot))