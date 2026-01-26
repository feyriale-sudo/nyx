import discord

from utils.db.user_oc_inv import fetch_all_user_oc_invs
from utils.logs.pretty_log import pretty_log

from .cache_list import user_oc_inv_cache


async def load_all_user_oc_inv_cache(bot: discord.Client):
    """Loads all user OC inventories from the database into the cache."""
    # Clear existing cache first
    user_oc_inv_cache.clear()
    try:
        user_invs = await fetch_all_user_oc_invs(bot)
        user_oc_inv_cache.update(user_invs)
        pretty_log(
            tag="info",
            message=f"Loaded OC inventories for {len(user_oc_inv_cache)} users into cache.",
        )
    except Exception as e:
        pretty_log(
            tag="error",
            message=f"Error loading user OC inventories into cache: {e}",
        )
    return user_oc_inv_cache


def get_user_oc_inv_cache() -> dict[int, list[dict[str, str]]]:
    """Returns the entire user OC inventory cache."""
    return user_oc_inv_cache


def list_oc_names_in_user_inv_cache(user_id: int) -> list[str]:
    """Lists all OC card names in a user's inventory from the cache."""
    oc_names = []
    try:
        user_inv = user_oc_inv_cache.get(user_id, [])
        for entry in user_inv:
            oc_names.append(entry.get("card_name", ""))
    except Exception as e:
        pretty_log(
            tag="error",
            message=f"Error listing OC names from cache for user '{user_id}': {e}",
        )
    return oc_names


def total_cards_owned_cache(user_id: int) -> int:
    """Calculates the total number of OC cards owned by a user from the cache."""
    total_owned = 0
    try:
        user_inv = user_oc_inv_cache.get(user_id, [])
        for entry in user_inv:
            total_owned += entry.get("owned", 0)
    except Exception as e:
        pretty_log(
            tag="error",
            message=f"Error calculating total cards owned from cache for user '{user_id}': {e}",
        )
    return total_owned


def total_unique_cards_owned_cache(user_id: int) -> int:
    """Calculates the total number of unique OC cards owned by a user from the cache."""
    unique_count = 0
    try:
        user_inv = user_oc_inv_cache.get(user_id, [])
        for entry in user_inv:
            if entry.get("owned", 0) > 0:
                unique_count += 1
    except Exception as e:
        pretty_log(
            tag="error",
            message=f"Error calculating total unique cards owned from cache for user '{user_id}': {e}",
        )
    return unique_count


def total_owned_cards_by_rarity_cache(user_id: int, rarity: str) -> int:
    """Calculates the total number of OC cards owned by a user of a specific rarity from the cache."""
    total_owned = 0
    try:
        user_inv = user_oc_inv_cache.get(user_id, [])
        for entry in user_inv:
            if entry.get("rarity") == rarity:
                total_owned += entry.get("owned", 0)
    except Exception as e:
        pretty_log(
            tag="error",
            message=f"Error calculating total owned cards by rarity from cache for user '{user_id}', rarity '{rarity}': {e}",
        )
    return total_owned


def total_unique_cards_by_rarity_cache(user_id: int, rarity: str) -> int:
    """Calculates the total number of unique OC cards owned by a user of a specific rarity from the cache."""
    unique_count = 0
    try:
        user_inv = user_oc_inv_cache.get(user_id, [])
        for entry in user_inv:
            if entry.get("rarity") == rarity and entry.get("owned", 0) > 0:
                unique_count += 1
    except Exception as e:
        pretty_log(
            tag="error",
            message=f"Error calculating total unique cards by rarity from cache for user '{user_id}', rarity '{rarity}': {e}",
        )
    return unique_count


