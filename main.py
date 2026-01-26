import glob
import logging
import os
import warnings

import discord
from discord.ext import commands

from utils.cache.central_cache_loader import load_all_cache
from utils.db.get_pg_pool import *
from utils.logs.pretty_log import pretty_log, set_bot

# ╭───────────────────────────────╮
#   ⭐ Suppress Default Discord Logs
# ╰───────────────────────────────╯
logging.basicConfig(level=logging.CRITICAL)
logging.getLogger("discord").setLevel(logging.CRITICAL)
logging.getLogger("discord.gateway").setLevel(logging.CRITICAL)
logging.getLogger("discord.http").setLevel(logging.CRITICAL)
logging.getLogger("discord.client").setLevel(logging.CRITICAL)
logging.getLogger("asyncio").setLevel(logging.CRITICAL)
warnings.filterwarnings("ignore")

# ╭───────────────────────────────╮
#   ⭐ Bot Setup
# ╰───────────────────────────────╯
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix=".", intents=intents)

# Set the global bot instance for pretty_log
set_bot(bot)


# ╭───────────────────────────────╮
#   ⭐ Error Handler
# ╰───────────────────────────────╯
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return  # Ignore CommandNotFound errors


# ╭───────────────────────────────╮
#   ⭐ On Ready Event
# ╰───────────────────────────────╯
@bot.event
async def on_ready():
    pretty_log("ready", f"Nyx bot awake as {bot.user}")

    # ❀ Sync slash commands ❀
    await bot.tree.sync()
    pretty_log("info", "Slash commands synced.")

    # ❀ Load all caches ❀
    await load_all_cache(bot)


# ╭───────────────────────────────╮
#   ⭐ Setup Hook
# ╰───────────────────────────────╯
@bot.event
async def setup_hook():
    # ❀ PostgreSQL connection ❀
    try:
        bot.pg_pool = await get_pg_pool()
    except Exception as e:
        pretty_log("critical", f"Postgres connection failed: {e}", include_trace=True)

    # ❀ Load all cogs ❀
    for cog_path in glob.glob("cogs/**/*.py", recursive=True):
        if os.path.basename(cog_path) == "__init__.py":
            continue  # Skip __init__.py files
        relative_path = os.path.relpath(cog_path, "cogs")
        module_name = relative_path[:-3].replace(os.sep, ".")
        cog_name = f"cogs.{module_name}"
        #pretty_log("debug", f"Attempting to load cog: {cog_name}")
        try:
            await bot.load_extension(cog_name)
            #pretty_log("info", f"Loaded cog: {cog_name}")
        except Exception as e:
            pretty_log("error", f"Failed to load {cog_name}: {e}", include_trace=True)


# ╭───────────────────────────────╮
#   ⭐ Main Async Runner
# ╰───────────────────────────────╯
async def main():
    load_dotenv()
    pretty_log("ready", "Nyx Bot is starting...")

    retry_delay = 5
    while True:
        try:
            await bot.start(os.getenv("DISCORD_TOKEN"))
        except KeyboardInterrupt:
            pretty_log("ready", "Shutting down Nyx Bot...")
            break
        except Exception as e:
            pretty_log("error", f"Bot crashed: {e}", include_trace=True)
            pretty_log("ready", f"Restarting Nyx Bot in {retry_delay} seconds...")
            await asyncio.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, 60)


# ╭───────────────────────────────╮
#   ⭐ Entry Point
# ╰───────────────────────────────╯
if __name__ == "__main__":
    asyncio.run(main())
