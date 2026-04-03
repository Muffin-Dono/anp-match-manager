import asyncio
import logging
import os
from logging.handlers import TimedRotatingFileHandler

import discord
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables including discord token and server ID(s)
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("DISCORD_GUILD"))

# Log errors/debug info
try:
    os.mkdir("logs")
except OSError:
    pass

handler = TimedRotatingFileHandler(
    "logs/discord.log", when="midnight", interval=1, backupCount=3, encoding="utf-8"
)

handler.suffix = "%Y-%m-%d"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    handlers=[handler, logging.StreamHandler()]
)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class MatchManager(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
    
    async def reset_nickname(self):
        await self.wait_until_ready()
        
        for guild in self.guilds:
            me = guild.me
            await me.edit(nick=None)

    async def setup_hook(self):
        for filename in os.listdir("./cogs"):
            if (
                filename.endswith(".py")
                and not filename.endswith("dev.py")
                and filename != "__init__.py"
            ):
                await self.load_extension(f"cogs.{filename[:-3]}")
                print(f"Loaded cog: {filename}")
        
        asyncio.create_task(self.reset_nickname())
        
        # guild = discord.Object(id=GUILD_ID)
        
        # # Clear command tree
        # self.tree.clear_commands(guild=guild)
        
        # Global sync
        synced = await self.tree.sync()
        print(f"Synced {len(synced)} commands to guild {GUILD_ID}")

bot = MatchManager()
bot.run(TOKEN)