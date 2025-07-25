import os
import discord
import random
import logging
import importlib
import asyncio
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables including discord token and server ID(s)
load_dotenv()
token = os.getenv('DISCORD_TOKEN')
server = os.getenv('DISCORD_GUILD')

# Log errors/debug info
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

# Create an instance of Intents
intents = discord.Intents.default()
intents.message_content = True

# Define "!" as a command prefix
bot = commands.Bot(command_prefix='!', intents=intents)

# List of Discord roles and corresponding team names/aliases for team selection (Summer Skirmish 2025)
TEAM_ROLES = {"[BONK] Bonkurazu": ["BONK", "Bonkurazu"], 
              "._o< | DuctTales": ["._o<", "DuctTales", "Duck", "Duct"],
              "[EQ] Equinox": ["EQ", "Equinox"],
              "[KOBA] KOBAYASHI CLAN": ["KOBA", "KOBAYASHI CLAN", "KOBAYASHI"],
              "[SAA] SHOCK AND AWE": ["SAA", "SHOCK AND AWE"],
              "=-SLI-= Slightly Less Incompetent": ["SLI", "Slightly Less Incompetent"],
              "[11:59] They Will Eat Earl's Dust": ["11:59", "They Will Eat Earl's Dust", "TWEED"]
              }

# Initialize global state dictionary for map selection
state_handler = {}
timeout_tasks = {}  # Track per-channel timeout tasks

# Set up the timeout logic for the bot

# Timeout counter in seconds
TIMEOUT_DURATION = 72*60*60  # 72 hours

async def timeout_clear(channel_id, interaction):
    await asyncio.sleep(TIMEOUT_DURATION)
    state_handler.pop(channel_id, None)
    timeout_tasks.pop(channel_id, None)
    try:
        await interaction.followup.send(
            f"Map selection has timed out after {TIMEOUT_DURATION/(60*60)} hour(s) of inactivity and has been cleared.")
    except:
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
    if channel_id not in state_handler:
        state_handler[channel_id] = {
            "teams": {"team1": None, "team2": None},
            "coin_toss_winner": None,
            "ban_order": None,
            "bans": {"team1": None, "team2": None},
            "picks": {"team1": None, "team2": None},
            "remaining_maps": {},
            "final_map_pool": {"team1": None, "team2": None},
            "random_map": None
        }
    return state_handler[channel_id]

# Function to resolve map name (checks map names and aliases)
def resolve_map_name(map_name):
    for official_name, aliases in MAP_POOL.items():
        if map_name.lower() == official_name.lower():
            return official_name
        for alias in aliases['aliases']:
            if map_name.lower() == alias.lower():
                return official_name
    return None

# Check if a user has the required perms to bypass team restrictions
def has_admin_privileges(member):
    admin_roles = ["Discord Admin", "Organizer"]
    return any(role.name in admin_roles for role in member.roles)

# Function to resolve team name (checks roles and team aliases)
def resolve_team_name(team_name):
    if team_name == "Mixed Team":
        return "Mixed Team"
    for official_name, aliases in TEAM_ROLES.items():
        if team_name.lower() == official_name.lower() or team_name.lower() in [alias.lower() for alias in aliases]:
            return official_name
    return None

# Function to check if user belongs to a team
def user_is_on_team(member: discord.Member, team_name: str):
    if team_name in ["Mixed Team", "Mixed Team A", "Mixed Team B"]:
        return True # Means that anyone can be on "Mixed Team"
    return any(role.name == team_name for role in member.roles)

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

# Command to clear the selection state
@bot.tree.command(name="clear", description="Clears the map selection state", guild=discord.Object(id=server))
async def clear_command(interaction: discord.Interaction):
    selection_state = get_state(interaction.channel_id)

    state_handler.pop(interaction.channel_id, None)
    await clear_timeout(interaction.channel_id)
    await interaction.response.send_message("Map selection has been cleared. Use `/match` to start again.")

# Command to print commands for bot
@bot.tree.command(name="help", description="List all available commands", guild=discord.Object(id=server))
async def help_command(interaction: discord.Interaction):
    await interaction.response.send_message(
        "## Useful commands\n"
        "- `/help` Displays this list of available commands.\n"
        "- `/clear` Clears the bot and resets the map selection process.\n"
        "- `/match` Begin map selection by inputting two teams and initiate the coin toss.\n"
        "- `/order` Select either \"First\" or \"Second\" to decide your team's ban order.\n"
        "- `/map_ban` Select a map to ban from the remaining Standard map pool.\n"
        "- `/map_pick` Select a map to pick from the remaining __Standard__ map pool or **INVOKE WILDCARD**. Invoking the wildcard will randomly select a map from the remaining __Wildcard__ map pool.\n"
        "- `/map_final` Select either \"Standard\" or \"Wildcard\" to randomly select the final map from either of these map pools.\n"
    )