def upsert_user_oc_inv_cache(
    user_id: int,
    user_name: str,
    card_name: str,
    rarity: str,
    character_info: str,
    image_link: str,
    owned: int,
):
    """Upserts a user's OC inventory entry into the cache."""
    try:
        user_inv = user_oc_inv_cache.get(user_id, [])
        # Check if the entry already exists
        for entry in user_inv:
            if entry["card_name"] == card_name:
                # Update existing entry
                entry["user_name"] = user_name
                entry["rarity"] = rarity
                entry["character_info"] = character_info
                entry["image_link"] = image_link
                entry["owned"] = owned
                pretty_log(
                    tag="info",
                    message=f"Updated OC '{card_name}' for user ID '{user_id}' in cache.",
                )
                return
        # If not found, add new entry
        new_entry = {
            "user_name": user_name,
            "card_name": card_name,
            "rarity": rarity,
            "character_info": character_info,
            "image_link": image_link,
            "owned": owned,
        }
        user_inv.append(new_entry)
        user_oc_inv_cache[user_id] = user_inv
        pretty_log(
            tag="info",
            message=f"Added new OC '{card_name}' for user ID '{user_id}' to cache.",
        )
    except Exception as e:
        pretty_log(
            tag="error",
            message=f"Error upserting user OC inventory in cache for user '{user_id}', card '{card_name}': {e}",
        )


def fetch_user_oc_inv_cache(user_id: int) -> list[dict[str, str]]:
    """Fetches a user's OC inventory from the cache."""
    return user_oc_inv_cache.get(user_id, [])


def increment_oc_owned_cache(user_id: int, card_name: str):
    """Increments the 'owned' count for a specific OC in a user's inventory cache."""
    try:
        user_inv = user_oc_inv_cache.get(user_id, [])
        for entry in user_inv:
            if entry["card_name"] == card_name:
                entry["owned"] += 1
                pretty_log(
                    tag="info",
                    message=f"Incremented 'owned' count for OC '{card_name}' for user ID '{user_id}' in cache.",
                )
                break
    except Exception as e:
        pretty_log(
            tag="error",
            message=f"Error incrementing 'owned' count in cache for user '{user_id}', card '{card_name}': {e}",
        )


def decrement_oc_owned_cache(user_id: int, card_name: str):
    """Decrements the 'owned' count for a specific OC in a user's inventory cache."""
    try:
        user_inv = user_oc_inv_cache.get(user_id, [])
        for entry in user_inv:
            if entry["card_name"] == card_name:
                if entry["owned"] > 0:
                    entry["owned"] -= 1
                    pretty_log(
                        tag="info",
                        message=f"Decremented 'owned' count for OC '{card_name}' for user ID '{user_id}' in cache.",
                    )
                break
    except Exception as e:
        pretty_log(
            tag="error",
            message=f"Error decrementing 'owned' count in cache for user '{user_id}', card '{card_name}': {e}",
        )


def update_oc_owned_cache(
    user_id: int,
    card_name: str,
    new_owned: int,
):
    """Updates the 'owned' count for a specific OC in a user's inventory cache."""
    try:
        user_inv = user_oc_inv_cache.get(user_id, [])
        for entry in user_inv:
            if entry["card_name"] == card_name:
                entry["owned"] = new_owned
                pretty_log(
                    tag="info",
                    message=f"Updated 'owned' count for OC '{card_name}' for user ID '{user_id}' to {new_owned} in cache.",
                )
                break
    except Exception as e:
        pretty_log(
            tag="error",
            message=f"Error updating 'owned' count in cache for user '{user_id}', card '{card_name}': {e}",
        )


def delete_user_inv_cache(user_id: int):
    """Deletes a user's OC inventory from the cache."""
    try:
        if user_id in user_oc_inv_cache:
            del user_oc_inv_cache[user_id]
            pretty_log(
                tag="info",
                message=f"Deleted OC inventory for user ID '{user_id}' from cache.",
            )
    except Exception as e:
        pretty_log(
            tag="error",
            message=f"Error deleting user OC inventory cache for user '{user_id}': {e}",
        )


def fetch_all_rarity_oc_invs_cache(user_id: int, rarity: str) -> list[dict[str, str]]:
    """Fetches all OC inventory entries of a specific rarity for a user from the cache."""
    result = []
    try:
        user_inv = user_oc_inv_cache.get(user_id, [])
        for entry in user_inv:
            if entry.get("rarity") == rarity:
                result.append(entry)
    except Exception as e:
        pretty_log(
            tag="error",
            message=f"Error fetching OC inventory by rarity from cache for user '{user_id}', rarity '{rarity}': {e}",
        )
    return result
