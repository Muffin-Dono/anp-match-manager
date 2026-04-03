# ANP Match Manager
ANP Match Manager is a Discord bot that supports two major functions for competition:
- Tournament map selection for matches
- Pick-up game (PUG) queue management

Although the bot was initially built to organize competition in the video game **NEOTOKYO°**, it is planned to eventually support a wider range of games, map pools, and tournament formats.

## Tournament Map Selection

The bot is designed for competitive environments where teams and players already have roles in the server, and where map pools may change between tournaments. The number of maps you can ban or pick, as well as the order in which you do so, may vary depending on the tournament.

> [!IMPORTANT]
> The current version of the bot assumes that each team bans one map and picks one map for each matchup.

The tournament map selection process is as follows:
1. First, two opposing teams register themselves and initiate a coin toss.
2. The team that wins the coin toss will determine which team will ban first in the banning phase.
3. For the banning phase, each team bans one map.
4. For the picking phase, each team picks one map (but team order is reversed for this phase!).
5. Finally, the third map is randomly selected by the bot.
   - Optional - only available if a Wildcard map pool is present in the tournament.
   - From **Standard** by default, from **Wildcard** if both teams agree.

---

## PUG Queue

The PUG queue system is simple and designed to have all the essential features available in a single embed, the **PUG Panel**. More features are planned for the future and these will be available from the "Actions" button.

Players can currently:
- Join and leave a queue
- See who is currently queued
- Ping the queue (with cooldown) when enough players are ready
- Receive a DM notification to gather in voice and form teams
- Expand the PUG Panel with the Actions button to access bonus options

**PUG Panel Actions Button Menu**
- **Ping Queue**
  - DM players in the queue.
- **Map Vote** - Planned (tentative)
  - Start a map vote for the PUG.
- **Scramble** - Planned (tentative)
  - Randomize queued players into two teams.

---

## Useful commands

### Help
- **`/help pug`** Help options for PUG queue
- **`/help tourney`** Help options for Tournament map selection

### Tournament Commands
- **`/clear`** Clears the bot and resets the map selection process.
- **`/match`** Begin map selection by inputting two teams and initiate the coin toss.
    - The bot can load other tournaments besides those listed by this command. Simply input its name (e.g. "WW25") when using the command.
- **`/order`** Select either "BAN first, PICK second" or "BAN second, PICK first" to decide your team's ban order.
- **`/map_ban`** Select a map to ban from the remaining <ins>Standard</ins> map pool.
- **`/map_pick`** Select a map to pick from the remaining <ins>Standard</ins> map pool or **INVOKE WILDCARD**. Invoking the wildcard will randomly select a map from the remaining <ins>Wildcard</ins> map pool.
- **`/map_final`** Select either "Standard" or "Wildcard" to randomly select the final map from either of these map pools.

### PUG Commands
- **`/pug`** Opens the panel for the PUG queue.
- **`/join`** Join the PUG queue.
- **`/leave`** Leave the PUG queue.
- **`/remove`** Remove a player from the PUG queue.

---

## Hosting the Bot Yourself

To host the **ANP Match Manager** bot yourself, follow these steps:

1. **Configuration**
   - Create an `.env` file in the root of the project. This should include your Discord bot token (`DISCORD_TOKEN`) and your Discord guild ID (`DISCORD_GUILD`).

2. **Adding Your Own Tournaments**
   - To add your own tournament, place your tournament file in the `tournaments/` directory. Ensure that your file follows the same format as the existing files in that directory. The bot will automatically load the teams and maps from your newly added file.

3. **Define Your Tournament**:
   - **`MAP_POOL`** - Map names, versions etc.
   - **`TEAM_ROLES`** - Team names, clan tags, roles etc.
   - **`INFO`** - Tournament name, start date, map pools etc.

4. **Manage Permissons**
   - The bot requires the "Manage Nickname" permission to automatically update its nickname to reflect the number of players in the PUG queue.

5. **Configure Your Commands**
   - You may only want one of the two major functions of this bot. You can restrict usage of the bot's commands to channels, roles, and users.
   - Go to the following settings and edit the commands accordingly:
     - **Server Settings** -> **Apps** -> **Integrations** -> **Command Permissions**

6. **Run the Bot**

---

## Future Developments
- [x] Skip redundant commands for single-map-pool tournaments
- [x] Add support for queueing pick-up games
- [ ] Make bot format-agnostic and allow support for more types of tournaments (or even different games)
- [ ] Add views (buttons, dropdowns) to map selection