# Command to start map selection, with team assignment and coin toss
@bot.tree.command(name="match", description="Sets the opposing teams and map pool (optional) for a tournament match", guild=discord.Object(id=server))
@discord.app_commands.describe(team1="Name of team 1", team2="Name of team 2", pool="Name of map pool you want to select from")
async def match_command(interaction: discord.Interaction, team1: str, team2: str, pool: str = "SS25"):
    selection_state = get_state(interaction.channel_id)
    
    resolved_team1 = resolve_team_name(team1)
    resolved_team2 = resolve_team_name(team2)
    
    # Dynamically import dictionary of map pool based on user input
    try:
        tournament = importlib.import_module(pool.lower())
        global MAP_POOL
        MAP_POOL = tournament.MAP_POOL
    except ImportError:
        await interaction.response.send_message(f"ImportError: Could not import the map pool: {pool}.", ephemeral=True)
        return
    except AttributeError:
        await interaction.response.send_message(f"AttributeError: Does not contain a valid map pool.", ephemeral=True)
        return

    if not has_admin_privileges(interaction.user):
        member_roles = [role.name for role in interaction.user.roles]
        user_teams = []
        for team, aliases in TEAM_ROLES.items():
            for role_name in member_roles:
                
                if any(alias.lower() in role_name.lower() for alias in aliases):
                    user_teams.append(team)
                    break
        
        if resolved_team1 not in user_teams and resolved_team2 not in user_teams and "Mixed Team" not in [resolved_team1, resolved_team2]:
            await interaction.response.send_message("You must belong to one of the selected teams. Otherwise, pick \"Mixed Team\".", ephemeral=True)
            return

    if not resolved_team1 or not resolved_team2 or not "Mixed Team":
        await interaction.response.send_message("Team names are not recognized.", ephemeral=True)
        return
    
    if resolved_team1 == resolved_team2:
        resolved_team1 = resolved_team1 + " A"
        resolved_team2 = resolved_team2 + " B"

    await interaction.response.defer()

    # Initialize selection state with assigned teams
    selection_state["teams"] = {"team1": resolved_team1, "team2": resolved_team2}
    selection_state["coin_toss_winner"] = None
    selection_state["ban_order"] = None
    selection_state["bans"] = {"team1": None, "team2": None}
    selection_state["picks"] = {"team1": None, "team2": None}
    selection_state["remaining_maps"] = MAP_POOL.copy()
    selection_state["final_map_pool"] = {"team1": None, "team2": None}
    selection_state["random_map"] = None
    
    # Announce coin toss winner
    selection_state["coin_toss_winner"] = random.choice([resolved_team1, resolved_team2])
    await interaction.followup.send(
        f"**{resolved_team1}** vs **{resolved_team2}**\n\n"
        f"Map selection started! The map pool will be **{pool}**.\n"
        f"Performing a coin toss to determine which team decides the ban order...\n\n"
        f"**{selection_state['coin_toss_winner']}** wins the coin toss! Pick your team's ban order using `/order`.\n"
        "If you ban first, you pick second.")
    
    # Restarts the timeout counter when a command is used on time
    reset_timeout_counter(interaction.channel_id, interaction)

# Show user choice of teams
@match_command.autocomplete('team1')
async def match_team1_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[discord.app_commands.Choice[str]]:
    selection_state = get_state(interaction.channel_id)

    options = ["Mixed Team"] + list(TEAM_ROLES.keys())
    return [
        discord.app_commands.Choice(name=opt, value=opt)
        for opt in options if current.lower() in opt
    ]

@match_command.autocomplete('team2')
async def match_team2_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[discord.app_commands.Choice[str]]:
    selection_state = get_state(interaction.channel_id)

    options = ["Mixed Team"] + list(TEAM_ROLES.keys())
    return [
        discord.app_commands.Choice(name=opt, value=opt)
        for opt in options if current.lower() in opt
    ]

@match_command.autocomplete('pool')
async def match_pool_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[discord.app_commands.Choice[str]]:
    selection_state = get_state(interaction.channel_id)

    options = ["SS25", "WW25"]
    return [
        discord.app_commands.Choice(name=opt, value=opt)
        for opt in options if current.lower() in opt
    ]

