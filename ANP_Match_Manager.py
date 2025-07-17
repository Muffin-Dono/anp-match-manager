
# This is the ANP Match Manager bot for Discord which helps players pick/ban maps for a match
# It has been written specifically for Summer Skirmish 2025 - map selection process may differ to other tournaments
# Future - allow mirror matches?

import os
import discord
import random
import logging
import importlib
from discord.ext import commands
from dotenv import load_dotenv

# Fetch token
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

# Log errors/debug info
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

# Create an instance of Intents
intents = discord.Intents.default()
intents.message_content = True  # This is required for reading message content

# Define "!" as a command prefix
bot = commands.Bot(command_prefix='!', intents=intents)

# List of Discord roles and corresponding team names (and their aliases) for team selection (Summer Skirmish 2025)
TEAM_ROLES = {"[BONK] Bonkurazu": ["BONK", "Bonkurazu"], 
              "._o< | DuctTales": ["._o<", "Duck", "Duct"],
              "[EQ] Equinox": ["EQ", "Equinox"],
              "[KOBA] KOBAYASHI CLAN": ["KOBA", "KOBAYASHI", "KOBAYASHI CLAN"],
              "[SAA] SHOCK AND AWE": ["SAA", "SHOCK AND AWE"],
              "=-SLI-= Slightly Less Incompetent": ["SLI", "Slightly Less Incompetent"],
              "[11:59] They Will Eat Earl's Dust": ["11:59", "They Will Eat Earl's Dust", "TWEED"]
              }

# Function to resolve map name (checks map names and aliases)
def resolve_map_name(map_name):
    for official_name, aliases in MAP_POOL.items():
        if map_name.lower() == official_name.lower():
            return official_name
        for alias in aliases['aliases']:
            if map_name.lower() == alias.lower():
                return official_name
    return None

# Check if a user has the required roles
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
    if team_name == "Mixed Team":
        return True # Means that anyone can be on "Mixed Team"
    return any(role.name == team_name for role in member.roles)

# Store state for map selection
selection_state = {
    "teams": {"team1": None, "team2": None},
    "coin_toss_winner": None,
    "ban_order": None,
    "bans": {"team1": None, "team2": None},
    "picks": {"team1": None, "team2": None},
    "remaining_maps": {},
    "final_map_pool": {"team1": None, "team2": None},
    "random_map": None
}

# Ensure bot is ready
@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")

# Command to clear the selection state
@bot.tree.command(name="clear", description="Clears the map selection state.")
async def clear_command(interaction: discord.Interaction):
    global selection_state
    selection_state = {
        "teams": {"team1": None, "team2": None},
        "coin_toss_winner": None,
        "ban_order": None,
        "bans": {"team1": None, "team2": None},
        "picks": {"team1": None, "team2": None},
        "remaining_maps": {},
        "final_map_pool": {"team1": None, "team2": None},
        "random_map": None
    }
    await interaction.response.send_message("Map selection has been cleared. Use `/match` to start a new match.")

# Command to start map selection, with team assignment and coin toss
@bot.tree.command(name="match", description="Sets the opposing teams and map pool (optional) for the match")
@discord.app_commands.describe(team1="Name of team 1", team2="Name of team 2", pool="Name of map pool you want to select from")
async def match_command(interaction: discord.Interaction, team1: str, team2: str, pool: str = "ss25"):
    global selection_state
    resolved_team1 = resolve_team_name(team1)
    resolved_team2 = resolve_team_name(team2)
    
    # Dynamically import dictionary of map pool based on user input
    try:
        tournament = importlib.import_module(pool)
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
        await interaction.response.send_message("Unable to matchup duplicate teams. Please try again with different teams.", ephemeral=True)

    await interaction.response.defer()

    # Initialize match state
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
        f"Map selection started! The map pool will be **{pool.upper()}**.\n"
        f"Performing a coin toss to determine which team decides the ban order...\n\n"
        f"**{selection_state['coin_toss_winner']}** wins the coin toss! Pick your team's ban order using `/order`.")

# Show user choice of teams
@match_command.autocomplete('team1')
async def match_team1_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[discord.app_commands.Choice[str]]:
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
    options = ["ss25", "ww25"]
    return [
        discord.app_commands.Choice(name=opt, value=opt)
        for opt in options if current.lower() in opt
    ]

