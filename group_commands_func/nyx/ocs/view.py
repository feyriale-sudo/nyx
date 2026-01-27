import discord
from discord.ui import Button, View

import utils.cache.cache_list as cache_list
from config.ocs import OCS_RARITY_MAP
from config.setup import DEFAULT_EMBED_COLOR
from utils.logs.debug_log import debug_log, enable_debug
from utils.logs.pretty_log import pretty_log
from utils.visuals.pretty_defer import pretty_defer

#enable_debug(f"{__name__}.view_ocs_func")
#enable_debug(f"{__name__}.get_embed")


class OC_Paginator(View):

    def __init__(
        self,
        bot,
        user,
        items,
        title,
        color,
        initial_rarity,
        context,
        per_page=10,
        timeout=120,
    ):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.user = user
        self.items = items
        self.title = title
        self.color = color
        self.initial_rarity = initial_rarity
        self.context = context
        self.per_page = per_page
        self.page = 0
        self.max_page = (len(items) - 1) // per_page + 1
        self.message: discord.Message | None = None  # Store the message object

        # If only one page, disable buttons
        if self.max_page == 0:
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
            # oc is a dict with a single key (the OC name)
            oc_name = list(oc.keys())[0]
            info = oc[oc_name]
            # Always get rarity from info for each OC
            oc_rarity = info.get("rarity", self.initial_rarity or "Unknown")
            rarity_emoji = OCS_RARITY_MAP.get(oc_rarity, {}).get("emoji", "")
            image_link = info.get("image_link", "No Image")
            number = start + idx + 1
            display_name = oc_name.title()
            name_str = f"{number}. {rarity_emoji} [{display_name}]({image_link})"
            desc_lines.append(name_str)

        description = "\n".join(desc_lines)
        embed = discord.Embed(
            title=title,
            color=self.color,
            description=description,
        )
        from utils.cache.ocs_cache import (
            get_overall_count_str,
            get_total_count_by_rarity,
        )

        pretty_log(tag="info", message=f"Context = {self.context}")
        # Footer logic: always show rarity emoji and count if specific rarity, else show detailed count string
        if self.initial_rarity == "All":
            count_str = get_overall_count_str()
            pretty_log(tag="info", message=f"Footer count string: {count_str}")
            debug_log(f"Footer count string: {count_str}")
            footer_text = f"Page {self.page + 1} of {self.max_page} | {count_str}"
        else:
            # Use initial_rarity for emoji and label
            pretty_log(
                tag="info", message=f"Initial rarity for footer: {self.initial_rarity}"
            )

            rarity = self.initial_rarity or "Unknown"
            rarity_emoji = OCS_RARITY_MAP.get(rarity, {}).get("emoji", "")
            total_count = get_total_count_by_rarity(rarity)
            footer_text = f"Page {self.page + 1} of {self.max_page} | {rarity_emoji} {total_count} {rarity} OCs"
        embed.set_footer(text=footer_text)
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


async def view_ocs_func(
    bot: discord.Client,
    interaction: discord.Interaction,
    rarity: str = None,
):
    """Function to view all OCs or OCs by rarity."""

    debug_log(f"view_ocs_func called with rarity: {rarity}")
    debug_log(f"Initial ocs_cache length: {len(cache_list.ocs_cache)}")
    debug_log(
        f"User: {getattr(interaction.user, 'id', None)} | {getattr(interaction.user, 'display_name', None)}"
    )

    # Defer
    loader = await pretty_defer(
        interaction=interaction, content="Fetching OCs...", ephemeral=False
    )
    if not rarity:
        rarity = "All"
    else:
        context = f"{rarity} OCs"

    # Check if cache is populated, if not load it
    if not cache_list.ocs_cache:
        debug_log("OCs cache is empty, loading cache...")
        from utils.cache.ocs_cache import load_ocs_cache

        await load_ocs_cache(bot)

    # Determine which cache to use based on rarity
    if rarity == "Common":
        selected_cache = cache_list.common_ocs_cache
        title = "Common Rarity OCs"
    elif rarity == "Rare":
        selected_cache = cache_list.rare_ocs_cache
        title = "Rare Rarity OCs"
    elif rarity == "Epic":
        selected_cache = cache_list.epic_ocs_cache
        title = "Epic Rarity OCs"
    elif rarity == "Legendary OCs":
        selected_cache = cache_list.legendary_ocs_cache
    else:
        selected_cache = cache_list.ocs_cache
        title = "All OCs"
        context = "all OCs"

    debug_log(f"Selected cache type: {type(selected_cache)}")
    debug_log(f"Selected cache length: {len(selected_cache)}")
    if selected_cache:
        debug_log(f"First item in selected_cache: {selected_cache[0]}")
    debug_log(f"Context: {context}, Title: {title}")

    if not selected_cache:
        if rarity:
            await loader.error(content=f"No OCs found for rarity '{rarity}'.")
        else:
            await loader.error(content="No OCs found.")
        return

    if title == "All OCs":
        # Sort all OCs: Common first, then Rare, then Legendary, then Epic, each group sorted alphabetically by name
        rarity_order = {"Common": 1, "Rare": 2, "Epic": 3, "Legendary": 4}
        debug_log(f"Rarity order mapping: {rarity_order}")

        def get_rarity_and_name(oc):
            oc_name = list(oc.keys())[0]
            info = oc[oc_name]
            rarity = str(info.get("rarity", "")).strip().title()
            return (rarity_order.get(rarity, 99), oc_name.lower())

        sorted_ocs = sorted(selected_cache, key=get_rarity_and_name)
        # Debug: print the rarity and name order for ALL sorted OCs
        debug_log("--- FULL SORTED ORDER ---")
        for oc in sorted_ocs:
            oc_name = list(oc.keys())[0]
            info = oc[oc_name]
            debug_log(f"SORTED: {info.get('rarity')} - {oc_name}")
        debug_log("--- END FULL SORTED ORDER ---")
        import sys

        sys.stdout.flush()
        color = DEFAULT_EMBED_COLOR
        context = "all OCs"
    else:
        # Sort by name only, using the OC name from the nested dict
        debug_log(f"Sorting OCs by name for rarity: {rarity}")

        def get_oc_name(oc):
            return list(oc.keys())[0]

        color = OCS_RARITY_MAP.get(rarity, {}).get("color", DEFAULT_EMBED_COLOR)
        sorted_ocs = sorted(selected_cache, key=get_oc_name)
        context = f"by rarity"

    debug_log(f"Sorted OCs length: {len(sorted_ocs)}")
    if sorted_ocs:
        debug_log(f"First item in sorted_ocs: {sorted_ocs[0]}")

    paginator = OC_Paginator(
        bot=bot,
        user=interaction.user,
        items=sorted_ocs,
        title=title,
        color=color,
        context=context,
        initial_rarity=rarity,
        per_page=10,
    )
    embed = await paginator.get_embed()
    debug_log(f"Paginator max_page: {paginator.max_page}")
    debug_log(f"Embed title: {embed.title}")
    debug_log(
        f"Embed description preview: {embed.description[:100] if embed.description else ''}"
    )
    sent_message = await loader.success(embed=embed, view=paginator, content="")
    paginator.message = sent_message  # Store the message object in the paginator
