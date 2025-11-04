# commands/movies.py
from discord.ext import commands
import aiohttp

class MovieCog(commands.Cog):
    """Movie recommendations using TMDB API."""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="movie")
    async def movie(self, ctx, *, genre: str = None):
        """Suggests a random movie based on genre"""
        url = "https://api.themoviedb.org/3/discover/movie"
        params = {
            "api_key": "YOUR_TMDB_API_KEY",  # Optional if you use TMDB
            "sort_by": "popularity.desc"
        }
        if genre:
            params["with_genres"] = genre

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()
                if "results" in data and len(data["results"]) > 0:
                    movie = data["results"][0]
                    await ctx.send(f"🎬 **{movie['title']}**\n{movie.get('overview', 'No description')}")
                else:
                    await ctx.send("No movies found for that genre.")

async def setup(bot):
    await bot.add_cog(MovieCog(bot))
