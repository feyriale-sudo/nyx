import discord
from discord.ext import commands

from utils.listener_func.gacha import gacha_pull


class MessageCreateListener(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):

        # Ignore messages from the bot itself and other bots
        if message.author.bot:
            return

        # Simple command check
        if message.content.lower() == ".gacha":
            # Call your gacha function here
            await gacha_pull(message)


async def setup(bot: commands.Bot):
    await bot.add_cog(MessageCreateListener(bot))
