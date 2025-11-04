import discord
from discord.ext import commands
import aiohttp
import random
import os

class SongCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lastfm_api = os.getenv("LASTFM_API_KEY")

    @commands.command(name="song")
    async def suggest_song(self, ctx, *, tag: str = "chill"):
        """Suggest a random song using Last.fm"""
        url = f"https://ws.audioscrobbler.com/2.0/?method=tag.gettoptracks&tag={tag}&api_key={self.lastfm_api}&format=json&limit=5"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()

        tracks = data.get("tracks", {}).get("track", [])
        if not tracks:
            await ctx.send("❌ No songs found.")
            return

        song = random.choice(tracks)
        name = song.get("name")
        artist = song.get("artist", {}).get("name")
        url = song.get("url")

        embed = discord.Embed(title=name, description=f"by {artist}", url=url, color=0xffa047)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(SongCog(bot))