# Command for the coin toss winner to pick the ban order
@bot.tree.command(name='order', description='Choose whether your team bans first or second', guild=discord.Object(id=server))
@discord.app_commands.describe(choice="First/Second")
async def order_command(interaction: discord.Interaction, choice: str):
    selection_state = get_state(interaction.channel_id)

    team1 = selection_state["teams"]["team1"]
    team2 = selection_state["teams"]["team2"]

    if selection_state["coin_toss_winner"] is None:
        await interaction.response.send_message("No coin toss winner! Please use `/match` first to select teams.", ephemeral=True)
        return

    if selection_state["ban_order"]:
        await interaction.response.send_message("The ban order has already been decided!", ephemeral=True)
        return

    # Check if user is part of the team that won the coin toss
    if not user_is_on_team(interaction.user, selection_state["coin_toss_winner"]) and not has_admin_privileges(interaction.user):
        await interaction.response.send_message(
            f"Only a member of **{selection_state['coin_toss_winner']}** or an admin/organizer can decide the ban order.",
            ephemeral=True
        )
        return
    
    if choice not in ["First", "Second"]:
        await interaction.response.send_message("Please choose either 'First' or 'Second'.", ephemeral=True)
        return

    if selection_state["coin_toss_winner"] == team1:
        selection_state["ban_order"] = [team1, team2] if choice == "First" else [team2, team1]
    else:
        selection_state["ban_order"] = [team2, team1] if choice == "First" else [team1, team2]

    await interaction.response.send_message(
        f"{selection_state["coin_toss_winner"]} has chosen to ban {choice.lower()}.\n"
        f"**{selection_state['ban_order'][0]}**, please ban a map using `/map_ban`."
    )

    # Restarts the timeout counter when a command is used on time
    reset_timeout_counter(interaction.channel_id, interaction)

# Show user the two options (First or Second)
@order_command.autocomplete('choice')
async def order_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[discord.app_commands.Choice[str]]:
    selection_state = get_state(interaction.channel_id)
    
    options = ["First", "Second"]
    return [
        discord.app_commands.Choice(name=opt, value=opt)
        for opt in options if current.lower() in opt
    ]

# Command for banning maps
@bot.tree.command(name='map_ban', description='Ban a map', guild=discord.Object(id=server))
@discord.app_commands.describe(map="Select a map to ban")
async def map_ban_command(interaction: discord.Interaction, map: str):
    selection_state = get_state(interaction.channel_id)

    team1 = selection_state["teams"]["team1"]
    team2 = selection_state["teams"]["team2"]

    # Validate the ban order
    if not selection_state["ban_order"]:
        await interaction.response.send_message("The ban order hasn't been decided yet! Use `/order` to decide the ban order.", ephemeral=True)
        return
    
    first_to_ban = selection_state["ban_order"][0]
    second_to_ban = selection_state["ban_order"][1]

    team1_ban = selection_state["bans"]["team1"]
    team2_ban = selection_state["bans"]["team2"]

    # Determine the banning team
    banning_team = None

    if not team1_ban and not team2_ban:
        banning_team = first_to_ban
    
    elif team1_ban and not team2_ban:
        banning_team = second_to_ban if team1 == first_to_ban else first_to_ban
    
    elif not team1_ban and team2_ban:
        banning_team = first_to_ban if team1 == first_to_ban else second_to_ban

    if banning_team is None:
        await interaction.response.send_message("You cannot ban any more maps.", ephemeral=True)
        return
    
    # Allow only the current team to ban
    if not user_is_on_team(interaction.user, banning_team) and not has_admin_privileges(interaction.user):
        await interaction.response.send_message(f"Only {banning_team} can ban right now.", ephemeral=True)
        return

    banning_team_key = "team1" if banning_team == team1 else "team2"
    
    if selection_state["bans"][banning_team_key]:
        await interaction.response.send_message(f"{banning_team} has already banned a map!", ephemeral=True)
        return

    standard_maps = [map_key for map_key, map_info in selection_state["remaining_maps"].items() if map_info["map_pool"] == "Standard"]
    banned_map = resolve_map_name(map)

    if not banned_map or banned_map not in standard_maps or banned_map in selection_state["bans"].values():
        await interaction.response.send_message("Please choose a remaining map from the Standard map pool: " + ", ".join(standard_maps))
        return

    selection_state["bans"][f"{banning_team_key}"] = banned_map
    selection_state["remaining_maps"].pop(banned_map)
    
    if not all(selection_state["bans"].values()):
        next_team = second_to_ban if banning_team == first_to_ban else first_to_ban
        await interaction.response.send_message(
            f"{banning_team} has banned: **{banned_map}**\n\n"
            f"**{next_team}**, please ban a map using `/map_ban`.")
    
    elif all(selection_state["bans"].values()):
        picking_team = second_to_ban
        await interaction.response.send_message(
            f"{banning_team} has banned: **{banned_map}**\n\n"
            "Banning phase complete!\n\n"
            f"**{picking_team}**, please begin picking phase by using `/map_pick`.")
    
    # Restarts the timeout counter when a command is used on time
    reset_timeout_counter(interaction.channel_id, interaction)

