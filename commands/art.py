import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import random

class ArtCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="art", description="Show a random artwork")
    async def random_art(self, ctx):
        """Show a random artwork"""
        is_interaction = getattr(ctx, "interaction", None) is not None
        if is_interaction and not ctx.interaction.response.is_done():
            await ctx.defer()
        
        async with aiohttp.ClientSession() as session:
            # Get artworks from the API with image info included
            url = "https://api.artic.edu/api/v1/artworks?page=1&limit=100&fields=id,title,artist_title,image_id,date_display,place_of_origin,artwork_type_title"
            async with session.get(url) as response:
                data = await response.json()
            
            # Get the IIIF base URL from config
            config = data.get("config", {})
            iiif_url = config.get("iiif_url", "https://www.artic.edu/iiif/2")
            
            # Filter artworks that have valid image_id
            artworks = data.get("data", [])
            artworks_with_images = [art for art in artworks if art.get("image_id")]
            
            if not artworks_with_images:
                if is_interaction:
                    await ctx.interaction.followup.send("❌ No artworks with images found.")
                else:
                    await ctx.send("❌ No artworks with images found.")
                return
            
            # Select a random artwork
            art = random.choice(artworks_with_images)

        title = art.get("title", "Unknown")
        artist = art.get("artist_title", "Unknown Artist")
        image_id = art.get("image_id")
        date = art.get("date_display", "Unknown date")
        place = art.get("place_of_origin", "Unknown origin")
        art_type = art.get("artwork_type_title", "Artwork")

        # Create aesthetic embed with Chiya-Pop colors
        embed = discord.Embed(
            title=f"🎨 {title}"[:256],  # Discord title limit
            description=f"**Artist:** {artist}\n**Date:** {date}\n**Origin:** {place}\n**Type:** {art_type}",
            color=0xffa047  # Chiya-Pop orange
        )
        
        # Set the artwork image using the correct IIIF URL format
        if image_id:
            # Use the full URL format: {iiif_url}/{image_id}/full/843,/0/default.jpg
            image_url = f"{iiif_url}/{image_id}/full/843,/0/default.jpg"
            embed.set_image(url=image_url)
        
        embed.set_footer(text="🖼️ Art Institute of Chicago")

        if is_interaction:
            await ctx.interaction.followup.send(embed=embed)
        else:
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ArtCog(bot))
