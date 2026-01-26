import discord
from discord.ext import commands

from utils.logs.pretty_log import pretty_log
from utils.visuals.pretty_defer import pretty_defer


async def echo_func(
    bot: commands.Bot,
    interaction: discord.Interaction,
    channel: discord.TextChannel,
    message: str,
    member: discord.Member | None = None,
):
    loader = await pretty_defer(
        interaction=interaction,
        content=f"Sending message to {channel.mention}...",
        ephemeral=True,
    )

    # 🌸 Construct message content
    if member and channel.permissions_for(member).read_messages:
        content = f"{member.mention} {message}"
    else:
        content = message

    # 🌸 Send the message
    await channel.send(content)
    await loader.success(content=f"Message sent to {channel.mention}")

    # 🌸 Pretty log
    log_msg = f"{interaction.user} echoed a message to {channel.name})"
    if member:
        log_msg += f", tagged_member={member}"
    pretty_log("info", log_msg)
