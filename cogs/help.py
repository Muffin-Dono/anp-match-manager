import logging

import discord
from discord.ext import commands
from discord import app_commands

log = logging.getLogger(__name__)

# Help for tournament map selection and pug queue
class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    help_group = app_commands.Group(
        name="help",
        description="Help commands"
    )

    @help_group.command(name="pug", description="Help options for PUG queue")
    async def help_pug(self, interaction: discord.Interaction):
        pug_embed = discord.Embed(title="**PUG Queue Help**", color=0x2F3136)

        pug_embed_field = (
            "Pick-up games (PUGs) are **competitive**. Although anyone can join, it is **recommended** that you have some experience playing the game before jumping in.\n\n"
            "**Useful Commands**\n"
            "- **`/pug`** - Opens the panel for the PUG queue.\n"
            "- **`/join`** - Join the PUG queue.\n"
            "- **`/leave`** - Leave the PUG queue.\n"
            "- **`/remove`** - Remove a player from the PUG queue.\n\n"
            "**PUG Panel Actions Menu**\n"
            "- **Ping Queue** - DM players in queue - ONLY when enough (usually 10) have joined!\n"
            "- **Map Vote** - Initiate map voting for PUG. Coming soon:tm:.\n"
            "- **Scramble** - Scramble the queued players into two teams. Coming soon:tm:.")
        pug_embed.add_field(name="", value=pug_embed_field, inline=False)

        pug_embed.set_footer(text="Created by Muffin-Dono")

        await interaction.response.send_message(embed=pug_embed)
    
    @help_group.command(name="tourney", description="Help options for tournament map selection")
    async def help_tourney(self, interaction: discord.Interaction):
        tourney_embed = discord.Embed(title="**Tournament Map Selection Help**", color=0x2F3136)

        tourney_embed_field = (
            "- **`/clear`** - Clears the bot and resets the map selection process.\n\n"
            "**Selecting Maps for your Match**\n"
            "1. **`/match`** - Begin map selection by inputting two teams and initiate the coin toss.\n"
            "2. **`/order`** - Decide your team's pick and ban order.\n"
            "3. **`/map_ban`** - Select a map to ban from the map pool.\n"
            "4. **`/map_pick`** - Select a map to pick from the map pool. In some tournaments, you can also select from a wildcard map pool.\n"
            "5. **`/map_final`** (optional) - Randomly select the final map from the map pool of choice.\n\n"
            "**The bot can load other tournaments not listed by the `/match` command**.\n"
            "Simply input its name (e.g. \"WW25\") when using the command.")
        tourney_embed.add_field(name="", value=tourney_embed_field, inline=False)

        tourney_embed.set_footer(text="Created by Muffin-Dono")

        await interaction.response.send_message(embed=tourney_embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Help(bot))