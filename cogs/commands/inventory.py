import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View

from config.ocs import OCS_RARITY_MAP
from config.setup import DEFAULT_EMBED_COLOR
from utils.cache.cache_list import user_oc_inv_cache
from utils.cache.user_inv_cache import (
    fetch_all_rarity_oc_invs_cache,
    fetch_user_oc_inv_cache,
)
from utils.db.user_oc_inv import user_inv_oc_name_autocomplete
from utils.logs.pretty_log import pretty_log
from utils.visuals.pretty_defer import pretty_defer


class OC_Paginator(View):

    def __init__(
        self, bot, user, items, title, color, context, per_page=10, timeout=120
    ):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.user = user
        self.items = items
        self.title = title
        self.color = color
        self.context = context
        self.per_page = per_page
        self.page = 0
        self.max_page = (len(items) - 1) // per_page + 1
        self.message: discord.Message | None = None  # Store the message object

        # If only one page, remove buttons
        if self.max_page == 1:
            self.clear_items()

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary)
    async def previous_page(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message(
                "You cannot interact with this paginator.", ephemeral=True
            )
            return

        if self.page > 0:
            self.page -= 1
            embed = await self.get_embed()
            await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
    async def next_page(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message(
                "You cannot interact with this paginator.", ephemeral=True
            )
            return

        if self.page < self.max_page - 1:
            self.page += 1
            embed = await self.get_embed()
            await interaction.response.edit_message(embed=embed, view=self)

    async def update_buttons(self, interaction: discord.Interaction):
        # Disable buttons if on first or last page
        for item in self.children:
            if isinstance(item, Button):
                if item.label == "Previous":
                    item.disabled = self.page == 0
                elif item.label == "Next":
                    item.disabled = self.page >= self.max_page - 1
        await interaction.message.edit(view=self)

    async def get_embed(self):
        start = self.page * self.per_page
        end = start + self.per_page
        page_items = self.items[start:end]

        title = self.title

        desc_lines = []
        for idx, oc in enumerate(page_items):
            oc_name = oc.get("card_name", "Unknown")
            oc_rarity = oc.get("rarity", "Unknown")
            rarity_emoji = OCS_RARITY_MAP.get(oc_rarity, {}).get("emoji", "")
            image_link = oc.get("image_link", "No Image")
            number = start + idx + 1
            display_name = oc_name.title()
            name_str = f"{number}. {rarity_emoji} [{display_name}]({image_link}) | Owned: {oc.get('owned', 0)}"
            desc_lines.append(name_str)

        description = "\n".join(desc_lines)
        embed = discord.Embed(
            title=title,
            color=self.color,
            description=description,
        )
        from utils.cache.user_inv_cache import (
            total_cards_owned_cache,
            total_unique_cards_owned_cache,
            total_owned_cards_by_rarity_cache,
            total_unique_cards_by_rarity_cache,
        )

        if self.context == "all OCs":
            total_unique_count = total_unique_cards_owned_cache()
            total_owned_count = total_cards_owned_cache()
            total_count_str = f"{total_unique_count} Unique OCs | {total_owned_count} Total OCs Owned"
            embed.set_footer(
                text=f"Page {self.page + 1} of {self.max_page} | {total_count_str}"
            )
        else:
            total_owned = total_owned_cards_by_rarity_cache(self.rarity)
            total_unique_cards = total_unique_cards_by_rarity_cache(self.rarity)
            total_count_str = f"{total_unique_cards} Unique | {total_owned} Owned"
            embed.set_footer(
                text=f"Page {self.page + 1} of {self.max_page} | {total_count_str} {self.rarity} OCs"
            )
        return embed

    async def on_timeout(self):
        # Disable all buttons on timeout
        for item in self.children:
            if isinstance(item, Button):
                item.disabled = True
        if self.message:
            try:
                await self.message.edit(view=self)
            except Exception as e:
                pass


# Slash command cog
class Inventory(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="inventory", description="View your OC inventory.")
    @app_commands.describe(rarity="Filter by rarity (optional)")
    async def inventory(
        self, interaction: discord.Interaction, rarity: str | None = None
    ):
        """Slash command to view all OCs or OCs by rarity."""
        # Defer
        loader = await pretty_defer(
            interaction=interaction, content="Fetching inventory...", ephemeral=False
        )

        # Check if cache is populated, if not load it
        if not user_oc_inv_cache:
            await loader.error(content="No inventory data found.")
            return

        # Determine which cache to use based on rarity
        if rarity:
            selected_cache = fetch_all_rarity_oc_invs_cache(interaction.user.id, rarity)
            title = f"{interaction.user.display_name}'s Inventory - {rarity} OCs"
            color = OCS_RARITY_MAP.get(rarity, {}).get("color", DEFAULT_EMBED_COLOR)
        else:
            selected_cache = fetch_user_oc_inv_cache(interaction.user.id)
            title = f"{interaction.user.display_name}'s Inventory - All OCs"
            color = DEFAULT_EMBED_COLOR

        if not selected_cache:
            if rarity:
                await loader.error(content=f"No OCs found for rarity '{rarity}'.")
            else:
                await loader.error(content="No OCs found.")
            return

        if not rarity:
            # Sort all OCs alphabetically rarity then name
            rarity_order = {"Common": 1, "Rare": 2, "Epic": 3, "Legendary": 4}
            sorted_ocs = sorted(
                selected_cache,
                key=lambda oc: (
                    rarity_order.get(oc.get("rarity"), 99),
                    oc.get("card_name", ""),
                ),
            )
            color = DEFAULT_EMBED_COLOR
            context = "all OCs"
        else:
            # Sort by name only
            color = OCS_RARITY_MAP.get(rarity, {}).get("color", DEFAULT_EMBED_COLOR)
            sorted_ocs = sorted(selected_cache, key=lambda oc: oc.get("card_name", ""))
            context = f"by rarity"

        paginator = OC_Paginator(
            bot=self.bot,
            user=interaction.user,
            items=sorted_ocs,
            title=title,
            color=color,
            context=context,
            per_page=10,
        )
        embed = await paginator.get_embed()
        sent_message = await loader.success(embed=embed, view=paginator, content="")
        paginator.message = sent_message  # Store the message object in the paginator


async def setup(bot: commands.Bot):
    await bot.add_cog(Inventory(bot))