# Command for the coin toss winner to pick the ban order
@bot.tree.command(name='order', description='Choose whether your team bans first or second.')
@discord.app_commands.describe(choice="First/Second")
async def order_command(interaction: discord.Interaction, choice: str):
    global selection_state

    if selection_state["coin_toss_winner"] is None:
        await interaction.response.send_message("No coin toss winner! Please use `/match` to start the process.", ephemeral=True)
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

    if selection_state["coin_toss_winner"] == selection_state["teams"]["team1"]:
        selection_state["ban_order"] = [selection_state["teams"]["team1"], selection_state["teams"]["team2"]] if choice == "First" else [selection_state["teams"]["team2"], selection_state["teams"]["team1"]]
    else:
        selection_state["ban_order"] = [selection_state["teams"]["team2"], selection_state["teams"]["team1"]] if choice == "First" else [selection_state["teams"]["team1"], selection_state["teams"]["team2"]]

    await interaction.response.send_message(
        f"**{selection_state['ban_order'][0]}** will ban first.\n"
        f"Please ban a map using the command `/map_ban`."
    )

# Show user the two options (First or Second)
@order_command.autocomplete('choice')
async def order_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[discord.app_commands.Choice[str]]:
    options = ["First", "Second"]
    return [
        discord.app_commands.Choice(name=opt, value=opt)
        for opt in options if current.lower() in opt
    ]

# Command for banning maps
@bot.tree.command(name='map_ban', description='Ban a map')
@discord.app_commands.describe(map="Select a map to ban")
async def map_ban_command(interaction: discord.Interaction, map: str):
    global selection_state

    # Validate the ban order
    if not selection_state["ban_order"]:
        await interaction.response.send_message("The ban order hasn't been decided yet! Use `/order` to decide the ban order.", ephemeral=True)
        return

    if not selection_state["bans"]["team1"] and not selection_state["bans"]["team2"]:
        banning_team = selection_state["ban_order"][0]
    
    elif selection_state["bans"]["team1"] and not selection_state["bans"]["team2"] and selection_state["teams"]["team1"] == selection_state["ban_order"][0]:
        banning_team = selection_state["ban_order"][1]

    # Allow only the current team to ban
    elif not user_is_on_team(interaction.user, banning_team) and not has_admin_privileges(interaction.user):
        await interaction.response.send_message(f"Only {banning_team} can ban right now.", ephemeral=True)
        return
    
    else:
        await interaction.response.send_message("You cannot ban any more maps.", ephemeral=True)
        return

    banning_team_key = "team1" if banning_team == selection_state["teams"]["team1"] else "team2"
    
    if selection_state["bans"][banning_team_key]:
        await interaction.response.send_message(f"{banning_team} has already banned a map!", ephemeral=True)
        return

    standard_maps = [map_key for map_key, map_info in selection_state["remaining_maps"].items() if map_info["map_pool"] == "Standard"]
    banned_map = resolve_map_name(map)

    if not banned_map or banned_map not in standard_maps or banned_map in selection_state["bans"].values():
        await interaction.response.send_message("Please choose a remaining map from the pool: " + ", ".join(standard_maps))
        return

    selection_state["bans"][f"{banning_team_key}"] = banned_map
    selection_state["remaining_maps"].pop(banned_map)
    
    if not all(selection_state["bans"].values()):
        next_team = selection_state["ban_order"][1] if banning_team == selection_state["ban_order"][0] else selection_state["ban_order"][0]
        await interaction.response.send_message(
            f"{banning_team} has banned: **{banned_map}**\n\n"
            f"**{next_team}**, please ban a map using `/map_ban`.")
    
    elif all(selection_state["bans"].values()):
        picking_team = selection_state["ban_order"][1]
        await interaction.response.send_message(
            f"{banning_team} has banned: **{banned_map}**\n\n"
            "Banning phase complete!\n\n"
            f"{picking_team}, please begin picking phase by using `/map_pick`.")

# Show user the choice of maps to ban
@map_ban_command.autocomplete('map')
async def map_ban_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[discord.app_commands.Choice[str]]:
    options = [map_key for map_key, map_info in selection_state["remaining_maps"].items() if map_info["map_pool"] == "Standard"]
    return [
        discord.app_commands.Choice(name=opt, value=opt)
        for opt in options if current.lower() in opt
    ]

