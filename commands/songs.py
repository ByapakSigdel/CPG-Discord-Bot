import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import random
import os

class SongCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lastfm_api = os.getenv("LASTFM_API_KEY")

    @app_commands.describe(tag="Mood/genre tag, e.g., chill, rock, synth")
    @commands.hybrid_command(name="song", description="Suggest a random song from Last.fm by tag")
    async def suggest_song(self, ctx, *, tag: str = "chill"):
        """Suggest a random song using Last.fm"""
        is_interaction = getattr(ctx, "interaction", None) is not None
        if is_interaction and not ctx.interaction.response.is_done():
            await ctx.defer()
        
        # Fetch top tracks by tag
        url = f"https://ws.audioscrobbler.com/2.0/?method=tag.gettoptracks&tag={tag}&api_key={self.lastfm_api}&format=json&limit=10"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()

        tracks = data.get("tracks", {}).get("track", [])
        if not tracks:
            await ctx.send("❌ No songs found.")
            return

        song = random.choice(tracks)
        name = song.get("name")
        artist_name = song.get("artist", {}).get("name")
        song_url = song.get("url")
        
        # Try to get additional track info including album art
        track_info_url = f"https://ws.audioscrobbler.com/2.0/?method=track.getInfo&api_key={self.lastfm_api}&artist={artist_name}&track={name}&format=json"
        
        album_name = None
        album_art = None
        listeners = None
        playcount = None
        
        async with aiohttp.ClientSession() as session:
            async with session.get(track_info_url) as response:
                if response.status == 200:
                    track_data = await response.json()
                    track = track_data.get("track", {})
                    
                    # Get album info
                    album = track.get("album")
                    if album:
                        album_name = album.get("title")
                        images = album.get("image", [])
                        # Get the largest image (extralarge or mega)
                        for img in reversed(images):
                            if img.get("#text"):
                                album_art = img.get("#text")
                                break
                    
                    # Get stats
                    listeners = track.get("listeners")
                    playcount = track.get("playcount")

        # Create aesthetic embed with album art
        embed = discord.Embed(
            title=f"🎵 {name}",
            description=f"**Artist:** {artist_name}" + (f"\n**Album:** {album_name}" if album_name else ""),
            url=song_url,
            color=0xffa047  # Chiya-Pop orange
        )
        
        # Add album artwork
        if album_art:
            embed.set_thumbnail(url=album_art)
        
        # Add stats as fields
        if listeners or playcount:
            if listeners:
                embed.add_field(name="👥 Listeners", value=f"{int(listeners):,}", inline=True)
            if playcount:
                embed.add_field(name="▶️ Plays", value=f"{int(playcount):,}", inline=True)
        
        embed.add_field(name="🏷️ Tag", value=tag.capitalize(), inline=True)
        embed.set_footer(text="🎶 Powered by Last.fm", icon_url="https://www.last.fm/static/images/lastfm_avatar_twitter.52a5d69a85ac.png")
        
        if is_interaction:
            await ctx.interaction.followup.send(embed=embed)
        else:
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(SongCog(bot))
