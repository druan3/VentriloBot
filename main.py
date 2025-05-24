import discord
import os

from discord.ext import commands
from dotenv import load_dotenv

# Load tokens from .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Setup bot
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

@bot.command()
async def ping(ctx):
    await ctx.send("pong!")

bot.run(TOKEN)