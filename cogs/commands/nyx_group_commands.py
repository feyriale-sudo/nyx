from typing import Literal, Optional, Union

import discord
from discord import app_commands
from discord.ext import commands

from group_commands_func.nyx import *
from utils.db.ocs_db import oc_name_autocomplete
from utils.essentials.command_safe import run_command_safe


# 🎀────────────────────────────────────────────
#           🌸 Nyx Group Commands Cog Setup 🌸
# ─────────────────────────────────────────────
class NyxGroupCommands(commands.Cog):
    """Nyx group commands cog."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_app_command_check(self, interaction: discord.Interaction) -> bool:
        """
        Global check for all Nyx group app commands: only allow users with Administrator permission.
        """
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "You do not have permission to use this command (Administrator required).",
                ephemeral=True,
            )
            return False
        return True

    # 🎀────────────────────────────────────────────
    #           🌸 Slash Command Group 🌸
    # 🎀────────────────────────────────────────────
    nyx_group = app_commands.Group(name="nyx", description="Nyx bot commands")
    # 🎀────────────────────────────────────────────
    #           🌸 Sub Command Group 🌸
    # 🎀────────────────────────────────────────────
    oc_group = app_commands.Group(
        name="oc",
        description="Commands related to Original Characters (OCs)",
    )
    nyx_group.add_command(oc_group)

    # 🎀────────────────────────────────────────────
    #              🌸 /nyx echo 🌸
    # 🎀────────────────────────────────────────────
    @nyx_group.command(
        name="echo",
        description="Send a message to a channel, with optional tagging",
    )
    @app_commands.describe(
        channel="The channel where the message will be sent",
        message="The message you want to send",
        member="Optional member to tag in the message",
    )
    async def echo(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        message: str,
        member: discord.Member | None = None,
    ):
        """Sends a message to a specified channel, optionally tagging a member."""
        slash_cmd_name = "nyx echo"

        await run_command_safe(
            bot=self.bot,
            interaction=interaction,
            slash_cmd_name=slash_cmd_name,
            command_func=echo_func,
            channel=channel,
            message=message,
            member=member,
        )

    echo.extras = {"category": "Admin"}

    # 🎀────────────────────────────────────────────
    #              🌸 /nyx oc create 🌸
    # 🎀────────────────────────────────────────────
    @oc_group.command(
        name="create",
        description="Create a new Original Character (OC) entry.",
    )
    @app_commands.describe(
        name="The name of the OC.",
        rarity="The rarity of the OC (e.g., Common, Rare, Epic, Legendary).",
        image_link="A link to an image representing the OC.",
        character_info="A brief description or information about the OC.",
    )
    async def create_oc(
        self,
        interaction: discord.Interaction,
        name: str,
        rarity: Literal["Common", "Rare", "Epic", "Legendary"],
        image_link: str,
        character_info: str = None,
    ):
        """Creates a new OC entry in the database."""
        slash_cmd_name = "nyx oc create"

        await run_command_safe(
            bot=self.bot,
            interaction=interaction,
            slash_cmd_name=slash_cmd_name,
            command_func=create_oc_func,
            name=name,
            rarity=rarity,
            image_link=image_link,
            character_info=character_info,
        )

    create_oc.extras = {"category": "Admin"}

    # 🎀────────────────────────────────────────────
    #              🌸 /nyx oc remove 🌸
    # 🎀────────────────────────────────────────────
    @oc_group.command(
        name="remove",
        description="Remove an existing Original Character (OC) entry.",
    )
    @app_commands.autocomplete(
        name=oc_name_autocomplete,
    )
    @app_commands.describe(
        name="The name of the OC to remove.",
    )
    async def remove_oc(
        self,
        interaction: discord.Interaction,
        name: str,
    ):
        """Removes an existing OC entry from the database."""
        slash_cmd_name = "nyx oc remove"

        await run_command_safe(
            bot=self.bot,
            interaction=interaction,
            slash_cmd_name=slash_cmd_name,
            command_func=remove_oc_func,
            name=name,
        )

    remove_oc.extras = {"category": "Admin"}

    # 🎀────────────────────────────────────────────
    #              🌸 /nyx oc edit 🌸
    # 🎀────────────────────────────────────────────
    @oc_group.command(
        name="edit",
        description="Edit an existing Original Character (OC) entry.",
    )
    @app_commands.autocomplete(
        name=oc_name_autocomplete,
    )
    @app_commands.describe(
        name="The name of the OC to edit.",
        new_rarity="The new rarity of the OC (leave blank to keep unchanged).",
        new_image_link="The new image link for the OC (leave blank to keep unchanged).",
        new_character_info="The new character info for the OC (leave blank to keep unchanged).",
    )
    async def edit_oc(
        self,
        interaction: discord.Interaction,
        name: str,
        new_rarity: Optional[Literal["Common", "Rare", "Epic", "Legendary"]] = None,
        new_image_link: Optional[str] = None,
        new_character_info: Optional[str] = None,
    ):
        """Edits an existing OC entry in the database."""
        slash_cmd_name = "nyx oc edit"

        await run_command_safe(
            bot=self.bot,
            interaction=interaction,
            slash_cmd_name=slash_cmd_name,
            command_func=edit_oc_func,
            name=name,
            new_rarity=new_rarity,
            new_image_link=new_image_link,
            new_character_info=new_character_info,
        )

    edit_oc.extras = {"category": "Admin"}

    # 🎀────────────────────────────────────────────
    #              🌸 /nyx oc view 🌸
    # 🎀────────────────────────────────────────────
    @oc_group.command(
        name="view",
        description="View all Original Characters (OCs) in the database.",
    )
    @app_commands.describe(
        rarity="Filter OCs by rarity (optional).",
    )
    async def view_ocs(
        self,
        interaction: discord.Interaction,
        rarity: Optional[Literal["Common", "Rare", "Epic", "Legendary"]] = None,
    ):
        """Views all OCs or OCs by rarity from the database."""
        slash_cmd_name = "nyx oc view"

        await run_command_safe(
            bot=self.bot,
            interaction=interaction,
            slash_cmd_name=slash_cmd_name,
            command_func=view_ocs_func,
            rarity=rarity,
        )

    view_ocs.extras = {"category": "Admin"}


async def setup(bot: commands.Bot):
    """Sets up the NyxGroupCommands cog."""
    await bot.add_cog(NyxGroupCommands(bot))
