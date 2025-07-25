# ANP Match Manager
ANP Match Manager is a Discord bot that helps teams select maps for their match. The number of maps you can ban or pick, as well as the order in which you do so, may vary depending on the tournament.

> [!IMPORTANT]
> The current version of the bot has been written specifically for Summer Skirmish 2025.

The map selection process is as follows:
1. First, the two opposing will initiate a coin toss.
3. The team that wins the coin toss will determine whether their team will ban a map first or second.
4. For the banning phase, each team bans one map.
5. For the picking phase, each team picks one map (but in reverse order to the banning phase!).
6. Finally, the third map is randomly selected by the bot.

## Useful commands
- `/help` Displays list of available commands.
- `/clear` Clears the bot and resets the map selection process.
- `/match` Begin map selection by inputting two teams and initiate the coin toss.
    - An optional parameter allows the user to change the map pool, otherwise it will default to the most recent tournament.
- `/order` Select either "First" or "Second" to decide your team's ban order.
- `/map_ban` Select a map to ban from the remaining <ins>Standard</ins> map pool.
- `/map_pick` Select a map to pick from the remaining <ins>Standard</ins> map pool or **INVOKE WILDCARD**. Invoking the wildcard will randomly select a map from the remaining <ins>Wildcard</ins> map pool.
- `/map_final` Select either "Standard" or "Wildcard" to randomly select the final map from either of these map pools.

## Future Developments
- [ ] Allow easy access to clan tags and team names without clan tag (Check against role IDs instead of string?)
- [ ] Replace nested dictionaries with classes
- [ ] Allow teams to schedule a datetime for their matchup
    - May need to introduce feature to edit times if teams change their minds
- [ ] Repair functionality for mirror matches
- [ ] Images for embed - team logos or something more broad?
- [ ] Implement new step-process to arrange scrims as well?
    - User says their team is looking to scrim (/scrim) -> assign team parameter + optional datetime parameter? Separate active requests by role_id?
    - Another user accepts the request (/accept), 
    - If no time was proposed, one of the users can propose a time (/time)