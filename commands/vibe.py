import discord
from discord.ext import commands
from discord import app_commands
import random

class VibeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.describe(mood="Pick a vibe: chill, nostalgic, creative")
    @commands.hybrid_command(name="vibe", description="Suggest media for a vibe")
    async def vibe(self, ctx, mood: str):
        """Suggest media for a vibe"""
        is_interaction = getattr(ctx, "interaction", None) is not None
        if is_interaction and not ctx.interaction.response.is_done():
            await ctx.defer()
        vibes = {
            "chill": ["🎥 Before Sunrise", "🎵 Lofi Beats", "📖 Norwegian Wood"],
            "nostalgic": ["🎥 Mid90s", "🎵 Somebody Else - The 1975", "📖 Eternal Sunshine"],
            "creative": ["🎥 Inception", "🎮 Life is Strange", "📖 Steal Like an Artist"]
        }

        if mood.lower() not in vibes:
            await ctx.send("Available vibes: chill, nostalgic, creative")
            return

        items = "\n".join(vibes[mood.lower()])
        embed = discord.Embed(title=f"🎧 Vibe: {mood}", description=items, color=0xffa047)
        
        if is_interaction:
            await ctx.interaction.followup.send(embed=embed)
        else:
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(VibeCog(bot))