# Show user the choice of maps to ban
@map_ban_command.autocomplete('map')
async def map_ban_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[discord.app_commands.Choice[str]]:
    selection_state = get_state(interaction.channel_id)

    options = [map_key for map_key, map_info in selection_state["remaining_maps"].items() if map_info["map_pool"] == "Standard"]
    return [
        discord.app_commands.Choice(name=opt, value=opt)
        for opt in options if current.lower() in opt
    ]

# Command for picking maps
@bot.tree.command(name="map_pick", description='Pick a map', guild=discord.Object(id=server))
@discord.app_commands.describe(map="Select a map to pick")
async def map_pick_command(interaction: discord.Interaction, map: str):
    selection_state = get_state(interaction.channel_id)

    team1 = selection_state["teams"]["team1"]
    team2 = selection_state["teams"]["team2"]

    if not all(selection_state["bans"].values()):
        await interaction.response.send_message("Teams must complete the banning phase first.", ephemeral=True)
        return
    
    first_to_ban = selection_state["ban_order"][0]
    second_to_ban = selection_state["ban_order"][1]

    team1_ban = selection_state["bans"]["team1"]
    team2_ban = selection_state["bans"]["team2"]
    
    # If a map hasn't been picked yet by either team, the team that banned second will pick a map first
    # Determine who picks first
    if not any(selection_state["picks"].values()):
        picking_team = second_to_ban
    else:
        picking_team = first_to_ban

    # Allow only the current team to ban
    if not user_is_on_team(interaction.user, picking_team) and not has_admin_privileges(interaction.user):
        await interaction.response.send_message(f"Only {picking_team} can pick a map right now.", ephemeral=True)
        return

    team_key = "team1" if picking_team == team1 else "team2"
    
    if "INVOKE WILDCARD" not in map:
        picked_map = resolve_map_name(map)
        standard_maps = [map_key for map_key, map_info in selection_state["remaining_maps"].items() if map_info["map_pool"] == "Standard"]
        
        if not picked_map or picked_map not in standard_maps:
            await interaction.response.send_message("Please choose a remaining map from the pool: " + ", ".join(selection_state["remaining_maps"].keys()))
            return

    elif "INVOKE WILDCARD" in map:
        wildcard_maps = [map_key for map_key, map_info in selection_state["remaining_maps"].items() if map_info["map_pool"] == "Wildcard"]
        picked_map = random.choice(wildcard_maps)

    # Prevent a team from picking twice
    if selection_state["picks"][team_key]:
        await interaction.response.send_message(
            f"{picking_team} has already picked a map: **{selection_state['picks'][team_key]}**. You cannot pick again.",
            ephemeral=True
        )
        return

    # Once map is validated, it is saved as a map pick and removed from the remaining map pool
    selection_state["picks"][team_key] = picked_map
    selection_state["remaining_maps"].pop(picked_map)

    if not all(selection_state["picks"].values()):
        next_team = first_to_ban if picking_team == second_to_ban else second_to_ban
        await interaction.response.send_message(
            f"{picking_team} has picked: **{picked_map}**\n\n"
            f"**{next_team}**, please pick a map using `/map_pick`.")
        
    if all(selection_state["picks"].values()):
        await interaction.response.send_message(
            f"{picking_team} has picked: **{picked_map}**\n\n"
            "Picking phase complete!\n\n")
        await interaction.followup.send(
            "The final map will be randomly selected from either the Standard or Wildcard map pool.\n\n"
            f"**{team1}** and **{team2}** can finalize the map selection process by using `/map_final`.\n\n"
            "-# To invoke the Wildcard, both teams must agree. Otherwise, the selection will default to the Standard map pool.")
    
    # Restarts the timeout counter when a command is used on time
    reset_timeout_counter(interaction.channel_id, interaction)

# Show user the choice of maps to pick
@map_pick_command.autocomplete('map')
async def map_pick_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[discord.app_commands.Choice[str]]:
    selection_state = get_state(interaction.channel_id)

    options = [map_key for map_key, map_info in selection_state["remaining_maps"].items() if map_info["map_pool"] == "Standard"] + ["INVOKE WILDCARD"]
    return [
        discord.app_commands.Choice(name=opt, value=opt)
        for opt in options if current.lower() in opt
    ]

