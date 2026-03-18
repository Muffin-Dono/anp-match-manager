# ANP Match Manager
ANP Match Manager is a Discord bot that helps teams select maps for their match. The number of maps you can ban or pick, as well as the order in which you do so, may vary depending on the tournament.

> [!IMPORTANT]
> The current version of the bot assumes that each team bans one map and picks one map for each matchup.

The map selection process is as follows:
1. First, the two opposing teams initiate a coin toss.
3. The team that wins the coin toss will determine which team will ban first in the banning phase.
4. For the banning phase, each team bans one map.
5. For the picking phase, each team picks one map (but team order is reversed for this phase!).
6. Finally, the third map is randomly selected by the bot.

---

## Useful commands
- `/help` Displays list of available commands.
- `/clear` Clears the bot and resets the map selection process.
- `/match` Begin map selection by inputting two teams and initiate the coin toss.
    - The bot can load other tournaments besides those listed by this command. Simply input its name (e.g. "WW25") when using the command.
- `/order` Select either "BAN first, PICK second" or "BAN second, PICK first" to decide your team's ban order.
- `/map_ban` Select a map to ban from the remaining <ins>Standard</ins> map pool.
- `/map_pick` Select a map to pick from the remaining <ins>Standard</ins> map pool or **INVOKE WILDCARD**. Invoking the wildcard will randomly select a map from the remaining <ins>Wildcard</ins> map pool.
- `/map_final` Select either "Standard" or "Wildcard" to randomly select the final map from either of these map pools.

---

## Hosting the Bot Yourself

To host the **ANP Match Manager** bot yourself, follow these steps:

1. **Configuration**
   - Create an `.env` file in the root of the project. This should include your Discord bot token (`DISCORD_TOKEN`) and your Discord guild ID (`DISCORD_GUILD`).

2. **Adding Your Own Tournaments**
   - To add your own tournament, place your tournament file in the `tournaments/` directory. Ensure that your file follows the same format as the existing files in that directory. The bot will automatically load the teams and maps from your newly added file.

3. **Run the Bot**

---

## Future Developments
- [ ] Replace nested dictionaries with classes
- [ ] Dynamic ban/pick format for different tournaments
- [ ] Add views (buttons, dropdowns)

### Bikeshedding
- [ ] Button(s) for callout maps?
- [ ] Images for embed - map screenshots or something more broad?
- [ ] Allow teams to schedule a date and time for their matchup?
    - Must introduce feature to edit datetimes if teams need to reschedule
- [ ] Implement new step-process to arrange scrims as well?
    - User states their team is looking to scrim (/scrim) -> assign team parameter + optional datetime parameter? Separate active requests by role_id?
    - Another user accepts the request (/accept),
    - If no time was proposed, one of the users can propose a time (/time)
