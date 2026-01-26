import discord

from utils.logs.pretty_log import pretty_log

# SQL SCRIPT
"""CREATE TABLE user_oc_inv (
    user_id TEXT NOT NULL,
    user_name TEXT NOT NULL,
    card_name TEXT NOT NULL,
    rarity TEXT NOT NULL,
    character_info TEXT,
    image_link TEXT NOT NULL,
    owned INT NOT NULL,
    PRIMARY KEY (user_id, card_name)
);"""


async def user_inv_oc_name_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[discord.app_commands.Choice[str]]:
    """Provides autocomplete suggestions for OC names in a user's inventory."""
    from utils.cache.user_inv_cache import list_oc_names_in_user_inv_cache

    user_id = interaction.user.id
    oc_names_in_inv = list_oc_names_in_user_inv_cache(user_id)
    suggestions = [
        discord.app_commands.Choice(name=oc_name, value=oc_name)
        for oc_name in oc_names_in_inv
        if current.lower() in oc_name.lower()
    ]
    return suggestions[:25]  # Limit to top 25 suggestions


async def upsert_user_oc_inv(
    bot: discord.Client,
    user_id: int,
    user_name: str,
    card_name: str,
    rarity: str,
    image_link: str,
    owned: int,
    character_info: str | None,
):
    """Inserts or updates a user OC inventory entry in the database."""
    try:
        async with bot.pg_pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO user_oc_inv (user_id, user_name, card_name, rarity, character_info, image_link, owned)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (user_id, card_name) DO UPDATE
                SET user_name = EXCLUDED.user_name,
                    rarity = EXCLUDED.rarity,
                    character_info = EXCLUDED.character_info,
                    image_link = EXCLUDED.image_link,
                    owned = EXCLUDED.owned;
                """,
                user_id,
                user_name,
                card_name,
                rarity,
                character_info,
                image_link,
                owned,
            )
        pretty_log(
            tag="info",
            message=f"Upserted user OC inventory for user '{user_id}', card '{card_name}' into database.",
        )
        # Update cache as well
        from utils.cache.user_inv_cache import upsert_user_oc_inv_cache

        upsert_user_oc_inv_cache(
            user_id=user_id,
            user_name=user_name,
            card_name=card_name,
            rarity=rarity,
            character_info=character_info,
            image_link=image_link,
            owned=owned,
        )
    except Exception as e:
        pretty_log(
            tag="error",
            message=f"Error upserting user OC inventory for user '{user_id}', card '{card_name}': {e}",
        )


async def fetch_all_user_oc_invs(
    bot: discord.Client,
) -> dict[int, list[dict[str, str]]]:
    """Fetches the OC inventories for all users."""
    try:
        async with bot.pg_pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT user_id, user_name, card_name, rarity, character_info, image_link, owned
                FROM user_oc_inv;
                """
            )
            user_invs = {}
            for row in rows:
                user_id = row["user_id"]
                if user_id not in user_invs:
                    user_invs[user_id] = []
                user_invs[user_id].append(
                    {
                        "user_name": row["user_name"],
                        "card_name": row["card_name"],
                        "rarity": row["rarity"],
                        "character_info": row["character_info"],
                        "image_link": row["image_link"],
                        "owned": row["owned"],
                    }
                )
            return user_invs
    except Exception as e:
        pretty_log(
            tag="error",
            message=f"Error fetching all user OC inventories: {e}",
        )
        return {}


async def fetch_user_oc_inv(bot: discord.Client, user_id: int) -> list[dict[str, str]]:
    """Fetches the OC inventory for a specific user."""
    try:
        async with bot.pg_pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT card_name, rarity, character_info, image_link, owned
                FROM user_oc_inv
                WHERE user_id = $1;
                """,
                user_id,
            )
            return [
                {
                    "card_name": row["card_name"],
                    "rarity": row["rarity"],
                    "character_info": row["character_info"],
                    "image_link": row["image_link"],
                    "owned": row["owned"],
                }
                for row in rows
            ]
    except Exception as e:
        pretty_log(
            tag="error",
            message=f"Error fetching user OC inventory for user '{user_id}': {e}",
        )
        return []


async def increment_oc_owned(
    bot: discord.Client,
    user_id: int,
    card_name: str,
    increment_by: int = 1,
):
    """Increments the owned count of a specific OC in a user's inventory."""
    try:
        async with bot.pg_pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE user_oc_inv
                SET owned = owned + $1
                WHERE user_id = $2 AND card_name = $3;
                """,
                increment_by,
                user_id,
                card_name,
            )
        pretty_log(
            tag="info",
            message=f"Incremented owned count for user '{user_id}', card '{card_name}' by {increment_by}.",
        )
        # Update cache as well
        from utils.cache.user_inv_cache import increment_oc_owned_cache

        increment_oc_owned_cache(user_id, card_name)
    except Exception as e:
        pretty_log(
            tag="error",
            message=f"Error incrementing owned count for user '{user_id}', card '{card_name}': {e}",
        )


async def decrement_oc_owned(
    bot: discord.Client,
    user_id: int,
    card_name: str,
    decrement_by: int = 1,
):
    """Decrements the owned count of a specific OC in a user's inventory."""
    try:
        async with bot.pg_pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE user_oc_inv
                SET owned = GREATEST(owned - $1, 0)
                WHERE user_id = $2 AND card_name = $3;
                """,
                decrement_by,
                user_id,
                card_name,
            )
        pretty_log(
            tag="info",
            message=f"Decremented owned count for user '{user_id}', card '{card_name}' by {decrement_by}.",
        )
        # Update cache as well
        from utils.cache.user_inv_cache import decrement_oc_owned_cache

        decrement_oc_owned_cache(user_id, card_name)
    except Exception as e:
        pretty_log(
            tag="error",
            message=f"Error decrementing owned count for user '{user_id}', card '{card_name}': {e}",
        )


async def update_oc_owned(
    bot: discord.Client,
    user_id: int,
    card_name: str,
    new_owned: int,
):
    """Updates the owned count of a specific OC in a user's inventory."""
    try:
        async with bot.pg_pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE user_oc_inv
                SET owned = $1
                WHERE user_id = $2 AND card_name = $3;
                """,
                new_owned,
                user_id,
                card_name,
            )
        pretty_log(
            tag="info",
            message=f"Updated owned count for user '{user_id}', card '{card_name}' to {new_owned}.",
        )
        # Update cache as well
        from utils.cache.user_inv_cache import update_oc_owned_cache

        update_oc_owned_cache(user_id, card_name, new_owned)
    except Exception as e:
        pretty_log(
            tag="error",
            message=f"Error updating owned count for user '{user_id}', card '{card_name}': {e}",
        )


async def delete_user_inv(
    bot: discord.Client,
    user_id: int,
):
    """Deletes the entire OC inventory for a specific user."""
    try:
        async with bot.pg_pool.acquire() as conn:
            await conn.execute(
                """
                DELETE FROM user_oc_inv
                WHERE user_id = $1;
                """,
                user_id,
            )

        pretty_log(
            tag="info",
            message=f"Deleted OC inventory for user '{user_id}'.",
        )
        # Delete from cache as well
        from utils.cache.user_inv_cache import delete_user_inv_cache

        delete_user_inv_cache(user_id)

    except Exception as e:
        pretty_log(
            tag="error",
            message=f"Error deleting OC inventory for user '{user_id}': {e}",
        )