# Command for picking maps
@bot.tree.command(name="map_final", description='Choose whether the final map is from the Standard or Wildcard map pool', guild=discord.Object(id=server))
@discord.app_commands.describe(choice="Standard/Wildcard")
async def map_final_command(interaction: discord.Interaction, choice: str):
    selection_state = get_state(interaction.channel_id)

    team1 = selection_state["teams"]["team1"]
    team2 = selection_state["teams"]["team2"]

    # Allow only the opposing teams to use the command
    if not(
        user_is_on_team(interaction.user, team1) or
        user_is_on_team(interaction.user, team2)
    ) and not has_admin_privileges(interaction.user):
        await interaction.response.send_message("You must belong to one of the opposing teams.", ephemeral=True)
        return
    
    if not all(selection_state["bans"].values()):
        await interaction.response.send_message("Teams must complete the banning phase first.", ephemeral=True)
        return
    
    first_to_ban = selection_state["ban_order"][0]
    second_to_ban = selection_state["ban_order"][1]

    team1_ban = selection_state["bans"]["team1"]
    team2_ban = selection_state["bans"]["team2"]
    
    if not all(selection_state["picks"].values()):
        await interaction.response.send_message("Teams must complete the picking phase first.", ephemeral=True)
        return
    
    team1_pick = selection_state["picks"]["team1"]
    team2_pick = selection_state["picks"]["team2"]
    
    choice = choice.capitalize()
    
    if choice not in ["Standard", "Wildcard"]:
        await interaction.response.send_message("Please choose either 'Standard' or 'Wildcard'.", ephemeral=True)
        return
    
    # Assign the selected choice of map pool to each team
    choosing_team_key = "team1" if user_is_on_team(interaction.user, team1) else "team2"
    non_choosing_team_key = "team2" if user_is_on_team(interaction.user, team1) else "team1"
    selection_state["final_map_pool"][choosing_team_key] = choice
    
    if selection_state["final_map_pool"]["team1"] and selection_state["final_map_pool"]["team2"]:

        agreed_pool = "Wildcard" if selection_state["final_map_pool"]["team1"] == selection_state["final_map_pool"]["team2"] == "Wildcard" else "Standard"

        # Pull the remaining maps in the selected map pool
        final_maps = [
            map_key for map_key, map_info in selection_state["remaining_maps"].items()
            if map_info["map_pool"] == agreed_pool
            ]
        
        if not final_maps:
            await interaction.response.send_message(
                f"No maps left in the {agreed_pool} map pool to choose from!", ephemeral=True
            )
            return
    
        selection_state["random_map"] = random.choice(final_maps)

        await interaction.response.send_message(
            f"The final map will be from the __{agreed_pool}__ map pool!\n"
            f"Randomly selecting the final map...\n\n"
            f"The final map is: **{selection_state['random_map']}**")
        
        # Confirm match details in an embed
        embed = discord.Embed(
        title=f"{team1} vs {team2}",
        description=":white_check_mark: Match is ready to go!",
        colour=discord.Colour.from_rgb(252, 155, 40)
        )

        # Add fields to the embed for picks...
        first_map = team1_pick if team1 == second_to_ban else team2_pick
        second_map = team2_pick if team2 == first_to_ban else team1_pick
        third_map = selection_state["random_map"]

        embed_maps = (
            f"1. {first_map} ({second_to_ban} pick)\n"
            f"2. {second_map} ({first_to_ban} pick)\n"
            f"3. {third_map} (Random pick)"
            )

        embed.add_field(name="Maps", value=embed_maps, inline=False)

        # ...and bans
        embed.add_field(name=f"{team1} Ban", value=team1_ban, inline=True)
        embed.add_field(name=f"{team2} Ban", value=team2_ban, inline=True)

        await interaction.followup.send(embed=embed)

        state_handler.pop(interaction.channel_id, None)

    else:
        await interaction.response.send_message(
            f"{selection_state['teams'][choosing_team_key]} wants to play a map from the __{choice}__ map pool.\n"
            f"Waiting for **{selection_state['teams'][non_choosing_team_key]}** to submit their preference."
        )
    
    # Restarts the timeout counter when a command is used on time
    reset_timeout_counter(interaction.channel_id, interaction)

# Show user the choice of maps to pick
@map_final_command.autocomplete('choice')
async def map_final_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[discord.app_commands.Choice[str]]:
    selection_state = get_state(interaction.channel_id)
    
    options = ["Standard","Wildcard"]
    return [
        discord.app_commands.Choice(name=opt, value=opt)
        for opt in options if current.lower() in opt
    ]

# Run the bot with the token
bot.run(token, log_handler=handler, log_level=logging.DEBUG)
