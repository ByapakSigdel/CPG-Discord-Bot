import discord
from discord.ext import commands
import aiohttp
import random

class ArtCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="art")
    async def random_art(self, ctx):
        """Show a random artwork"""
        url = "https://api.artic.edu/api/v1/artworks?page=1&limit=20"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()

        art = random.choice(data["data"])
        title = art.get("title", "Unknown")
        artist = art.get("artist_title", "Unknown Artist")
        image_id = art.get("image_id")

        embed = discord.Embed(title=title, description=artist, color=0xffa047)
        if image_id:
            embed.set_image(url=f"https://www.artic.edu/iiif/2/{image_id}/full/843,/0/default.jpg")

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ArtCog(bot))
