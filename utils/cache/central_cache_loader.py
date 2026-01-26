import discord

from utils.logs.pretty_log import pretty_log

from .ocs_cache import load_ocs_cache
from .user_inv_cache import load_all_user_oc_inv_cache


async def load_all_cache(bot: discord.Client):
    """Loads all caches for the bot."""
    pretty_log("info", "Loading all caches...")

    # Load OCs cache
    await load_ocs_cache(bot)

    # Load User OC Inventories cache
    await load_all_user_oc_inv_cache(bot)

    pretty_log("info", "All caches loaded successfully.")
