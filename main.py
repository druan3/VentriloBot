import discord
import os
import spotipy

from discord.ext import commands
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials

# Load tokens from .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Set up bot
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Set up Spotify
spotify_client = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
))

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

@bot.command()
async def ping(ctx):
    await ctx.send("pong!")

@bot.command()
async def spotify(ctx, *, query: str):
    """Search Spotify for a track and return the top result."""
    try:
        results = spotify_client.search(q=query, type='track', limit=1)
        tracks = results.get('tracks', {}).get('items', [])

        if not tracks:
            await ctx.send("No tracks found.")
            return
        
        track = tracks[0]
        name = track['name']
        artist = track['artists'][0]['name']
        url = track['external_urls']['spotify']

        await ctx.send(f"{name} by {artist}\n{url}")

    except Exception as e:
        print(f"Error during Spotify search: {e}")
        await ctx.send("There was an error processing your request.")

# Run the bot
bot.run(TOKEN)