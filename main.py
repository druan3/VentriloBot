import asyncio
import discord
import os
import spotipy
import yt_dlp

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
async def play(ctx, *, query: str):
    """Plays a song from Spotify or text by streaming from  YouTube."""
    voice = ctx.author.voice
    if not voice or not voice.channel:
        await ctx.send("You must be in a voice channel.")
        return
    
    # Convert Spotify URL to search query
    if "open.spotify.com" in query:
        try:
            track_id = query.split("/")[-1].split("?")[0]
            track = spotify_client.track(track_id)
            query = f"{track['name']} {track['artists'][0]['name']}"
        except Exception:
            await ctx.send("Could not parse Spotify track.")
            return
    
    # Connect to voice if not already connected
    if ctx.voice_client is None:
        vc = await voice.channel.connect()
    else:
        vc = ctx.voice_client

    await ctx.send(f"Searching for `{query}`")

    ytdlp_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'ytsearch1',
    }

    with yt_dlp.YoutubeDL(ytdlp_opts) as ydl:
        try:
            info = ydl.extract_info(query, download=False)
            if 'entries' in info:
                info = info['entries'][0] # First result from ytsearch
            url = info['url']
            title = info['title']
        except Exception as e:
            print(f"yt-dlp error: {e}")
            await ctx.send("Failed to get audio from YouTube.")
            return
        
    await ctx.send(f"Now playing: **{title}**")
    print(f"Streaming from: {url}")

    def after_play(error):
        if error:
            print(f"Playback error: {error}")
        else:
            print("Playback finished successfully.")

    vc.stop()
    vc.play(discord.FFmpegPCMAudio(url), after=after_play)

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

@bot.command()
async def stop(ctx):
    """Stops playback and disconnects from the voice channel."""
    voice_client = ctx.voice_client

    if voice_client is None:
        await ctx.send("I'm not connected to a voice channel.")

    if voice_client.is_playing():
        voice_client.stop()

    await voice_client.disconnect()
    await ctx.send("Playback stopped and disconnected.")

# Run the bot
bot.run(TOKEN)