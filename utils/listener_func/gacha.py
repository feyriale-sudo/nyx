import random

import discord

from config.ocs import OCS_RARITY_MAP, determine_is_skin
from utils.cache.cache_list import (
    common_ocs_cache,
    epic_ocs_cache,
    legendary_ocs_cache,
    ocs_cache,
    rare_ocs_cache,
    user_oc_inv_cache,
)
from utils.db.user_oc_inv import increment_oc_owned, upsert_user_oc_inv
from utils.logs.debug_log import debug_log, enable_debug
from utils.logs.pretty_log import pretty_log

#enable_debug(f"{__name__}.gacha_pull")
RARITY_CACHE_MAP = {
    "Common": common_ocs_cache,
    "Rare": rare_ocs_cache,
    "Epic": epic_ocs_cache,
    "Legendary": legendary_ocs_cache,
}


def get_random_rarity():
    rarities = list(OCS_RARITY_MAP.keys())
    rates = [OCS_RARITY_MAP[r]["rate"] for r in rarities]
    return random.choices(rarities, weights=rates, k=1)[0]


async def pick_random_oc_by_rarity(
    bot: discord.Client, rarity: str
) -> dict[str, dict[str, str]] | None:
    cache = RARITY_CACHE_MAP.get(rarity)
    if not cache:
        # Reload caches if not found
        from utils.cache.ocs_cache import load_ocs_cache

        await load_ocs_cache(bot)
        # Re-import cache variables to get updated references
        from utils.cache.cache_list import (
            common_ocs_cache,
            epic_ocs_cache,
            legendary_ocs_cache,
            rare_ocs_cache,
        )

        cache = {
            "Common": common_ocs_cache,
            "Rare": rare_ocs_cache,
            "Epic": epic_ocs_cache,
            "Legendary": legendary_ocs_cache,
        }.get(rarity)
    if not cache:
        return None
    return random.choice(cache) if cache else None


def get_oc_from_user_inv_cache(user_id: int, card_name: str) -> dict[str, str] | None:
    user_inv = user_oc_inv_cache.get(user_id, [])
    return next((item for item in user_inv if item["card_name"] == card_name), None)


async def gacha_pull(bot: discord.Client, message: discord.Message):
    """Simulates a gacha pull and sends the result as an embed."""
    try:
        rarity = get_random_rarity()
        oc_entry = await pick_random_oc_by_rarity(bot, rarity)
        if not oc_entry:
            debug_log(
                f"No OC found for rarity {rarity} during gacha pull",
            )
            await message.reply(
                "No OCs available for the selected rarity. Please try again later."
            )
            return
        character_name = list(oc_entry.keys())[0]
        info = oc_entry[character_name]
        # Debug: log the structure of oc_entry and info
        debug_log(f"oc_entry: {oc_entry}")
        debug_log(f"character_name: {character_name}")
        debug_log(f"info: {info} (type: {type(info)})")
        character_info = info.get("character_info", None)
        image_url = info["image_link"]

        display_character_name = character_name.title()
        rarity_emoji = OCS_RARITY_MAP[rarity]["emoji"]
        rarity_color = OCS_RARITY_MAP[rarity]["color"]

        # Check if user already owns the OC
        already_owned = False
        footer_text = None
        is_skin = determine_is_skin(character_name)
        user = message.author
        user_id = user.id
        owned_oc_info = get_oc_from_user_inv_cache(user_id, character_name)
        if owned_oc_info:
            already_owned = True
            await increment_oc_owned(bot, user_id, character_name)
        else:
            await upsert_user_oc_inv(
                bot=bot,
                user_id=user_id,
                user_name=user.name,
                card_name=character_name,
                rarity=rarity,
                character_info=character_info,
                image_link=image_url,
                owned=1,
            )

        # Determine footer text
        if not already_owned:
            if is_skin:
                footer_text = "New skin unlocked!"
            else:
                footer_text = "New Character unlocked!"

        description = f"{rarity_emoji} `{display_character_name}` has been added to your collection!\n"
        embed = discord.Embed(
            title="You have been blessed!",
            color=rarity_color,
            description=description,
        )
        if image_url:
            embed.set_image(url=image_url)

        if footer_text:
            embed.set_footer(text=footer_text)
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
