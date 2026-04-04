import asyncio
import logging

# from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord import app_commands

log = logging.getLogger(__name__)

# Initialize global state dictionary for pug queue
queue_handler = {}
timeout_tasks = {}
panel_messages = {}

# Set up the timeout logic for the bot
TIMEOUT_DURATION = 3*60*60  # 3 hours

async def timeout_clear(bot: commands.Bot, channel_id):
    try:
        await asyncio.sleep(TIMEOUT_DURATION)

        # Check if players are in queue
        queue = queue_handler.get(channel_id)
        if not queue or not queue['players']:
            return

        # Clear queue
        queue_handler.pop(channel_id, None)
        timeout_tasks.pop(channel_id, None)

        # Change nickname, refresh panel, reset timeout counter
        await update_queue(bot, channel_id)

        # Notify channel that queue has been cleared
        channel = await bot.fetch_channel(channel_id)
        await channel.send(
            f"PUG queue has been cleared of all players, due to {int(TIMEOUT_DURATION // (60*60))} hour(s) of inactivity. :hourglass:")
        
        await clear_timeout(channel_id)
        guild = channel.guild
        print(f"Clearing PUG queue in {channel}, {guild}...")

    except asyncio.CancelledError:
        pass

# Function to reset the timeout counter
def reset_timeout_counter(bot: commands.Bot, channel_id):
    if channel_id in timeout_tasks:
        timeout_tasks[channel_id].cancel()

    task = asyncio.create_task(timeout_clear(bot, channel_id))
    timeout_tasks[channel_id] = task

# Function to remove any active timeout counters in the channel
async def clear_timeout(channel_id):
    if channel_id in timeout_tasks:
        timeout_tasks[channel_id].cancel()
        timeout_tasks.pop(channel_id, None)

# Function to resolve interaction channel (bot must only take inputs from the channel it is being used in)
def get_state(channel_id):
    if channel_id not in queue_handler:
        queue_handler[channel_id] = {
            "players": []
        }
    return queue_handler[channel_id]

# Build PUG panel embed
def build_main_panel_embed(channel_id: int):
    queue = get_state(channel_id)

    description=("Join the queue to play!\n\n"
                 "**Competitive rules apply**. Click **How to Play** for more info.")

    embed = discord.Embed(
        title="Competitive PUG Queue",
        description=description,
        colour=0x99AAB5
    )

    embed.add_field(name="", value="\u00AD", inline=False)

    if not queue['players']:
        embed.add_field(name="Player Queue", value="Queue is empty :dash:", inline=False)
    else:
        embed.add_field(
            name="Player Queue",
            value="\n".join(
                f"{i+1}. <@{user_id}>"
                for i, user_id in enumerate(queue['players'])
            ),
            inline=False
        )

    embed.set_footer(text="Created by Muffin-Dono")

    return embed

# Refresh PUG panel embed
async def refresh_panel(bot: commands.Bot, channel_id: int):
    if channel_id not in panel_messages:
        return

    channel = await bot.fetch_channel(channel_id)
    panel_message = await channel.fetch_message(panel_messages[channel_id])
    panel = build_main_panel_embed(channel_id)

    await panel_message.edit(embed=panel, view=MainButtons())

# Build Actions panel embed
def build_more_panel_embed(channel_id: int):

    embed = discord.Embed(
        title=":sparkles: Actions Menu",
        description=(
            "**Here are some bonus options to help players set up a PUG:**\n\n"
            "**Ping Queue**\n"
            "- DM players in the queue.\n"
            "**Map Vote**\n"
            "- Start a map vote for the PUG.\n"
            "**Scramble**\n"
            "- Randomize queued players into two teams.\n"),
        colour=0x99AAB5
    )

    embed.set_footer(text="Created by Muffin-Dono")

    return embed

# Change nickname according to the number of players in queue
async def change_nickname(bot: commands.Bot, channel_id: int):
    queue = get_state(channel_id)
    players = len(queue['players'])

    channel = await bot.fetch_channel(channel_id)
    guild = channel.guild
    me = guild.me

    if players > 0:
        nickname = f"{bot.user.name} ({players} in queue)"
    else:
        nickname = None

    await me.edit(nick=nickname)

# All the necessary updates in one function
async def update_queue(bot: commands.Bot, channel_id: int):
    await change_nickname(bot, channel_id)
    await refresh_panel(bot, channel_id)
    reset_timeout_counter(bot, channel_id)

