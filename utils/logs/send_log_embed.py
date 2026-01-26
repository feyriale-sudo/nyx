import discord

from config.setup import BOT_LOG_CHANNEL_ID
from utils.logs.pretty_log import pretty_log

async def send_log_embed(
    bot: discord.Client, embed: discord.Embed = None, content: str = None
):
    """Sends a log message to the bot log channel."""
    try:
        log_channel = bot.get_channel(BOT_LOG_CHANNEL_ID)
        if not log_channel:
            pretty_log(tag="error", message="Log channel not found.")
            return

        if not embed and not content:
            pretty_log(
                tag="error", message="No content or embed provided for log message."
            )
            return
        await log_channel.send(content=content, embed=embed)

    except Exception as e:
        pretty_log(
            tag="error",
            message=f"Error sending log message: {e}",
        )
