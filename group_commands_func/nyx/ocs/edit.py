import discord
from discord import app_commands
from discord.ext import commands

from config.ocs import OCS_RARITY_MAP
from utils.cache.cache_list import ocs_cache
from utils.db.ocs_db import edit_oc
from utils.logs.pretty_log import pretty_log
from utils.logs.send_log_embed import send_log_embed
from utils.visuals.pretty_defer import pretty_defer

async def edit_oc_func(
    bot: commands.Bot,
    interaction: discord.Interaction,
    name: str,
    new_rarity: str | None = None,
    new_image_link: str | None = None,
    new_character_info: str | None = None,
):
    """Edits an existing OC entry in the database."""
    # Defer the interaction to allow for processing time
    loader = await pretty_defer(
        interaction=interaction, content="Editing OC...", ephemeral=False
    )
    # Check if OC exists in cache
    if name not in ocs_cache:
        await loader.error(content=f"OC '{name}' does not exist!")
        return
    # Check if there is anything to update
    if not any([new_rarity, new_image_link, new_character_info]):
        await loader.error(content="No new information provided to update!")
        return
    # Fetch old info for embed
    old_oc_info = ocs_cache.get(name, {})
    old_rarity = old_oc_info.get("rarity", "Unknown")
    old_rarity_emoji = OCS_RARITY_MAP.get(old_rarity, {}).get("emoji", "")
    old_image_link = old_oc_info.get("image_link", "")
    old_character_info = old_oc_info.get("character_info", "")
    # Edit OC in database
    await edit_oc(
        bot,
        name,
        new_rarity,
        new_image_link,
        new_character_info,
    )
    # Prepare embed with old and new info
    embed = discord.Embed(
        title="OC Edited Successfully!",
        description=f"**Name:** {name}\n",
        color=OCS_RARITY_MAP.get(new_rarity or old_rarity, {}).get("color", 0xFFFFFF),
    )
    if new_rarity:
        new_rarity_emoji = OCS_RARITY_MAP.get(new_rarity, {}).get("emoji", "")
        embed.add_field(
            name="Rarity Updated",
            value=f"{old_rarity_emoji} {old_rarity} → {new_rarity_emoji} {new_rarity}",
            inline=False,
        )
    if new_character_info:
        embed.add_field(
            name="Character Info Updated",
            value=f"{old_character_info} → \n{new_character_info}",
            inline=False,
        )
    if new_image_link:
        embed.add_field(
            name="Image Link Updated",
            value=f"[Old Image]({old_image_link}) → [New Image]({new_image_link})",
            inline=False,
        )
    embed.set_image(url=new_image_link or old_image_link)
    embed.set_author(
        name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url
    )
    await loader.success(embed=embed, content="")
    pretty_log(
        tag="info",
        message=f"OC '{name}' edited by {interaction.user}.",
    )

    # Send log embed to bot log channel
    await send_log_embed(
        bot=bot,
        embed=embed,
    )