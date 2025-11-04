import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import random

class BookCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.describe(topic="Subject to explore, e.g., fiction, romance, history")
    @commands.hybrid_command(name="book", description="Suggest a random book from OpenLibrary")
    async def suggest_book(self, ctx, topic: str = "fiction"):
        """Suggests a random book from OpenLibrary"""
        is_interaction = getattr(ctx, "interaction", None) is not None
        if is_interaction and not ctx.interaction.response.is_done():
            await ctx.defer()
        url = f"https://openlibrary.org/subjects/{topic}.json?limit=5"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()

        if "works" not in data or not data["works"]:
            await ctx.send(f"❌ No books found for '{topic}'.")
            return

        book = random.choice(data["works"])
        title = book.get("title", "Unknown")
        author = book["authors"][0]["name"] if book.get("authors") else "Unknown"
        link = f"https://openlibrary.org{book.get('key', '')}"
        first_publish_year = book.get("first_publish_year", "Unknown")
        cover_id = book.get("cover_id")
        
        # Create aesthetic embed with book cover
        embed = discord.Embed(
            title=f"📚 {title}",
            description=f"**Author:** {author}\n**First Published:** {first_publish_year}",
            url=link,
            color=0xffa047  # Chiya-Pop orange
        )
        
        # Add book cover if available
        if cover_id:
            cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
            embed.set_image(url=cover_url)
        
        # Add subject tags if available
        if book.get("subject"):
            subjects = ", ".join(book["subject"][:3])  # First 3 subjects
            embed.add_field(name="📖 Topics", value=subjects, inline=False)
        
        embed.set_footer(text="📚 Open Library", icon_url="https://openlibrary.org/static/images/openlibrary-logo-tighter.svg")
        
        if is_interaction:
            await ctx.interaction.followup.send(embed=embed)
        else:
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(BookCog(bot))
