import discord

from utils.logs.pretty_log import pretty_log

# SQL SCRIPT
"""CREATE TABLE ocs (
    name TEXT PRIMARY KEY,
    rarity TEXT NOT NULL,
    character_info TEXT,
    image_link TEXT NOT NULL
);"""


async def oc_name_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[discord.app_commands.Choice[str]]:
    """Provides autocomplete suggestions for OC names."""
    from utils.cache.ocs_cache import list_all_oc_names

    all_oc_names = list_all_oc_names()
    suggestions = [
        discord.app_commands.Choice(name=oc_name, value=oc_name)
        for oc_name in all_oc_names
        if current.lower() in oc_name.lower()
    ]
    return suggestions[:25]  # Limit to top 25 suggestions


async def upsert_oc(
    bot: discord.Client,
    name: str,
    rarity: str,
    image_link: str,
    character_info: str | None,
):
    """Inserts or updates an OC entry in the database."""
    try:
        async with bot.pg_pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO ocs (name, rarity, character_info, image_link)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (name) DO UPDATE
                SET rarity = EXCLUDED.rarity,
                    character_info = EXCLUDED.character_info,
                    image_link = EXCLUDED.image_link;
                """,
                name,
                rarity,
                character_info,
                image_link,
            )
        pretty_log(
            tag="info",
            message=f"Upserted OC '{name}' with rarity '{rarity}' into database.",
        )
        # Upsert into cache as well
        from utils.cache.ocs_cache import upsert_oc_cache

        upsert_oc_cache(name, rarity, character_info, image_link)
    except Exception as e:
        pretty_log(
            tag="error",
            message=f"Error upserting OC '{name}': {e}",
        )


async def remove_oc(bot: discord.Client, name: str):
    """Removes an OC entry from the database."""
    try:
        async with bot.pg_pool.acquire() as conn:
            await conn.execute(
                """
                DELETE FROM ocs WHERE name = $1;
                """,
                name,
            )
        pretty_log(
            tag="info",
            message=f"Removed OC '{name}' from database.",
        )
        # Remove from cache as well
        from utils.cache.ocs_cache import remove_oc_from_cache

        remove_oc_from_cache(name)

    except Exception as e:
        pretty_log(
            tag="error",
            message=f"Error removing OC '{name}': {e}",
        )


async def fetch_oc(bot: discord.Client, name: str) -> dict | None:
    """Fetches an OC entry from the database."""
    try:
        async with bot.pg_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT name, rarity, character_info, image_link
                FROM ocs WHERE name = $1;
                """,
                name,
            )
            if row:
                return {
                    "name": row["name"],
                    "rarity": row["rarity"],
                    "character_info": row["character_info"],
                    "image_link": row["image_link"],
                }
            return None
    except Exception as e:
        pretty_log(
            tag="error",
            message=f"Error fetching OC '{name}': {e}",
        )
        return None


async def fetch_all_ocs(bot: discord.Client) -> list[dict]:
    """Fetches all OC entries from the database."""
    try:
        async with bot.pg_pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT name, rarity, character_info, image_link
                FROM ocs;
                """
            )
            return [
                {
                    "name": row["name"],
                    "rarity": row["rarity"],
                    "character_info": row["character_info"],
                    "image_link": row["image_link"],
                }
                for row in rows
            ]
    except Exception as e:
        pretty_log(
            tag="error",
            message=f"Error fetching all OCs: {e}",
        )
        return []


async def fetch_all_ocs_by_rarity(bot: discord.Client, rarity: str) -> list[dict]:
    """Fetches all OC entries of a specific rarity from the database."""
    try:
        async with bot.pg_pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT name, rarity, character_info, image_link
                FROM ocs WHERE rarity = $1;
                """,
                rarity,
            )
            return [
                {
                    "name": row["name"],
                    "rarity": row["rarity"],
                    "character_info": row["character_info"],
                    "image_link": row["image_link"],
                }
                for row in rows
            ]
    except Exception as e:
        pretty_log(
            tag="error",
            message=f"Error fetching OCs of rarity '{rarity}': {e}",
        )
        return []


async def edit_oc(
    bot: discord.Client,
    name: str,
    new_rarity: str | None = None,
    new_image_link: str | None = None,
    new_character_info: str | None = None,
):
    """Edits an existing OC entry in the database."""
    try:
        async with bot.pg_pool.acquire() as conn:
            # Fetch current values
            current_oc = await fetch_oc(bot, name)
            if not current_oc:
                pretty_log(
                    tag="error",
                    message=f"OC '{name}' not found for editing.",
                )
                return

            # Use new values if provided, else keep current
            rarity = new_rarity if new_rarity is not None else current_oc["rarity"]
            image_link = (
                new_image_link
                if new_image_link is not None
                else current_oc["image_link"]
            )
            character_info = (
                new_character_info
                if new_character_info is not None
                else current_oc["character_info"]
            )

            await conn.execute(
                """
                UPDATE ocs
                SET rarity = $1,
                    character_info = $2,
                    image_link = $3
                WHERE name = $4;
                """,
                rarity,
                character_info,
                image_link,
                name,
            )
        pretty_log(
            tag="info",
            message=f"Edited OC '{name}' in database.",
        )
        # Update cache as well
        from utils.cache.ocs_cache import edit_oc_cache

        await edit_oc_cache(bot, name, character_info, image_link)

    except Exception as e:
        pretty_log(
            tag="error",
            message=f"Error editing OC '{name}': {e}",
        )
