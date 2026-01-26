import discord

from utils.db.ocs_db import fetch_all_ocs, fetch_all_ocs_by_rarity
from utils.logs.pretty_log import pretty_log

from .cache_list import (
    common_ocs_cache,
    epic_ocs_cache,
    legendary_ocs_cache,
    ocs_cache,
    rare_ocs_cache,
)


def clear_all_ocs_cache():
    """Clears all OC caches."""

    import utils.cache.cache_list as cache_list

    cache_list.ocs_cache = []
    cache_list.common_ocs_cache = []
    cache_list.rare_ocs_cache = []
    cache_list.epic_ocs_cache = []
    cache_list.legendary_ocs_cache = []
    pretty_log(tag="info", message="Cleared all OC caches.")


async def load_ocs_cache(bot: discord.Client):
    """Loads all OCs from the database into the cache."""
    # Clear existing caches first
    clear_all_ocs_cache()

    try:

        import utils.cache.cache_list as cache_list

        # Always wrap each OC dict from DB in the expected nested format
        def wrap_oc_entry(oc):
            normalized_rarity = str(oc["rarity"]).strip().title()
            return {
                oc["name"]: {
                    "rarity": normalized_rarity,
                    "character_info": oc["character_info"],
                    "image_link": oc["image_link"],
                }
            }

        cache_list.ocs_cache = [wrap_oc_entry(oc) for oc in await fetch_all_ocs(bot)]
        pretty_log(
            tag="info", message=f"Loaded {len(cache_list.ocs_cache)} OCs into cache."
        )

        cache_list.common_ocs_cache = [
            wrap_oc_entry(oc) for oc in await fetch_all_ocs_by_rarity(bot, "Common")
        ]
        pretty_log(
            tag="info",
            message=f"Loaded {len(cache_list.common_ocs_cache)} Common OCs into cache.",
        )

        cache_list.rare_ocs_cache = [
            wrap_oc_entry(oc) for oc in await fetch_all_ocs_by_rarity(bot, "Rare")
        ]
        pretty_log(
            tag="info",
            message=f"Loaded {len(cache_list.rare_ocs_cache)} Rare OCs into cache.",
        )

        cache_list.epic_ocs_cache = [
            wrap_oc_entry(oc) for oc in await fetch_all_ocs_by_rarity(bot, "Epic")
        ]
        pretty_log(
            tag="info",
            message=f"Loaded {len(cache_list.epic_ocs_cache)} Epic OCs into cache.",
        )

        cache_list.legendary_ocs_cache = [
            wrap_oc_entry(oc) for oc in await fetch_all_ocs_by_rarity(bot, "Legendary")
        ]
        pretty_log(
            tag="info",
            message=f"Loaded {len(cache_list.legendary_ocs_cache)} Legendary OCs into cache.",
        )

    except Exception as e:
        pretty_log(
            tag="error",
            message=f"Error loading OCs into cache: {e}",
            include_trace=True,
        )


def get_total_count_by_rarity(rarity: str) -> int:
    """Returns the total count of OCs in the cache for a given rarity."""
    import utils.cache.cache_list as cache_list

    rarity_cache_map = {
        "Common": cache_list.common_ocs_cache,
        "Rare": cache_list.rare_ocs_cache,
        "Epic": cache_list.epic_ocs_cache,
        "Legendary": cache_list.legendary_ocs_cache,
    }
    cache = rarity_cache_map.get(rarity)
    if cache is not None:
        return len(cache)
    return 0


def get_total_count_all_ocs() -> int:
    """Returns the total count of all OCs in the main cache."""
    import utils.cache.cache_list as cache_list

    return len(cache_list.ocs_cache)


def get_overall_total_count() -> int:
    """Returns the overall total count of OCs across all rarity caches as an integer."""
    import utils.cache.cache_list as cache_list

    common_count = len(cache_list.common_ocs_cache)
    rare_count = len(cache_list.rare_ocs_cache)
    epic_count = len(cache_list.epic_ocs_cache)
    legendary_count = len(cache_list.legendary_ocs_cache)
    total_count = common_count + rare_count + epic_count + legendary_count
    return total_count


