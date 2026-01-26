import discord
from discord import app_commands
from discord.ext import commands

from config.ocs import OCS_RARITY_MAP
from utils.cache.cache_list import ocs_cache
from utils.db.ocs_db import upsert_oc
from utils.logs.pretty_log import pretty_log
from utils.logs.send_log_embed import send_log_embed
from utils.visuals.pretty_defer import pretty_defer


async def create_oc_func(
    bot: commands.Bot,
    interaction: discord.Interaction,
    name: str,
    rarity: str,
    image_link: str,
    character_info: str = None,
):
    """Creates a new OC entry in the database."""
    # Defer the interaction to allow for processing time
    loader = await pretty_defer(
        interaction=interaction, content="Creating OC...", ephemeral=False
    )
    # Check if OC already exists in cache
    if name in ocs_cache:
        await loader.error(content=f"OC '{name}' already exists!")
        return

    # Insert OC into database
    await upsert_oc(
        bot,
        name,
        rarity,
        image_link,
        character_info,
    )
    rarity_color = OCS_RARITY_MAP.get(rarity, {}).get("color", 0xFFFFFF)
    rarity_emoji = OCS_RARITY_MAP.get(rarity, {}).get("emoji", "")
    desc = f"**Name:** {name}\n" f"**Rarity:** {rarity_emoji} {rarity}\n"
    if character_info:
        desc += f"**Info:** {character_info}\n"
    embed = discord.Embed(
        title="OC Created Successfully!",
        description=desc,
        color=rarity_color,
    )
    if image_link:
        embed.set_image(url=image_link)
    embed.set_author(
        name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url
    )
    await loader.success(embed=embed, content=f"")
    pretty_log(
        tag="info",
        message=f"OC '{name}' created by {interaction.user} with rarity '{rarity}'.",
    )

    # Send log embed to bot log channel
    await send_log_embed(
        bot=bot,
        embed=embed,
    )
