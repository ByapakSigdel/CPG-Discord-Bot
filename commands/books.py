import discord
from discord.ext import commands
import aiohttp
import random

class BookCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="book")
    async def suggest_book(self, ctx, topic: str = "fiction"):
        """Suggests a random book from OpenLibrary"""
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

        embed = discord.Embed(title=title, description=f"by {author}", color=0xffa047)
        embed.url = link
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(BookCog(bot))
