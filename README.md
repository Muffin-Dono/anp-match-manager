# ANP Match Manager
ANP Match Manager is a Discord bot that helps teams select maps for their match.

The map selection process is as follows:
1. First, input the two teams playing against each other.
2. This will initiate the coin toss and a winner is announced promptly.
3. Then, the team that wins the coin toss will determine whether they will ban a map first or second.
4. After both teams have each banned a map, the banning phase is over.
5. For the picking phase, each team picks one map, but in reverse order to the banning phase.
6. Finally, the third and final map is randomly selected by the bot from the remaining pool. 

## Useful commands
- `/match` Input two teams to initiate the coin toss. 
    - An optional parameter allows the user to change the map pool, otherwise it will default to the most recent tournament.
- `/order` Select either "First" or "Second" to decide your team's ban order.