def get_overall_count_str() -> str:
    """Returns a string with the count of OCs by rarity and total."""
    import utils.cache.cache_list as cache_list

    common_count = len(cache_list.common_ocs_cache)
    rare_count = len(cache_list.rare_ocs_cache)
    epic_count = len(cache_list.epic_ocs_cache)
    legendary_count = len(cache_list.legendary_ocs_cache)
    total_count = common_count + rare_count + epic_count + legendary_count
    count_str = f"Common: {common_count} | Rare: {rare_count} | Epic: {epic_count} | Legendary: {legendary_count} | Total: {total_count}"
    return count_str


async def edit_oc_cache(bot, name: str, character_info: str, image_link: str):
    """Edits an existing OC in the cache."""
    import utils.cache.cache_list as cache_list

    def edit_in_cache(cache: list[dict[str, dict[str, str]]], name: str):
        for i, oc in enumerate(cache):
            if name in oc:
                cache[i] = {
                    name: {
                        "character_info": character_info,
                        "image_link": image_link,
                    }
                }
                return

    edit_in_cache(cache_list.ocs_cache, name)
    edit_in_cache(cache_list.common_ocs_cache, name)
    edit_in_cache(cache_list.rare_ocs_cache, name)
    edit_in_cache(cache_list.epic_ocs_cache, name)
    edit_in_cache(cache_list.legendary_ocs_cache, name)
    pretty_log(tag="info", message=f"Edited OC '{name}' in all caches.")
    # Reload caches to ensure consistency
    await load_ocs_cache(bot)


def list_all_oc_names() -> list[str]:
    """Returns a list of all OC names in the main cache."""
    import utils.cache.cache_list as cache_list

    return [list(oc.keys())[0] for oc in cache_list.ocs_cache]


def upsert_oc_cache(name: str, rarity: str, character_info: str, image_link: str):
    """Upserts an OC into the appropriate cache based on its rarity."""
    import utils.cache.cache_list as cache_list

    normalized_rarity = str(rarity).strip().title()
    oc_entry = {
        name: {
            "character_info": character_info,
            "image_link": image_link,
            "rarity": normalized_rarity,
        }
    }
    # Upsert into the main ocs_cache
    for i, oc in enumerate(cache_list.ocs_cache):
        if name in oc:
            cache_list.ocs_cache[i] = oc_entry
            break
    else:
        cache_list.ocs_cache.append(oc_entry)
    # Upsert into the specific rarity cache
    rarity_cache_map = {
        "Common": cache_list.common_ocs_cache,
        "Rare": cache_list.rare_ocs_cache,
        "Epic": cache_list.epic_ocs_cache,
        "Legendary": cache_list.legendary_ocs_cache,
    }
    rarity_cache = rarity_cache_map.get(normalized_rarity)
    if rarity_cache is not None:
        for i, oc in enumerate(rarity_cache):
            if name in oc:
                rarity_cache[i] = oc_entry
                break
        else:
            rarity_cache.append(oc_entry)
    pretty_log(
        tag="info",
        message=f"Upserted OC '{name}' with rarity '{normalized_rarity}' into cache.",
    )


def remove_oc_from_cache(name: str):
    """Removes an OC from all caches."""
    import utils.cache.cache_list as cache_list

    def remove_from_cache(cache: list[dict[str, dict[str, str]]], name: str):
        for i, oc in enumerate(cache):
            if name in oc:
                del cache[i]
                return

    remove_from_cache(cache_list.ocs_cache, name)
    remove_from_cache(cache_list.common_ocs_cache, name)
    remove_from_cache(cache_list.rare_ocs_cache, name)
    remove_from_cache(cache_list.epic_ocs_cache, name)
    remove_from_cache(cache_list.legendary_ocs_cache, name)
    pretty_log(tag="info", message=f"Removed OC '{name}' from all caches.")