# Command for picking maps
@bot.tree.command(name="map_pick", description='Pick a map')
@discord.app_commands.describe(map="Select a map to pick")
async def map_pick_command(interaction: discord.Interaction, map: str):
    global selection_state

    if not all(selection_state["bans"].values()):
        await interaction.response.send_message("Teams must complete the banning phase first.", ephemeral=True)
        return
    
    # If a map hasn't been picked yet by either team, the team that banned second will pick a map first
    # Determine who picks first
    if not any(selection_state["picks"].values()):
        picking_team = selection_state["ban_order"][1]
    else:
        picking_team = selection_state["ban_order"][0]
    
    # Allow only the current team to ban
    if not user_is_on_team(interaction.user, picking_team) and not has_admin_privileges(interaction.user):
        await interaction.response.send_message(f"Only {picking_team} can pick a map right now.", ephemeral=True)
        return

    team_key = "team1" if picking_team == selection_state["teams"]["team1"] else "team2"
    
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
        next_team = selection_state["ban_order"][0] if picking_team == selection_state["ban_order"][1] else selection_state["ban_order"][1]
        await interaction.response.send_message(
            f"{picking_team} has picked: **{picked_map}**\n\n"
            f"**{next_team}**, please pick a map using `/map_pick`.")
        
    if all(selection_state["picks"].values()):
        await interaction.response.send_message(
            f"{picking_team} has picked: **{picked_map}**\n\n"
            "Picking phase complete!\n\n")
        await interaction.followup.send(
            "The final map will be randomly selected from either the Standard or Wildcard map pool. If both teams do not agree to invoke the Wildcard, the selection will default to the Standard map pool.\n\n"
            "Both teams can complete the map selection process by using `/map_final`.")

# Show user the choice of maps to pick
@map_pick_command.autocomplete('map')
async def map_pick_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[discord.app_commands.Choice[str]]:
    options = [map_key for map_key, map_info in selection_state["remaining_maps"].items() if map_info["map_pool"] == "Standard"] + ["INVOKE WILDCARD"]
    return [
        discord.app_commands.Choice(name=opt, value=opt)
        for opt in options if current.lower() in opt
    ]

# Command for picking maps
@bot.tree.command(name="map_final", description='Choose whether the final map is from the Standard or Wildcard map pool.')
@discord.app_commands.describe(choice="Standard/Wildcard")
async def map_final_command(interaction: discord.Interaction, choice: str):

    # Allow only the opposing teams to use the command
    if not(
        user_is_on_team(interaction.user, selection_state["teams"]["team1"]) or
        user_is_on_team(interaction.user, selection_state["teams"]["team2"])
    ) and not has_admin_privileges(interaction.user):
        await interaction.response.send_message("You must belong to one of the opposing teams.", ephemeral=True)
        return
    
    if not all(selection_state["bans"].values()):
        await interaction.response.send_message("Teams must complete the banning phase first.", ephemeral=True)
        return
    
    if not all(selection_state["picks"].values()):
        await interaction.response.send_message("Teams must complete the picking phase first.", ephemeral=True)
        return
    
    choice = choice.capitalize()
    
    if choice not in ["Standard", "Wildcard"]:
        await interaction.response.send_message("Please choose either 'Standard' or 'Wildcard'.", ephemeral=True)
        return
    
    # Assign the selected choice of map pool to each team
    team_key = "team1" if user_is_on_team(interaction.user, selection_state["teams"]["team1"]) else "team2"
    selection_state["final_map_pool"][team_key] = choice
    
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
            f"Map pool will be {agreed_pool}!"
            f"Randomly selecting the final map from the {agreed_pool} map pool...\n"
            f"The final map is: {selection_state['random_map']}")
        
        # Confirm match details in an embed
        embed = discord.Embed(
        title=f"{selection_state["teams"]["team1"]} vs {selection_state["teams"]["team2"]}",
        description=":white_check_mark: Match is ready to go!",
        colour=discord.Colour.from_rgb(252, 155, 40)
        )

        # Add fields to the embed for picks...
        first_map = selection_state["picks"]["team1"] if selection_state["teams"]["team1"] == selection_state["ban_order"][1] else selection_state["picks"]["team2"]
        second_map = selection_state["picks"]["team2"] if selection_state["teams"]["team2"] == selection_state["ban_order"][0] else selection_state["picks"]["team1"]
        third_map = selection_state["random_map"]

        embed_maps = f"{first_map}\n{second_map}\n{third_map}"

        embed.add_field(name="", value=embed_maps, inline=False)

        # ...and bans
        embed.add_field(name=f"{selection_state['teams']['team1']} Ban", value=selection_state["bans"]["team1"], inline=True)
        embed.add_field(name=f"{selection_state['teams']['team2']} Ban", value=selection_state["bans"]["team2"], inline=True)

        await interaction.followup.send(embed=embed)

    else:
        await interaction.response.send_message(
            f"Your team has chosen the **{choice}** map pool.\n"
            "Waiting for the other team to submit their preference.",
            ephemeral=True
        )

# Show user the choice of maps to pick
@map_final_command.autocomplete('choice')
async def map_final_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[discord.app_commands.Choice[str]]:
    options = ["Standard","Wildcard"]
    return [
        discord.app_commands.Choice(name=opt, value=opt)
        for opt in options if current.lower() in opt
    ]

# Run the bot with the token
bot.run(token, log_handler=handler, log_level=logging.DEBUG)
