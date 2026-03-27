import asyncio
import importlib
import logging
from logging.handlers import TimedRotatingFileHandler
import os
import pkgutil
import random
from datetime import datetime

from dotenv import load_dotenv
import discord
from discord.ext import commands

# Load environment variables including discord token and server ID(s)
load_dotenv()
token = os.getenv('DISCORD_TOKEN')
server = int(os.getenv('DISCORD_GUILD'))

# Create an instance of Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Define "!" as a command prefix
bot = commands.Bot(command_prefix='!', intents=intents)

# Initialize global state dictionary for map selection
queue_handler = {}
timeout_tasks = {}  # Track per-channel timeout tasks

# Set up the timeout logic for the bot
TIMEOUT_DURATION = 3*60*60  # 3 hours

async def timeout_clear(channel_id, interaction):
    try:
        await asyncio.sleep(TIMEOUT_DURATION)

        queue_handler.pop(channel_id, None)
        timeout_tasks.pop(channel_id, None)
        await interaction.followup.send(
            f"Pug queue has timed out after {TIMEOUT_DURATION/(60*60)} hour(s) of inactivity and has been cleared.")

    except asyncio.CancelledError:
        pass

# Function to reset the timeout counter
def reset_timeout_counter(channel_id, interaction):
    if channel_id in timeout_tasks:
        timeout_tasks[channel_id].cancel()
    task = asyncio.create_task(timeout_clear(channel_id, interaction))
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
            "players": [],
            "player_count": 0
        }
    return queue_handler[channel_id]

# Printing channel messages on event
panel_messages = {}

# Function to build pug embed
def build_main_panel_embed(channel_id: int):
    queue = get_state(channel_id)

    description=("Join the queue to play!\n\n"
                 "**Competitive rules apply**. Click the **Guide** button for more info.")

    embed = discord.Embed(
        title="Competitive PUG Queue!",
        description=description
    )

    embed.add_field(name="", value="\u00AD", inline=False)

    if not queue['players']:
        embed.add_field(name="Player Queue", value="Queue is empty.", inline=False)
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

async def refresh_panel(channel_id: int):
    if channel_id not in panel_messages:
        return  # No panel in this channel yet

    panel_message = panel_messages[channel_id]
    embed = build_main_panel_embed(channel_id)

    await panel_message.edit(embed=embed, view=MainButtons())

def build_more_panel_embed(channel_id: int):

    embed = discord.Embed(
        title="Additional Actions",
        description="**The (optional) buttons below may help you start your match**"
    )

    embed.set_footer(text="Created by Muffin-Dono")

    return embed

async def join_queue(user_id: int, channel_id: int):
    queue = get_state(channel_id)

    if user_id in queue['players']:
        return False

    queue['players'].append(user_id)
    return True

async def leave_queue(user_id: int, channel_id: int):
    queue = get_state(channel_id)

    if user_id not in queue['players']:
        return False

    queue['players'].remove(user_id)
    return True

