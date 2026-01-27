# 🌠 utils.loggers.pretty_logs import pretty_log

import traceback
from datetime import datetime

import discord
from discord.ext import commands

# -------------------- 🌠 Global Bot Reference --------------------
BOT_INSTANCE: commands.Bot | None = None


def set_bot(bot: commands.Bot):
    """Set the global bot instance for automatic logging."""
    global BOT_INSTANCE
    BOT_INSTANCE = bot


# -------------------- 🌠 Critical Logs Channel --------------------
CRITICAL_LOG_CHANNEL_ID = (
    1444997181244444672  # TODO: replace with your bot error log channel
)

# -------------------- 🌌 Logging Tags --------------------
TAGS = {
    "info": "🏮 INFO",  # red lantern (night light)
    "db": "🔮 STAR DB",  # crystal ball (mystical/night)
    "cmd": "🌌 COMMAND",  # milky way (night sky)
    "ready": "🌙 READY",  # crescent moon
    "error": "💜 ERROR",  # purple heart (night color)
    "warn": "🦉 WARN",  # owl (night animal)
    "critical": "🌑 CRITICAL",  # new moon (darkest phase)
    "skip": "🌃 SKIP",  # night cityscape
    "sent": "💫 SENT",  # shooting star (night)
    "debug": "🧿 DEBUG",  # evil eye (mystical/night)
}

# -------------------- 🎨 ANSI Colors --------------------
COLOR_LAVENDER = "\033[38;2;180;140;255m"  # soft lavender for info/default
COLOR_PURPLE_MEDIUM = "\033[38;2;160;90;220m"  # medium purple for warnings
COLOR_PURPLE_VIBRANT = "\033[38;2;130;0;180m"  # vibrant purple for critical/error
COLOR_RESET = "\033[0m"
COLOR_RESET = "\033[0m"


# -------------------- ✨ Pretty Log --------------------
def pretty_log(
    tag: str = None,
    message: str = "",
    *,
    label: str = None,
    bot: commands.Bot = None,
    include_trace: bool = True,
):
    prefix = TAGS.get(tag) if tag else ""
    # combine tag + label with ★ if label exists
    if prefix and label:
        prefix_part = f"[{prefix} ★ {label}] "
    elif prefix:
        prefix_part = f"[{prefix}] "
    elif label:
        prefix_part = f"[{label}] "
    else:
        prefix_part = ""

    # Choose color
    if tag in ("critical", "error"):
        color = COLOR_PURPLE_VIBRANT
    elif tag == "warn":
        color = COLOR_PURPLE_MEDIUM
    else:
        color = COLOR_LAVENDER

    now = datetime.now().strftime("%H:%M:%S")
    log_message = f"[{now}] {prefix_part}{message}"
    print(f"{color}{log_message}{COLOR_RESET}")

    # Print traceback in console
    if include_trace and tag in ("error", "critical"):
        traceback.print_exc()

    bot_to_use = bot or BOT_INSTANCE

    # Send to Discord channel if needed
    if bot_to_use and tag in ("critical", "error", "warn"):
        try:
            channel = bot_to_use.get_channel(CRITICAL_LOG_CHANNEL_ID)
            if channel:
                full_message = f"{prefix_part}{message}"
                if include_trace and tag in ("error", "critical"):
                    full_message += f"\n```py\n{traceback.format_exc()}```"
                if len(full_message) > 2000:
                    full_message = full_message[:1997] + "..."
                bot_to_use.loop.create_task(channel.send(full_message))
        except Exception:
            print("[☄️ ERROR] Failed to send log to bot channel:")
            traceback.print_exc()


# -------------------- 🌠 UI Error --------------------
def log_ui_error(
    *,
    error: Exception,
    interaction: discord.Interaction = None,
    label: str = "UI",
    bot: commands.Bot = None,
    include_trace: bool = True,
):
    """Logs UI errors with automatic Discord reporting."""
    location_info = ""
    if interaction:
        user = interaction.user
        location_info = f"User: {user} ({user.id}) | Channel: {interaction.channel} ({interaction.channel_id})"

    error_message = f"UI error occurred. {location_info}".strip()
    now = datetime.now().strftime("%H:%M:%S")

    print(
        f"{COLOR_PURPLE_VIBRANT}[{now}] [💫 CRITICAL {label}] error: {error_message}{COLOR_RESET}"
    )

    if include_trace:
        traceback.print_exception(type(error), error, error.__traceback__)

    bot_to_use = bot or BOT_INSTANCE

    pretty_log(
        "error",
        error_message,
        label=label,
        bot=bot_to_use,
        include_trace=include_trace,
    )

    if bot_to_use:
        try:
            channel = bot_to_use.get_channel(CRITICAL_LOG_CHANNEL_ID)
            if channel:
                embed = discord.Embed(
                    title=f"☄️ UI Error Logged [{label}]",
                    description=f"{location_info or '*No interaction data*'}",
                    color=0xA45EE5,  # night-themed purple
                )
                if include_trace:
                    trace_text = "".join(
                        traceback.format_exception(
                            type(error), error, error.__traceback__
                        )
                    )
                    if len(trace_text) > 1000:
                        trace_text = trace_text[:1000] + "..."
                    embed.add_field(
                        name="Traceback", value=f"```py\n{trace_text}```", inline=False
                    )
                bot_to_use.loop.create_task(channel.send(embed=embed))
        except Exception:
            print("[☄️ ERROR] Failed to send UI error to bot log channel:")
            traceback.print_exc()
