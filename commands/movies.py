# commands/movies.py
import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import os
import random

class MovieCog(commands.Cog):
    """Movie recommendations using TMDB API."""
    def __init__(self, bot):
        self.bot = bot
        self.tmdb_api = os.getenv("TMDB_API_KEY")

        # Common TMDB movie genre name -> ID mapping
        # https://developer.themoviedb.org/reference/genre-movie-list
        self.genre_map = {
            "action": 28,
            "adventure": 12,
            "animation": 16,
            "comedy": 35,
            "crime": 80,
            "documentary": 99,
            "drama": 18,
            "family": 10751,
            "fantasy": 14,
            "history": 36,
            "horror": 27,
            "music": 10402,
            "mystery": 9648,
            "romance": 10749,
            "science fiction": 878,
            "sci-fi": 878,
            "tv movie": 10770,
            "thriller": 53,
            "war": 10752,
            "western": 37,
        }

    @app_commands.describe(genre="TMDB genre ID or name (optional)")
    @commands.hybrid_command(name="movie", description="Suggest a random popular movie, optionally by genre")
    @app_commands.describe(genre="Genre name or ID (e.g., action, comedy, 18). Comma-separated supported.")
    async def movie(self, ctx, *, genre: str = None):
        """Suggest a random popular movie. Accepts a TMDB genre name or ID (comma-separated)."""
        is_interaction = getattr(ctx, "interaction", None) is not None
        if is_interaction and not ctx.interaction.response.is_done():
            # Avoid 3s timeout for slash invocations
            await ctx.defer()
        if not self.tmdb_api:
            if is_interaction:
                await ctx.interaction.followup.send(
                    "❌ TMDB API key is missing. Set TMDB_API_KEY in your .env to enable /movie.")
            else:
                await ctx.send(
                    "❌ TMDB API key is missing. Set TMDB_API_KEY in your .env to enable /movie.")
            return

        url = "https://api.themoviedb.org/3/discover/movie"

        # Map provided genre names to TMDB IDs; allow IDs directly and comma-separated input
        with_genres = None
        if genre:
            raw_parts = [g.strip() for g in genre.split(",") if g.strip()]
            mapped_ids = []
            for g in raw_parts:
                if g.isdigit():
                    mapped_ids.append(g)
                else:
                    gid = self.genre_map.get(g.lower())
                    if gid:
                        mapped_ids.append(str(gid))
            if mapped_ids:
                with_genres = ",".join(mapped_ids)

        params = {
            "api_key": self.tmdb_api,
            "sort_by": "popularity.desc",
            "include_adult": "false",
            "include_video": "false",
            "language": "en-US",
            "page": 1,
        }
        if with_genres:
            params["with_genres"] = with_genres

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    if is_interaction:
                        await ctx.interaction.followup.send(f"❌ TMDB request failed ({response.status}).")
                    else:
                        await ctx.send(f"❌ TMDB request failed ({response.status}).")
                    return
                data = await response.json()

        results = data.get("results", [])
        if not results:
            if is_interaction:
                if genre and not with_genres:
                    # User gave names we couldn't map
                    valid = ", ".join(sorted(set(self.genre_map.keys())))
                    await ctx.interaction.followup.send(
                        "❌ No movies found. If you used names, try one of: " + valid)
                else:
                    await ctx.interaction.followup.send("❌ No movies found for that genre.")
            else:
                if genre and not with_genres:
                    # User gave names we couldn't map
                    valid = ", ".join(sorted(set(self.genre_map.keys())))
                    await ctx.send(
                        "❌ No movies found. If you used names, try one of: " + valid)
                else:
                    await ctx.send("❌ No movies found for that genre.")
            return

        movie = random.choice(results)
        title = movie.get("title") or movie.get("name") or "Unknown Title"
        overview = movie.get("overview") or "No description available"
        poster_path = movie.get("poster_path")
        release_date = movie.get("release_date", "Unknown")
        rating = movie.get("vote_average", 0)
        popularity = movie.get("popularity", 0)
        
        # Create aesthetic embed with movie poster
        embed = discord.Embed(
            title=f"🎬 {title}",
            description=overview[:500] + ("..." if len(overview) > 500 else ""),
            color=0xffa047  # Chiya-Pop orange
        )
        
        # Add movie poster image
        if poster_path:
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
            embed.set_image(url=poster_url)
        
        # Add additional info as fields
        embed.add_field(name="📅 Release Date", value=release_date if release_date else "N/A", inline=True)
        embed.add_field(name="⭐ Rating", value=f"{rating}/10" if rating else "N/A", inline=True)
        embed.add_field(name="📊 Popularity", value=f"{popularity:.0f}", inline=True)
        
        embed.set_footer(text="🎥 Powered by TMDB", icon_url="https://www.themoviedb.org/assets/2/v4/logos/v2/blue_square_2-d537fb228cf3ded904ef09b136fe3fec72548ebc1fea3fbbd1ad9e36364db38b.svg")
        
        if is_interaction:
            await ctx.interaction.followup.send(embed=embed)
        else:
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(MovieCog(bot))