# Ensure bot is ready
@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")
    try:
        # Force sync to servers
        GUILD = discord.Object(id=server)
        synced = await bot.tree.sync(guild=GUILD)
        print(f"Synced {len(synced)} commands to guild {GUILD.id}.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

# Command to join the queue
@bot.tree.command(name="join", description="Join the PUG queue", guild=discord.Object(id=server))
async def join_command(interaction: discord.Interaction):
    queue = get_state(interaction.channel_id)

    added = await join_queue(interaction.user.id, interaction.channel_id)
    if not added:
        await interaction.response.send_message("You are already in the queue.", ephemeral=True)
    else:
        await interaction.response.send_message(
            f"<@{interaction.user.id}> has joined the queue -----> **{len(queue['players'])} player(s) in queue**\n",
            allowed_mentions=discord.AllowedMentions(users=False))

    # Refresh the panel
    await refresh_panel(interaction.channel_id)

    # Restarts the timeout counter when a command is used on time
    reset_timeout_counter(interaction.channel_id, interaction)

# Command to leave the queue
@bot.tree.command(name="leave", description="Leave the PUG queue", guild=discord.Object(id=server))
async def leave_command(interaction: discord.Interaction):
    queue = get_state(interaction.channel_id)

    removed = await leave_queue(interaction.user.id, interaction.channel_id)
    if not removed:
        await interaction.response.send_message("You are not in the queue.", ephemeral=True)
    else:
        await interaction.response.send_message(
            f"<@{interaction.user.id}> has left the queue -----> **{len(queue['players'])} player(s) in queue**\n",
            allowed_mentions=discord.AllowedMentions(users=False))

    # Refresh the panel
    await refresh_panel(interaction.channel_id)

    # Restarts the timeout counter when a command is used on time
    reset_timeout_counter(interaction.channel_id, interaction)

class ButtonOnCooldown(commands.CommandError):
    pass
def key(interaction: discord.Interaction):
    return "global"

class MoreButtons(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.ping_cd = commands.CooldownMapping.from_cooldown(1, 600, key) # 10 minutes

    @discord.ui.button(label="Ping Queue", style=discord.ButtonStyle.red, emoji="\U0001f514")
    async def ping_queue_button(self, interaction, button):
        retry_after = self.ping_cd.update_rate_limit(interaction)
        if retry_after:
            minutes = int(retry_after // 60)
            await interaction.response.send_message(f"Ping is on cooldown. Try again in {minutes} minutes.", ephemeral=True)
            return
        
        queue = get_state(interaction.channel_id)

        if not queue['players']:
            await interaction.response.send_message("Queue is empty.", ephemeral=True)
            return

        if interaction.user.id not in queue['players']:
            await interaction.response.send_message("Only queued players may ping the queue.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        for user_id in queue['players'][:10]:
            player = interaction.guild.get_member(user_id)

            await player.send(f"<@{interaction.user.id}> has pinged everyone in the queue! :bell:\n\n"
                "Gather in VC and make teams! :sound:"
                , allowed_mentions=discord.AllowedMentions(users=False))
            
            await interaction.followup.send(f"**<@{interaction.user.id}> has pinged everyone in the queue!**"
                                            , allowed_mentions=discord.AllowedMentions(users=False))

    @discord.ui.button(label="Map Vote", style=discord.ButtonStyle.blurple)
    async def map_vote_button(self, interaction, button):
        await interaction.response.send_message("Map vote coming soon:tm:", ephemeral=True)

    @discord.ui.button(label="Scramble", style=discord.ButtonStyle.blurple)
    async def scramble_button(self, interaction, button):
        await interaction.response.send_message("Scramble coming soon:tm:", ephemeral=True)

# Main set of buttons, for joining/leaving queue and guide
class MainButtons(discord.ui.View):
    @discord.ui.button(label="Join Queue", style=discord.ButtonStyle.green, emoji="\U0000270b")
    async def join_button(self, interaction, button):
        queue = get_state(interaction.channel_id)

        added = await join_queue(interaction.user.id, interaction.channel_id)
        if not added:
            await interaction.response.send_message("You are already in the queue.", ephemeral=True)
            return

        panel = build_main_panel_embed(interaction.channel_id)
        await interaction.response.edit_message(embed=panel, view=self)

        await interaction.followup.send(
            f"<@{interaction.user.id}> has joined the queue -----> **{len(queue['players'])} player(s) in queue**\n",
            allowed_mentions=discord.AllowedMentions(users=False))

    @discord.ui.button(label="Leave Queue", style=discord.ButtonStyle.red, emoji="\U0001f44b")
    async def leave_button(self, interaction, button):
        queue = get_state(interaction.channel_id)

        removed = await leave_queue(interaction.user.id, interaction.channel_id)
        if not removed:
            await interaction.response.send_message("You are not in the queue.", ephemeral=True)
            return

        panel = build_main_panel_embed(interaction.channel_id)
        await interaction.response.edit_message(embed=panel, view=self)

        await interaction.followup.send(
            f"<@{interaction.user.id}> has left the queue -----> **{len(queue['players'])} player(s) in queue**\n",
            allowed_mentions=discord.AllowedMentions(users=False))

    @discord.ui.button(label="Guide", style=discord.ButtonStyle.blurple, emoji="\U0001f5d2")
    async def guide_button(self, interaction, button):
        await interaction.response.send_message(
            "Use this bot to organize **semi-competitive** pick-up games (PUGs)!\n\n"
            "1. You can join or leave the queue for PUGs through this bot. Join the queue by clicking \"**Join Queue**\" or by typing `/join`.\n\n"
            "2. Please **only join the queue if you can play a full PUG**, which may last up to 40 minutes. Remember to `/leave` once you're finished playing.\n\n"
            "3. The bot will DM you when enough players (usually 5v5) join - please **assemble in the voice chat and start picking teams**.\n\n"
            "4. **You must join the VC on time**. Otherwise, you risk losing your spot after a 10-minute grace period.\n\n"
            "5. Please **follow good comms etiquette in your team VC**. Try your best to provide info to your team, such as enemy locations."
            , ephemeral=True
        )

    @discord.ui.button(label="Actions", style=discord.ButtonStyle.grey, emoji="\U00002728", row=1)
    async def actions_button(self, interaction, button):
        more_panel = build_more_panel_embed(interaction.channel_id)
        await interaction.response.send_message(embed=more_panel, view=MoreButtons(), ephemeral=True)

# Command to open PUG prompt
@bot.tree.command(name="pug", description="Open the PUG panel and view the queue", guild=discord.Object(id=server))
async def pug_command(interaction: discord.Interaction):
    main_panel = build_main_panel_embed(interaction.channel_id)
    await interaction.response.send_message(embed=main_panel, view=MainButtons())

    panel_message = await interaction.original_response()

    panel_messages[interaction.channel_id] = panel_message

# Command to kick a player from the queue
@bot.tree.command(name="remove", description="Remove a player from the PUG queue", guild=discord.Object(id=server))
async def remove_command(interaction: discord.Interaction, player: discord.Member):
    queue = get_state(interaction.channel_id)

    if player.id not in queue['players']:
        await interaction.response.send_message(
            "Player is not in the queue.",
            allowed_mentions=None, ephemeral=True)
        return

    queue['players'].remove(player.id)

    await interaction.response.send_message(
        f"<@{interaction.user.id}> has removed <@{player.id}> from the queue -----> **{len(queue['players'])} player(s) in queue**\n",
        allowed_mentions=discord.AllowedMentions(users=False))

    # Refresh the panel
    await refresh_panel(interaction.channel_id)

    await player.send(f"<@{interaction.user.id}> has removed you from the queue.")

    # Restarts the timeout counter when a command is used on time
    reset_timeout_counter(interaction.channel_id, interaction)

# Run the bot with the token
bot.run(token)
