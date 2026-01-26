import discord
from discord.ext import commands

from config.ocs import OCS_RARITY_MAP
from utils.cache.cache_list import ocs_cache
from utils.db.ocs_db import remove_oc
from utils.logs.pretty_log import pretty_log
from utils.logs.send_log_embed import send_log_embed
from utils.visuals.pretty_defer import pretty_defer


async def remove_oc_func(
    bot: commands.Bot,
    interaction: discord.Interaction,
    name: str,
):
    """Removes an OC entry from the database."""

    # Defer the interaction to allow for processing time
    loader = await pretty_defer(
        interaction=interaction, content="Removing OC...", ephemeral=False
    )
    # Check if OC exists in cache
    if name not in ocs_cache:
        await loader.error(content=f"OC '{name}' does not exist!")
        return

    # Get info for embed before removal
    oc_info = ocs_cache.get(name, {})
    rarity = oc_info.get("rarity", "Unknown")
    rarity_color = OCS_RARITY_MAP.get(rarity, {}).get("color", 0xFFFFFF)
    rarity_emoji = OCS_RARITY_MAP.get(rarity, {}).get("emoji", "")
    image_link = oc_info.get("image_link", "")

    embed = discord.Embed(
        title="OC Removed Successfully!",
        description=f"**Name:** {name}\n" f"**Rarity:** {rarity_emoji} {rarity}\n",
        color=rarity_color,
    )
    if image_link:
        embed.set_image(url=image_link)
    # Remove OC from database
    await remove_oc(bot, name)
    embed.set_author(
        name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url
    )
    await loader.success(embed=embed, content="")
    pretty_log(
        tag="info",
        message=f"OC '{name}' removed by {interaction.user}.",
    )
    # Send log embed to bot log channel
    await send_log_embed(
        bot=bot,
        embed=embed,
    )
