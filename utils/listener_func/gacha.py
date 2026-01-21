import random

import discord

from constants.config import DEFAULT_EMBED_COLOR
from constants.ocs import CHARACTERS
from utils.logs.pretty_log import pretty_log


async def gacha_pull(message: discord.Message):
    """Simulates a gacha pull and sends the result as an embed."""
    try:
        character_name, skins = random.choice(list(CHARACTERS.items()))
        # Randomly pick a skin type if available, else use 'casual'
        if skins:
            skin_type, image_url = random.choice(list(skins.items()))
        else:
            skin_type, image_url = "casual", None

        display_name = f"{skin_type.capitalize()} {character_name}"
        description = f"**Character Name:** `{display_name}`\n"
        embed = discord.Embed(
            title="Gacha", color=DEFAULT_EMBED_COLOR, description=description
        )
        if image_url:
            embed.set_image(url=image_url)
        await message.reply(embed=embed)
    except Exception as e:
        pretty_log(
            tag="error",
            message=f"Error during gacha pull for message ID {message.id}: {e}",
            include_trace=True,
        )
        await message.reply(
            "An error occurred while processing your gacha pull. Please try again later."
        )