# Function to join queue
async def queue_add(user_id: int, channel_id: int):
    queue = get_state(channel_id)

    if user_id in queue['players']:
        return False

    queue['players'].append(user_id)
    return True

# Function to leave queue
async def queue_remove(user_id: int, channel_id: int):
    queue = get_state(channel_id)

    if user_id not in queue['players']:
        return False

    queue['players'].remove(user_id)
    return True

class ButtonOnCooldown(commands.CommandError):
    pass
def key(interaction: discord.Interaction):
    return interaction.channel_id

ping_cd = commands.CooldownMapping.from_cooldown(1, 600, key) # 10 minutes

class MoreButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Ping Queue", style=discord.ButtonStyle.red, emoji="\U0001f514")
    async def ping_queue_button(self, interaction, button):
        
        queue = get_state(interaction.channel_id)

        if not queue['players']:
            await interaction.response.send_message("Queue is empty.", ephemeral=True)
            return

        if interaction.user.id not in queue['players']:
            await interaction.response.send_message("Only queued players may ping the queue.", ephemeral=True)
            return
        
        if len(queue['players']) < 6:
            await interaction.response.send_message(
                ":exclamation:**Don't Ping Queue yet**\n\n"
                "Aim for 10 players (5v5) first before you Ping Queue.\n"
                "If you want to start with less players (3v3, 4v4), ask the queue first.",
                ephemeral=True)
            return
        
        retry_after = ping_cd.update_rate_limit(interaction)
        if retry_after:
            minutes = int(retry_after // 60)
            await interaction.response.send_message(f"Ping is on cooldown. Try again in {minutes} minutes. :hourglass_flowing_sand:", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        for user_id in queue['players'][:10]:
            player = interaction.guild.get_member(user_id)

            await player.send(f"<@{interaction.user.id}> has pinged everyone in the queue! :bell:\n"
                              f"> <#{interaction.channel_id}>\n\n"
                              "Gather in VC and make teams! :sound:",
                              allowed_mentions=discord.AllowedMentions(users=False))
            
        await interaction.followup.send(f"**<@{interaction.user.id}> has pinged everyone in the queue! :bell:**",
                                        allowed_mentions=discord.AllowedMentions(users=True))

    @discord.ui.button(label="Map Vote", style=discord.ButtonStyle.blurple, emoji="\U0001f5fa")
    async def map_vote_button(self, interaction, button):
        await interaction.response.send_message(":tools: Planned (tentative)", ephemeral=True)

    @discord.ui.button(label="Scramble", style=discord.ButtonStyle.blurple, emoji="\U0001f500")
    async def scramble_button(self, interaction, button):
        await interaction.response.send_message(":tools: Planned (tentative)", ephemeral=True)

# Main set of buttons, for joining/leaving queue and guide
class MainButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Join Queue", style=discord.ButtonStyle.green, emoji="\U0000270b", custom_id='persistent_view:queue_add')
    async def join_button(self, interaction, button):
        queue = get_state(interaction.channel_id)

        added = await queue_add(interaction.user.id, interaction.channel_id)
        if not added:
            await interaction.response.send_message("You are already in the queue.", ephemeral=True)
            return

        await interaction.response.send_message(
            f"<@{interaction.user.id}> has joined the queue -----> **{len(queue['players'])} player(s) in queue**\n",
            allowed_mentions=discord.AllowedMentions(users=False))
        
        asyncio.create_task(update_queue(interaction.client, interaction.channel_id))

    @discord.ui.button(label="Leave Queue", style=discord.ButtonStyle.red, emoji="\U0001f44b", custom_id='persistent_view:queue_remove')
    async def leave_button(self, interaction, button):
        queue = get_state(interaction.channel_id)

        removed = await queue_remove(interaction.user.id, interaction.channel_id)
        if not removed:
            await interaction.response.send_message("You are not in the queue.", ephemeral=True)
            return

        await interaction.response.send_message(
            f"<@{interaction.user.id}> has left the queue -----> **{len(queue['players'])} player(s) in queue**\n",
            allowed_mentions=discord.AllowedMentions(users=False))
        
        asyncio.create_task(update_queue(interaction.client, interaction.channel_id))

    @discord.ui.button(label="How to Play", style=discord.ButtonStyle.blurple, emoji="\U0001f5d2", custom_id='persistent_view:how_to_play')
    async def how_to_play_button(self, interaction, button):
        how_to_play_embed = discord.Embed(
            title=":notepad_spiral: How to Play",
            description="",
            colour=0x5865F2
            )

        how_to_play_field1 = (
            "Pick-up games (PUGs) are **competitive**. While anyone is welcome to join, **prior experience is recommended**.\n\n"
            ":dart: **__Overview__**\n"
            "1. First, **`/join`** the queue, but **only if you can play a full PUG** (up to 40 mins)."
            )

        how_to_play_field2 = (
            "2. Matches only start when (usually) 10 players join. **__Don't Ping Queue until then__**."
            )

        how_to_play_field3 = (
            "3. **Join VC on time** and make teams, or lose your spot (10-minute grace period)."
            )

        how_to_play_field4 = (
            "4. Share info (**enemy locations, health** etc.) with your team and work together."
            )

        how_to_play_field5 = (
            "5. **Have fun!** Remember to **`/leave`** when you're finished **so others can play too**.\n\n"
            ":scroll: Use **`/help pug`** for the full list of commands."
            )

        how_to_play_embed.add_field(name="", value=how_to_play_field1, inline=False)
        how_to_play_embed.add_field(name="", value=how_to_play_field2, inline=False)
        how_to_play_embed.add_field(name="", value=how_to_play_field3, inline=False)
        how_to_play_embed.add_field(name="", value=how_to_play_field4, inline=False)
        how_to_play_embed.add_field(name="", value=how_to_play_field5, inline=False)

        await interaction.response.send_message(embed=how_to_play_embed, ephemeral=True)

    @discord.ui.button(label="Actions", style=discord.ButtonStyle.grey, emoji="\U00002728", row=1, custom_id='persistent_view:actions')
    async def actions_button(self, interaction, button):
        more_panel = build_more_panel_embed(interaction.channel_id)
        await interaction.response.send_message(embed=more_panel, view=MoreButtons(), ephemeral=True)

class Pug(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        bot.add_view(MainButtons())

    # Command to open PUG prompt
    @app_commands.command(name="pug", description="Open the PUG panel and view the queue")
    async def pug_command(self, interaction: discord.Interaction):
        main_panel = build_main_panel_embed(interaction.channel_id)
        await interaction.response.send_message(embed=main_panel, view=MainButtons())

        save_panel_message = await interaction.original_response()
        
        panel_message = await interaction.channel.fetch_message(save_panel_message.id)
        panel_messages[interaction.channel_id] = panel_message.id

    # Command to join the queue
    @app_commands.command(name="join", description="Join the PUG queue")
    async def join_command(self, interaction: discord.Interaction):
        queue = get_state(interaction.channel_id)

        added = await queue_add(interaction.user.id, interaction.channel_id)
        if not added:
            await interaction.response.send_message("You are already in the queue.", ephemeral=True)
        else:
            await interaction.response.send_message(
                f"<@{interaction.user.id}> has joined the queue -----> **{len(queue['players'])} player(s) in queue**\n",
                allowed_mentions=discord.AllowedMentions(users=False))

        asyncio.create_task(update_queue(interaction.client, interaction.channel_id))

    # Command to leave the queue
    @app_commands.command(name="leave", description="Leave the PUG queue")
    async def leave_command(self, interaction: discord.Interaction):
        queue = get_state(interaction.channel_id)

        removed = await queue_remove(interaction.user.id, interaction.channel_id)
        if not removed:
            await interaction.response.send_message("You are not in the queue.", ephemeral=True)
        else:
            await interaction.response.send_message(
                f"<@{interaction.user.id}> has left the queue -----> **{len(queue['players'])} player(s) in queue**\n",
                allowed_mentions=discord.AllowedMentions(users=False))

        asyncio.create_task(update_queue(interaction.client, interaction.channel_id))

    # Command to kick a player from the queue
    @app_commands.command(name="remove", description="Remove a player from the PUG queue")
    async def remove_command(self, interaction: discord.Interaction, player: discord.Member):
        queue = get_state(interaction.channel_id)

        removed = await queue_remove(player.id, interaction.channel_id)
        if not removed:
            await interaction.response.send_message("Player is not in the queue.", allowed_mentions=None, ephemeral=True)
            return

        await interaction.response.send_message(
            f"<@{interaction.user.id}> has removed <@{player.id}> from the queue -----> **{len(queue['players'])} player(s) in queue**\n",
            allowed_mentions=discord.AllowedMentions(users=False))

        await player.send(
            f"<@{interaction.user.id}> has removed you from the queue. :door:\n"
            f"> <#{interaction.channel_id}>\n\n")

        asyncio.create_task(update_queue(interaction.client, interaction.channel_id))

async def setup(bot: commands.Bot):
    await bot.add_cog(Pug(bot))
